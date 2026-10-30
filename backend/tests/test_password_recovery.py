"""Admin-assisted recovery only. Temporary accounts; no email/network."""
import sys
import uuid
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from app.core.database import SessionLocal, q_one
from app.core.security import create_token, hash_password, verify_password
from app.core.responses import ApiError
from app.main import app
from scripts.recover_admin import recover
client = TestClient(app)


@pytest.fixture
def users():
    rows = {}
    with SessionLocal() as db:
        for role in ('admin', 'teacher', 'student'):
            email = 'assisted-recovery-' + uuid.uuid4().hex + '@example.test'
            db.execute(text("INSERT INTO users (fullname,email,password,role,is_active) VALUES ('Assisted Recovery Test',:email,:pw,:role,1)"),
                       {"email": email, "pw": hash_password('OldPass123!'), "role": role})
            db.commit()
            rows[role] = q_one(db, 'SELECT * FROM users WHERE email=:email', email=email)
    try:
        yield rows
    finally:
        with SessionLocal() as db:
            for row in rows.values(): db.execute(text('DELETE FROM users WHERE id=:id'), {"id": row['id']})
            db.commit()


@pytest.mark.parametrize('endpoint', ['forgot-password', 'reset-password', 'reset-password/validate'])
def test_public_email_reset_disabled(endpoint):
    assert client.post('/api/auth/' + endpoint, json={"email": 'any@example.test', "token": 'old-token', "password": 'Password123!', "confirm_password": 'Password123!'}).status_code == 404


@pytest.mark.parametrize('role', ['teacher', 'student'])
def test_admin_assisted_reset_revokes_sessions_and_preserves_profile(users, role):
    row = users[role]
    old = create_token(row)
    admin = {"Authorization": 'Bearer ' + create_token(users['admin'])}
    response = client.put('/api/users', headers=admin, json={"id": row['id'], "fullname": row['fullname'], "email": row['email'], "role": role, "password": 'Assisted123!'})
    assert response.status_code == 200
    assert client.get('/api/auth/me', headers={"Authorization": 'Bearer ' + old}).status_code == 401
    assert client.post('/api/auth/login', json={"email": row['email'], "password": 'OldPass123!'}).status_code == 401
    assert client.post('/api/auth/login', json={"email": row['email'], "password": 'Assisted123!'}).status_code == 200
    with SessionLocal() as db:
        updated = q_one(db, 'SELECT * FROM users WHERE id=:id', id=row['id'])
        assert verify_password('Assisted123!', updated['password'])
        assert all(updated[k] == row[k] for k in ('id', 'fullname', 'email', 'role', 'is_active', 'bio', 'avatar'))
    for forbidden_role in ('teacher', 'student'):
        assert client.put('/api/users', headers={"Authorization": 'Bearer ' + create_token(users[forbidden_role])},
                          json={"id": row['id'], "fullname": row['fullname'], "email": row['email'], "role": role, "password": 'BadReset123!'}).status_code in (401, 403)


def test_admin_uses_server_recovery(users):
    row = users['admin']
    old = create_token(row)
    assert client.put('/api/users', headers={"Authorization": 'Bearer ' + old}, json={"id": row['id'], "fullname": row['fullname'], "email": row['email'], "role": 'admin', "password": 'AdminNew123!'}).status_code == 403
    recover(row['email'], 'AdminNew123!', 'AdminNew123!')
    assert client.get('/api/auth/me', headers={"Authorization": 'Bearer ' + old}).status_code == 401
    assert client.post('/api/auth/login', json={"email": row['email'], "password": 'AdminNew123!'}).json()['user']['role'] == 'admin'
    with pytest.raises(ApiError): recover(users['student']['email'], 'NewPass123!', 'NewPass123!')
