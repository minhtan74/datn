"""/api/recommendations — PHASE 5 Rule-based Personalized Recommendation."""
from fastapi import APIRouter, Body, Depends, Query
from sqlalchemy.orm import Session

from app.ai import recommendation as rec
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.responses import ok

router = APIRouter(prefix="/api/recommendations", tags=["recommendations"])


# GET /api/recommendations — gợi ý học tập hiện tại + 10 lần gợi ý đã lưu gần nhất
@router.get("")
def get_recommendations(
    course_id: int | None = Query(default=None),
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Gợi ý hiện tại (tính trực tiếp từ dữ liệu mới nhất) + lịch sử đã lưu."""
    current = rec.build(db, user["id"], course_id)
    return ok(data={"current": current, "history": rec.history(db, user["id"], 10)})


# POST /api/recommendations/refresh — người học bấm "Cập nhật gợi ý"
@router.post("/refresh")
def refresh(
    body: dict = Body(default={}),
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Tính lại từ dữ liệu học tập mới nhất và LƯU lại (1 dòng lịch sử mới)."""
    course_id = body.get("course_id")
    # Tính lại gợi ý từ dữ liệu mới nhất rồi lưu vào lịch sử
    course_id = int(course_id) if course_id else None
    current = rec.build(db, user["id"], course_id)
    saved = rec.save(db, user["id"], course_id, current)
    return ok("Đã cập nhật gợi ý học tập.", data=saved)
