from pydantic import BaseModel


class Cafe(BaseModel):
    id: int
    name: str
    address: str
    mood: list[str]        # 예: ["조용한", "모던한"]
    purpose: list[str]     # 예: ["작업", "대화", "디저트"]
    signature_menu: str
    price_range: str       # "저가" / "중가" / "고가"
    rating: float
    description: str
    quiet: bool = False           # 조용한 카페 여부
    power_socket: bool = False    # 콘센트 유무
    distance: float = 0.0        # 문정역 기준 거리 (km)
    reviews: list[str] = []
    tags: list[str] = []          # 리뷰 분석으로 생성된 특징 태그


class RecommendRequest(BaseModel):
    mood: str | None = None
    purpose: str | None = None
    price_range: str | None = None


class RecommendResponse(BaseModel):
    cafes: list[Cafe]
    total: int
