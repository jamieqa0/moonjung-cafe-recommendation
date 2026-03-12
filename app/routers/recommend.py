from fastapi import APIRouter

from app.data import BAKERIES
from app.models import RecommendRequest, RecommendResponse
from app.recommender import recommend

router = APIRouter(prefix="/api", tags=["recommend"])


@router.post("/recommend", response_model=RecommendResponse)
def recommend_bakeries(req: RecommendRequest):
    results = recommend(
        BAKERIES,
        mood=req.mood,
        purpose=req.purpose,
        price_range=req.price_range,
        parking=req.parking,
        custom_order=req.custom_order,
        max_distance=req.max_distance,
    )
    return RecommendResponse(bakeries=results, total=len(results))
