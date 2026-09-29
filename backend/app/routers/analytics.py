"""/api/analytics/* — PHASE 4 Learning Analytics (dữ liệu của chính học viên đang đăng nhập)."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.responses import ApiError, ok
from app.services import analytics_service as svc

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


# GET /api/analytics/overview — chỉ số tổng quan: điểm TB, % hoàn thành, thời gian học, mức năng lực
@router.get("/overview")
def overview(
    course_id: int | None = Query(default=None),
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return ok(data=svc.overview(db, user["id"], course_id))


# GET /api/analytics/topics — điểm theo từng chủ đề (topic) của câu hỏi, kèm danh sách chủ đề yếu/mạnh
@router.get("/topics")
def topics(
    course_id: int | None = Query(default=None),
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    rows = svc.topics(db, user["id"], course_id)
    # Chủ đề yếu = mức Weak hoặc Average; chủ đề mạnh = mức Excellent
    weak = [t["topic"] for t in rows if t["status"] in ("Weak", "Average")]
    strong = [t["topic"] for t in rows if t["status"] == "Excellent"]
    return ok(data=rows, weak_topics=weak, strong_topics=strong)


# GET /api/analytics/quiz-progress?quiz_id=X — lịch sử các lần làm 1 quiz và mức tiến bộ
@router.get("/quiz-progress")
def quiz_progress(
    quiz_id: int = Query(default=0),
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not quiz_id:
        raise ApiError("Thiếu quiz_id.")
    return ok(data=svc.quiz_progress(db, user["id"], quiz_id))
