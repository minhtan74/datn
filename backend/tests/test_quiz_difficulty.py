"""Kiểm tra quy tắc sinh quiz, không kết nối DB hay gọi LLM thật."""
import json
import threading

import pytest

from app.ai import quiz_generator as gen


def test_offline_does_not_generate_higher_levels():
    for level in ("medium", "hard"):
        assert gen._generate_batch("", "", n=2, difficulty=level, seen=set(), provider="stub") == []


@pytest.mark.parametrize('candidate,expected', [(55,55),(999,None)])
def test_generated_lesson_ids_are_limited_to_the_requested_chapter(monkeypatch,candidate,expected):
    from app.services import knowledge
    monkeypatch.setattr(gen,'_build_chapter_context',lambda *args:('Nội dung','Chương 1',[],[]))
    monkeypatch.setattr(gen,'_existing_questions',lambda *args:set())
    monkeypatch.setattr(gen.model_manager,'active_provider',lambda:'stub')
    monkeypatch.setattr(knowledge,'outline',lambda *args:dict(chapters=[dict(id=19,chapter_name='Chương 1')],
        lessons=[dict(id=55,title='Bài 1',chapter_id=19),dict(id=999,title='Bài khác',chapter_id=20)]))
    monkeypatch.setattr(gen,'_generate_batch',lambda *args,**kwargs:[dict(question='Câu mới',difficulty='easy',
        topic='Chủ đề riêng',correct_answer='A',knowledge_lesson_id=candidate)])
    question=gen.generate(object(),course_id=7,chapter_id=19,lesson_id=None,n=1,difficulty='easy')['questions'][0]
    assert question['knowledge_chapter_id']==19
    assert question['knowledge_lesson_id']==expected


def test_offline_does_not_fill_missing_distractors(monkeypatch):
    sentence = "Python là một ngôn ngữ lập trình phổ biến trong học tập."
    monkeypatch.setattr(gen, "_sentences", lambda _: [sentence])
    monkeypatch.setattr(gen, "_key_term", lambda _: "Python")
    assert gen._heuristic(sentence, n=1, difficulty="easy", topic_hint="Python", seen=set()) == []


def test_duplicate_options_are_rejected():
    question = {"question": "Chọn đáp án", "options": {"A": "Python", "B": " python ", "C": "Java", "D": "C"}, "correct_answer": "A"}
    assert gen._clean_questions({"questions": [question]}, n=1, difficulty="easy", topic_hint="", seen=set()) == []


def test_difficulty_review_flags_mismatch_without_changing_requested_label(monkeypatch):
    monkeypatch.setattr(gen.model_manager, "generate", lambda *args, **kwargs:
        '{"answers":[{"i":0,"answer":"A","difficulty":"easy","difficulty_reason":"Chỉ nhớ định nghĩa"}]}')
    question = {"question": "Khái niệm là gì?", "options": dict(zip("ABCD", ["a", "b", "c", "d"])), "correct_answer": "A", "difficulty": "hard"}
    gen._verify("Tài liệu", [question])
    assert question["verified"] == "A"
    assert question["difficulty"] == "hard"
    assert question["difficulty_review"]["matches_requested"] is False


@pytest.mark.parametrize('verification_available', [True, False])
def test_mixed_quiz_verifies_all_levels_in_one_call(monkeypatch, verification_available):
    monkeypatch.setattr(gen, '_build_chapter_context', lambda *args: ('Tài liệu', 'Chương 1', [], []))
    monkeypatch.setattr(gen, '_existing_questions', lambda *args: set())
    monkeypatch.setattr(gen.model_manager, 'active_provider', lambda: 'gemini')
    calls = []

    def generate(system, user, **kwargs):
        calls.append(system)
        if system == gen._VERIFY_SYSTEM:
            if not verification_available:
                return '[Lỗi gọi LLM: HTTP 503 — lỗi dịch vụ]'
            return json.dumps({'answers': [
                {'i': i, 'answer': 'B', 'difficulty': level}
                for i, level in enumerate(('easy', 'medium', 'hard'))
            ]})
        return json.dumps({'questions': [{
            'question': f'Câu {level}', 'options': dict(zip('ABCD', ('a', 'b', 'c', 'd'))),
            'correct_answer': 'B', 'difficulty': level,
        } for level in ('easy', 'medium', 'hard')]})

    monkeypatch.setattr(gen.model_manager, 'generate', generate)
    result = gen.generate(None, course_id=7, chapter_id=19, lesson_id=None, n=3,
                          difficulty='medium', mix={'easy': 1, 'medium': 1, 'hard': 1})
    assert len(calls) == 2  # One mixed generation and one shared verification.
    assert calls[-1] == gen._VERIFY_SYSTEM
    assert [q['difficulty'] for q in result['questions']] == ['easy', 'medium', 'hard']
    if verification_available:
        assert all(q['verified'] == 'B' for q in result['questions'])
        assert result['meta']['verification']['verified'] == 3
        assert result['meta']['warnings'] == []
    else:
        assert len(result['questions']) == 3  # Keep the draft when verification is unavailable.
        assert result['meta']['verification']['unverified'] == 3
        assert any('Chưa tự kiểm tra' in message for message in result['meta']['warnings'])


def test_parallel_generation_deduplicates_and_reports_before_verification(monkeypatch):
    monkeypatch.setattr(gen, '_build_chapter_context', lambda *args: ('Tài liệu', 'Chương', [], []))
    monkeypatch.setattr(gen, '_existing_questions', lambda *args: {'câu cũ'})
    monkeypatch.setattr(gen.model_manager, 'active_provider', lambda: 'gemini')
    barrier = threading.Barrier(2, timeout=3)
    lock = threading.Lock()
    activity = {'active': 0, 'peak': 0, 'started': 0}
    events = []

    def batch(*args, difficulty, **kwargs):
        with lock:
            activity['active'] += 1
            activity['started'] += 1
            index = activity['started']
            activity['peak'] = max(activity['peak'], activity['active'])
        try:
            if index <= 2:
                barrier.wait()  # Fails if both batches cannot run at the same time.
            return [{'question': content, 'difficulty': difficulty, 'correct_answer': 'B'}
                    for content in ('Câu cũ', 'Câu trùng giữa các mức', f'Câu {difficulty}')]
        finally:
            with lock:
                activity['active'] -= 1

    def verify(context, questions):
        assert len([e for e in events if e['type'] == 'batch']) == 3
        assert all('verified' not in q for e in events if e['type'] == 'batch' for q in e['questions'])
        for q in questions:
            q['verified'] = 'B'

    monkeypatch.setattr(gen, '_generate_batch', batch)
    monkeypatch.setattr(gen, '_verify', verify)
    result = gen.generate(None, course_id=7, chapter_id=19, lesson_id=None, n=15, difficulty='medium',
                          mix={'easy': 5, 'medium': 5, 'hard': 5}, on_progress=events.append)
    assert activity['peak'] == 2
    assert len(result['questions']) == 4
    assert len({q['question'] for q in result['questions']}) == 4
    assert all(q['question'] != 'Câu cũ' for q in result['questions'])
    assert sum(result['meta']['distribution'].values()) == 4


def test_mixed_batch_keeps_labels_and_enforces_each_requested_count(monkeypatch):
    raw = [{'question': f'Câu {i}', 'options': dict(zip('ABCD', ('a', 'b', 'c', 'd'))),
            'correct_answer': 'B', 'difficulty': level}
           for i, level in enumerate(('easy', 'easy', 'easy', 'hard', 'hard', None))]
    monkeypatch.setattr(gen.model_manager, 'generate', lambda *a, **kw: json.dumps({'questions': raw}))
    questions = gen._generate_batch('Tài liệu', 'Chương', n=3, difficulty='medium', seen=set(),
                                    provider='gemini', mix={'easy': 1, 'hard': 2})
    assert [q['difficulty'] for q in questions] == ['easy', 'hard', 'hard']
