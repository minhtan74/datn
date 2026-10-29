"""Streaming quiz responses: authorization, worker session and partial/error delivery."""
import json

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.routers import ai


@pytest.fixture
def stream_client(monkeypatch):
    engine = create_engine('sqlite://', connect_args={'check_same_thread': False}, poolclass=StaticPool)
    with engine.begin() as conn:
        conn.execute(text('CREATE TABLE courses (id INT, teacher_id INT)'))
        conn.execute(text('INSERT INTO courses VALUES (7,2),(8,3)'))
    factory = sessionmaker(bind=engine)

    def db():
        with Session(engine) as session:
            yield session

    actor = {'id': 2, 'role': 'teacher'}
    previous = dict(app.dependency_overrides)
    app.dependency_overrides[get_db] = db
    app.dependency_overrides[get_current_user] = lambda: actor
    monkeypatch.setattr(ai, 'SessionLocal', factory)
    try:
        yield TestClient(app), actor
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(previous)
        engine.dispose()


def test_stream_sends_partial_then_verified_result(stream_client, monkeypatch):
    client, _ = stream_client

    def generate(db, *, on_progress, **kwargs):
        assert db.execute(text('SELECT COUNT(*) FROM courses')).scalar() == 2
        on_progress({'type': 'batch', 'difficulty': 'easy', 'questions': [{'question': 'Câu 1'}]})
        return {'questions': [{'question': 'Câu 1', 'verified': 'B'}], 'meta': {}}

    monkeypatch.setattr(ai.quiz_generator, 'generate', generate)
    response = client.post('/api/ai/generate-quiz/stream', json={'course_id': 7})
    events = [json.loads(line) for line in response.text.splitlines()]
    assert response.status_code == 200
    assert response.headers['content-type'].startswith('application/x-ndjson')
    assert [event['type'] for event in events] == ['batch', 'complete']
    assert 'verified' not in events[0]['questions'][0]
    assert events[-1]['data']['questions'][0]['verified'] == 'B'


def test_stream_delivers_generation_error(stream_client, monkeypatch):
    client, _ = stream_client

    def generate(db, *, on_progress, **kwargs):
        on_progress({'type': 'status', 'message': 'Đang đọc tài liệu'})
        raise ai.QuizGenError('Chưa có tài liệu.')

    monkeypatch.setattr(ai.quiz_generator, 'generate', generate)
    response = client.post('/api/ai/generate-quiz/stream', json={'course_id': 7})
    events = [json.loads(line) for line in response.text.splitlines()]
    assert events[-1] == {'type': 'error', 'status': 422, 'message': 'Chưa có tài liệu.'}


def test_stream_checks_role_and_course_before_starting_worker(stream_client, monkeypatch):
    client, actor = stream_client
    calls = []
    monkeypatch.setattr(ai.quiz_generator, 'generate', lambda *a, **kw: calls.append(True))
    assert client.post('/api/ai/generate-quiz/stream', json={'course_id': 8}).status_code == 403
    actor['role'] = 'student'
    assert client.post('/api/ai/generate-quiz/stream', json={'course_id': 7}).status_code == 403
    assert calls == []
