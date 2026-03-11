from fastapi import APIRouter, HTTPException

from app.data import CAFES

router = APIRouter(prefix="/api/cafes", tags=["cafes"])


@router.get("/")
def get_all_cafes():
    return CAFES


@router.get("/{cafe_id}")
def get_cafe(cafe_id: int):
    for cafe in CAFES:
        if cafe.id == cafe_id:
            return cafe
    raise HTTPException(status_code=404, detail="카페를 찾을 수 없습니다")
