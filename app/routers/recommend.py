from fastapi import APIRouter

from app.data import CAFES
from app.models import RecommendRequest, RecommendResponse
from app.recommender import recommend

router = APIRouter(prefix="/api", tags=["recommend"])


@router.post("/recommend", response_model=RecommendResponse)
def recommend_cafes(req: RecommendRequest):
    results = recommend(
        CAFES,
        mood=req.mood,
        purpose=req.purpose,
        price_range=req.price_range,
    )
    return RecommendResponse(cafes=results, total=len(results))
