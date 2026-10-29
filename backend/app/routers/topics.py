"""Teacher-owned topic catalog and explicit study material mappings."""
from fastapi import APIRouter, Depends, Query, Body
from app.core.database import get_db, q_all, q_one, execute
from app.core.dependencies import require_roles
from app.core.responses import ok, ApiError
from ._common import assert_owns_course
from app.services.topic_catalog import catalog, resolve_topic
from app.services.analytics_service import normalize_topic
from sqlalchemy import text

router=APIRouter(prefix='/api/topics',tags=['topics'])


@router.get('')
def index(course_id:int=Query(...),user=Depends(require_roles('admin','teacher')),db=Depends(get_db)):
    assert_owns_course(db,user,course_id)
    return ok(data={'topics':catalog(db,course_id),
        'lessons':q_all(db,'SELECT l.id,l.title FROM lessons l JOIN chapters ch ON ch.id=l.chapter_id WHERE ch.course_id=:c ORDER BY ch.order_index,ch.id,l.order_index,l.id',c=course_id),
        'quizzes':q_all(db,'SELECT id,title FROM quizzes WHERE course_id=:c AND (chapter_id IS NOT NULL OR review_lesson_id IS NOT NULL) ORDER BY id',c=course_id)})


@router.post('')
def create(body:dict=Body(...),user=Depends(require_roles('admin','teacher')),db=Depends(get_db)):
    try:
        cid=int(body.get('course_id') or 0)
    except (ValueError,TypeError):
        raise ApiError('Khóa học không hợp lệ.')
    assert_owns_course(db,user,cid)
    if not str(body.get('name') or '').strip():
        raise ApiError('Vui lòng nhập tên chủ đề.')
    if len(str(body['name']))>100:
        raise ApiError('Tên chủ đề tối đa 100 ký tự.')
    topic=resolve_topic(db,cid,name=str(body['name']))
    db.commit()
    return ok('Đã thêm chủ đề.',data=topic)


@router.put('')
def update(body:dict=Body(...),user=Depends(require_roles('admin','teacher')),db=Depends(get_db)):
    try:
        tid=int(body.get('id') or 0)
        lesson=int(body['lesson_id']) if body.get('lesson_id') else None
        practice=int(body['practice_quiz_id']) if body.get('practice_quiz_id') else None
    except (ValueError,TypeError):
        raise ApiError('Chủ đề hoặc tài liệu không hợp lệ.')
    topic=q_one(db,'SELECT * FROM course_topics WHERE id=:id',id=tid)
    if not topic:
        raise ApiError('Không tìm thấy chủ đề.',404)
    cid=topic['course_id'];assert_owns_course(db,user,cid)
    name=' '.join(str(body.get('name') or '').split())
    if not name or len(name)>100:
        raise ApiError('Tên chủ đề phải có từ 1 đến 100 ký tự.')
    duplicate=q_one(db,'SELECT id FROM course_topics WHERE course_id=:c AND normalized_name=:n AND id<>:id',c=cid,n=normalize_topic(name),id=tid)
    if duplicate:
        raise ApiError('Tên chủ đề đã tồn tại; hãy chọn chủ đề đó khi phân loại câu hỏi.')
    if lesson and not q_one(db,'SELECT l.id FROM lessons l JOIN chapters ch ON ch.id=l.chapter_id WHERE l.id=:id AND ch.course_id=:c',id=lesson,c=cid):
        raise ApiError('Bài học không thuộc khóa học này.')
    if practice and not q_one(db,'SELECT id FROM quizzes WHERE id=:id AND course_id=:c AND (chapter_id IS NOT NULL OR review_lesson_id IS NOT NULL)',id=practice,c=cid):
        raise ApiError('Bài luyện phải là bộ ôn tập thuộc khóa học này.')
    if practice and not q_one(db,'SELECT id FROM questions WHERE quiz_id=:q AND topic_id=:t LIMIT 1',q=practice,t=tid):
        raise ApiError('Bài luyện chưa có câu hỏi thuộc chủ đề này. Hãy phân loại câu hỏi trước.')
    db.execute(text('UPDATE course_topics SET name=:n,normalized_name=:k,lesson_id=:l,practice_quiz_id=:q,confirmed=:f WHERE id=:id'),
            dict(n=name,k=normalize_topic(name),l=lesson,q=practice,f=1 if body.get('confirmed') is True else 0,id=tid))
    db.execute(text('UPDATE questions SET topic=:n WHERE topic_id=:id'),dict(n=name,id=tid))
    db.commit()
    return ok('Đã cập nhật chủ đề và liên kết học tập.')
