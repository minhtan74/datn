"""Content evidence and retake rules on an isolated in-memory database."""
import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from app.ai import recommendation as rec
from app.services import analytics_service as an
from app.services.topic_catalog import resolve_topic
from app.services import study_progress
from app.core.responses import ApiError
from app.routers import topics as topic_routes


@pytest.fixture
def db():
    engine = create_engine('sqlite://')
    with Session(engine) as session:
        for ddl in [
            'CREATE TABLE courses (id INT, title TEXT)',
            'CREATE TABLE enrollments (id INT, user_id INT, course_id INT)',
            'CREATE TABLE quizzes (id INT, title TEXT, course_id INT, lesson_id INT, review_lesson_id INT, chapter_id INT, grading_method TEXT, max_attempts INT, duration INT)',
            'CREATE TABLE results (id INT, user_id INT, quiz_id INT, score INT, total INT, passing_score INT, submit_time TEXT)',
            'CREATE TABLE questions (id INT, quiz_id INT, topic TEXT, topic_id INT)',
            'CREATE TABLE result_answers (result_id INT, question_id INT, is_correct INT, topic_id INT, topic_name TEXT, classification_version INT DEFAULT 0, knowledge_chapter_id INT, knowledge_lesson_id INT, knowledge_chapter_name TEXT, knowledge_lesson_name TEXT, knowledge_version INT DEFAULT 0)',
            'CREATE TABLE quiz_attempts (id INT, user_id INT, quiz_id INT, result_id INT, finished_ts INT, started_ts INT)',
            'CREATE TABLE course_topics (id INTEGER PRIMARY KEY, course_id INT, name TEXT, normalized_name TEXT, lesson_id INT, practice_quiz_id INT, confirmed INT DEFAULT 0)',
            'CREATE TABLE study_checkpoints (id INTEGER PRIMARY KEY, user_id INT, topic_id INT, baseline TEXT, baseline_result_id INT, started_at TEXT)',
            'CREATE TABLE knowledge_study_checkpoints (id INTEGER PRIMARY KEY, user_id INT, course_id INT, unit_kind TEXT, unit_id INT, baseline TEXT, baseline_result_id INT, started_at TEXT)',
            'CREATE TABLE chapters (id INT, course_id INT, order_index INT)',
            'CREATE TABLE lessons (id INT, title TEXT, chapter_id INT, order_index INT)',
            'CREATE TABLE lesson_progress (id INT, lesson_id INT, user_id INT, is_completed INT, watched_sec INT)',
            "INSERT INTO courses VALUES (1,'HĐH')",
            'INSERT INTO enrollments VALUES (1,1,1)',
            'INSERT INTO chapters VALUES (1,1,1)',
            "INSERT INTO lessons VALUES (1,'Đồng bộ hóa',1,1)",
            "INSERT INTO quizzes VALUES (1,'Kiểm tra HĐH',1,1,NULL,NULL,'latest',3,NULL)",
        ]:
            session.execute(text(ddl))
        yield session
    engine.dispose()


def result(db, rid, score, total=10, passing=80):
    db.execute(text('INSERT INTO results (id,user_id,quiz_id,score,total,passing_score) VALUES (:id,1,1,:s,:t,:p)'), dict(id=rid,s=score,t=total,p=passing))


def test_no_results_is_not_average(db):
    r = rec.build(db, 1)
    assert r['level'] == 'Insufficient'
    assert r['based_on']['avg_quiz_score'] is None
    assert any(i['type'] == 'next_lesson' for i in r['items'])


def test_latest_content_is_independent_of_highest_official_grade(db):
    db.execute(text("UPDATE quizzes SET grading_method='highest'"))
    result(db, 1, 10)
    result(db, 2, 2)
    for qid in range(1,7):
        db.execute(text("INSERT INTO questions (id,quiz_id,topic) VALUES (:id,1,'Đồng bộ hóa')"),dict(id=qid))
        db.execute(text('INSERT INTO result_answers (result_id,question_id,is_correct) VALUES (1,:id,1)'),dict(id=qid))
        db.execute(text('INSERT INTO result_answers (result_id,question_id,is_correct) VALUES (2,:id,:ok)'),dict(id=qid,ok=int(qid<=2)))
    r = rec.build(db, 1)
    assert r['based_on']['avg_quiz_score'] == 100
    t = r['topics'][0]
    assert (t['correct'],t['answered'],t['status']) == (2,6,'Weak')
    item = next(i for i in r['items'] if i['type']=='review_topic')
    assert '2/6' in item['text'] and item['action_url']=='/lesson?id=1'


def test_topic_normalization_course_separation_and_distinct_evidence():
    rows = [dict(topic='  Đồng   bộ hóa ',course_id=1,course_title='HĐH',question_id=1,is_correct=0,lesson_id=None),
            dict(topic='ĐỒNG BỘ HÓA',course_id=1,course_title='HĐH',question_id=1,is_correct=0,lesson_id=None),
            dict(topic='Đồng bộ hóa',course_id=2,course_title='Khóa khác',question_id=2,is_correct=1,lesson_id=None),
            dict(topic='  ',course_id=1,course_title='HĐH',question_id=3,is_correct=0,lesson_id=None)]
    topics = an.summarize_topics(rows)
    assert len(topics)==2
    assert all(t['answered']==1 and t['status']=='Insufficient' for t in topics)


@pytest.mark.parametrize('method,expected', [('latest',40),('average',65),('highest',None),('first',None)])
def test_retake_uses_grading_policy(db,method,expected):
    db.execute(text('UPDATE quizzes SET grading_method=:m'),dict(m=method))
    result(db,1,9)
    result(db,2,4)
    r=rec._weak_quiz(db,1,None)
    assert (r['evaluated_score'] if r else None)==expected


def test_retake_above_70_but_below_passing_score(db):
    result(db,1,15,total=20,passing=80)
    r=rec._weak_quiz(db,1,None)
    assert r['evaluated_score']==75 and r['passed'] is False


def test_abandoned_attempt_uses_last_slot(db):
    db.execute(text('UPDATE quizzes SET max_attempts=2'))
    result(db,1,4)
    db.execute(text('INSERT INTO quiz_attempts VALUES (1,1,1,NULL,1,0)'))
    assert rec._weak_quiz(db,1,None) is None


def test_removed_enrollment_does_not_create_retake(db):
    result(db,1,4)
    db.execute(text('DELETE FROM enrollments'))
    assert rec._weak_quiz(db,1,None) is None


def test_ambiguous_lesson_mapping_does_not_guess():
    t=dict(course_id=1,topic='Đồng bộ hóa',lesson_ids=[1,2])
    lessons=[dict(id=1,course_id=1,title='Bài A'),dict(id=2,course_id=1,title='Bài B')]
    assert rec._topic_action(t,lessons)['action_url']=='/chapters?course_id=1'


def test_live_last_attempt_can_be_resumed(db):
    db.execute(text('UPDATE quizzes SET max_attempts=2'))
    result(db,1,4)
    db.execute(text('INSERT INTO quiz_attempts VALUES (1,1,1,NULL,NULL,0)'))
    assert rec._weak_quiz(db,1,None)['resume'] is True


def test_expired_last_attempt_cannot_be_recommended(db):
    db.execute(text('UPDATE quizzes SET max_attempts=2,duration=1'))
    result(db,1,4)
    db.execute(text('INSERT INTO quiz_attempts VALUES (1,1,1,NULL,NULL,0)'))
    assert rec._weak_quiz(db,1,None) is None


def test_unclassified_question_still_counts_in_official_score(db):
    result(db,1,8)
    db.execute(text("INSERT INTO questions (id,quiz_id,topic) VALUES (1,1,' ')"))
    db.execute(text('INSERT INTO result_answers (result_id,question_id,is_correct) VALUES (1,1,1)'))
    r=rec.build(db,1)
    assert r['level']=='Insufficient' and r['topics']==[]
    assert r['based_on']['unclassified_answers']==1
    assert r['based_on']['avg_quiz_score']==80


def test_unenrolled_content_is_excluded(db):
    result(db,1,4)
    db.execute(text("INSERT INTO questions (id,quiz_id,topic) VALUES (1,1,'Đồng bộ hóa')"))
    db.execute(text('INSERT INTO result_answers (result_id,question_id,is_correct) VALUES (1,1,0)'))
    db.execute(text('DELETE FROM enrollments'))
    assert an.topics(db,1)==[]


def test_catalog_reuses_names_for_manual_word_and_ai(db):
    first=resolve_topic(db,1,name=' Đồng   bộ hóa ')
    second=resolve_topic(db,1,name='ĐỒNG BỘ HÓA')
    assert first['id']==second['id']
    assert resolve_topic(db,1,topic_id=first['id'])['id']==first['id']
    with pytest.raises(ApiError):
        resolve_topic(db,2,topic_id=first['id'])


def test_saved_classification_is_not_changed_by_question_edit(db):
    original=resolve_topic(db,1,name='Đồng bộ hóa')
    changed=resolve_topic(db,1,name='Lập lịch CPU')
    result(db,1,4)
    db.execute(text("INSERT INTO questions (id,quiz_id,topic,topic_id) VALUES (1,1,:n,:t)"),dict(n=changed['name'],t=changed['id']))
    db.execute(text('INSERT INTO result_answers (result_id,question_id,is_correct,topic_id,topic_name,classification_version) VALUES (1,1,0,:t,:n,2)'),dict(t=original['id'],n=original['name']))
    topics=an.topics(db,1)
    assert topics[0]['topic_id']==original['id'] and topics[0]['topic']=='Đồng bộ hóa'
    assert topics[0]['sources'][0]['result_id']==1


def test_snapshot_unclassified_remains_unclassified_after_edit(db):
    topic=resolve_topic(db,1,name='Đồng bộ hóa')
    result(db,1,4)
    db.execute(text('INSERT INTO questions (id,quiz_id,topic,topic_id) VALUES (1,1,:n,:t)'),dict(n=topic['name'],t=topic['id']))
    db.execute(text('INSERT INTO result_answers (result_id,question_id,is_correct,classification_version) VALUES (1,1,0,2)'))
    assert an.topics(db,1)==[]
    assert an.unclassified_answers(db,1)==1


def test_confirmed_mapping_overrides_source_lesson():
    t=dict(course_id=1,topic='Semaphore',lesson_ids=[1],confirmed=True,mapped_lesson_id=2)
    lessons=[dict(id=1,course_id=1,title='Nguồn đề'),dict(id=2,course_id=1,title='Các giải pháp đồng bộ hóa')]
    assert rec._topic_action(t,lessons)['action_url']=='/lesson?id=2'
    t['confirmed']=False
    assert rec._topic_action(t,lessons)['action_url']=='/lesson?id=1'


def test_practice_quiz_requires_matching_topic_and_available_slot(db):
    db.execute(text('UPDATE quizzes SET review_lesson_id=1,max_attempts=1'))
    db.execute(text("INSERT INTO questions (id,quiz_id,topic,topic_id) VALUES (1,1,'Đồng bộ hóa',1)"))
    assert rec.practice_url(db,1,1,1,2) is None
    assert rec.practice_url(db,1,1,1,1)=='/quiz-show?id=1'
    result(db,1,4)
    assert rec.practice_url(db,1,1,1,1) is None


def test_comparison_exposes_sample_limits_and_no_causal_claim():
    before=dict(correct=2,answered=6,avg_score=33.3,question_ids=list(range(1,7)))
    after=dict(correct=3,answered=3,avg_score=100,question_ids=[7,8,9])
    assert study_progress.comparison(before,None)['state']=='waiting'
    observed=study_progress.comparison(before,after)
    assert observed['difference_pct']==66.7
    assert not observed['same_questions'] and not observed['sufficient_data']
    assert 'Không chứng minh' in observed['note']


def test_progress_uses_only_submissions_after_checkpoint(db,monkeypatch):
    topic=resolve_topic(db,1,name='Đồng bộ hóa')
    result(db,1,2,total=6)
    for qid in range(1,7):
        db.execute(text('INSERT INTO questions (id,quiz_id,topic,topic_id) VALUES (:q,1,:n,:t)'),dict(q=qid,n=topic['name'],t=topic['id']))
        db.execute(text('INSERT INTO result_answers (result_id,question_id,is_correct,topic_id,topic_name,classification_version) VALUES (1,:q,:ok,:t,:n,2)'),dict(q=qid,ok=int(qid<=2),t=topic['id'],n=topic['name']))
    # The production write helper commits; keep this fixture isolated.
    monkeypatch.setattr(study_progress,'execute',lambda session,sql,**params:session.execute(text(sql),params))
    checkpoint=study_progress.start(db,1,topic['id'])
    assert study_progress.start(db,1,topic['id'])['id']==checkpoint['id']
    assert study_progress.history(db,1)[0]['state']=='waiting'
    result(db,2,5,total=6)
    for qid in range(1,7):
        db.execute(text('INSERT INTO result_answers (result_id,question_id,is_correct,topic_id,topic_name,classification_version) VALUES (2,:q,:ok,:t,:n,2)'),dict(q=qid,ok=int(qid<=5),t=topic['id'],n=topic['name']))
    progress=study_progress.history(db,1)[0]
    assert progress['before']['correct']==2 and progress['after']['correct']==5
    assert progress['difference_pct']==50 and progress['same_questions'] and progress['sufficient_data']


def test_teacher_cannot_edit_another_courses_topic(db):
    db.execute(text('ALTER TABLE courses ADD COLUMN teacher_id INT DEFAULT 99'))
    topic=resolve_topic(db,1,name='Đồng bộ hóa')
    with pytest.raises(ApiError) as error:
        topic_routes.update({'id':topic['id'],'name':topic['name']},user={'id':100,'role':'teacher'},db=db)
    assert error.value.status==403


def test_topic_mapping_rejects_other_course_lesson(db):
    topic=resolve_topic(db,1,name='Đồng bộ hóa')
    db.execute(text('INSERT INTO chapters VALUES (2,2,1)'))
    db.execute(text("INSERT INTO lessons VALUES (2,'Bài môn khác',2,1)"))
    with pytest.raises(ApiError):
        topic_routes.update({'id':topic['id'],'name':topic['name'],'lesson_id':2},user={'id':1,'role':'admin'},db=db)


def test_topic_mapping_rejects_practice_without_topic_questions(db):
    topic=resolve_topic(db,1,name='Đồng bộ hóa')
    db.execute(text('UPDATE quizzes SET review_lesson_id=1'))
    with pytest.raises(ApiError):
        topic_routes.update({'id':topic['id'],'name':topic['name'],'practice_quiz_id':1},user={'id':1,'role':'admin'},db=db)


def test_checkpoint_denied_after_enrollment_removed(db):
    topic=resolve_topic(db,1,name='Đồng bộ hóa')
    db.execute(text('DELETE FROM enrollments'))
    with pytest.raises(ApiError) as error:
        study_progress.start(db,1,topic['id'])
    assert error.value.status==403
    assert rec.practice_url(db,1,1,1,topic['id']) is None


def test_catalog_rejects_missing_course_before_insert(db):
    with pytest.raises(ApiError) as error:
        resolve_topic(db,999,name='Chủ đề')
    assert error.value.status==404


def test_new_good_lesson_practice_suppresses_stale_topic_suggestion(db):
    result(db,1,0,total=6)
    db.execute(text("INSERT INTO quizzes VALUES (2,'Luyện bài',1,1,NULL,NULL,'latest',NULL,NULL)"))
    db.execute(text('INSERT INTO results (id,user_id,quiz_id,score,total) VALUES (2,1,2,6,6)'))
    for rid in (1,2):
        for n in range(6):
            qid=rid*10+n
            db.execute(text("INSERT INTO questions (id,quiz_id,topic) VALUES (:id,:q,'Đồng bộ hóa')"),dict(id=qid,q=rid))
            db.execute(text('''INSERT INTO result_answers (result_id,question_id,is_correct,knowledge_chapter_id,
                knowledge_lesson_id,knowledge_chapter_name,knowledge_lesson_name,knowledge_version)
                VALUES (:r,:q,:correct,1,1,'Chương 1','Đồng bộ hóa',2)'''),dict(r=rid,q=qid,correct=int(rid==2)))
    recommendation=rec.build(db,1)
    assert not any(i['type'] in ('review_knowledge','review_topic') for i in recommendation['items'])
    assert recommendation['summary']=='Tiếp tục luyện tập và học nội dung tiếp theo'


def test_history_filters_both_checkpoint_types_before_limit(db, monkeypatch):
    import json
    db.execute(text("INSERT INTO courses VALUES (2,'Môn khác')"))
    db.execute(text('INSERT INTO enrollments VALUES (2,1,2)'))
    monkeypatch.setattr(an, 'topics', lambda *args, **kwargs: [])
    from app.services import knowledge
    monkeypatch.setattr(knowledge, 'rows', lambda *args, **kwargs: [])
    baseline = json.dumps(dict(title='Bài học', correct=1, answered=2, avg_score=50))
    for cid in (1, 2):
        topic = resolve_topic(db, cid, name='Chủ đề')
        for index in range(12 if cid == 2 else 1):
            params = dict(t=topic['id'], c=cid, b=baseline)
            db.execute(text("INSERT INTO study_checkpoints (user_id,topic_id,baseline,baseline_result_id) VALUES (1,:t,:b,0)"), params)
            db.execute(text("INSERT INTO knowledge_study_checkpoints (user_id,course_id,unit_kind,unit_id,baseline,baseline_result_id) VALUES (1,:c,'lesson',1,:b,0)"), params)
    filtered = study_progress.history(db, 1, 1)
    assert len(filtered) == 2
    assert {row['checkpoint_kind'] for row in filtered} == {'topic', 'knowledge'}
    assert all(row['course_id'] == 1 for row in filtered)
    assert len(study_progress.history(db, 1)) == 10
    assert study_progress.history(db, 99, 1) == []
