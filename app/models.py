from pydantic import BaseModel


class Bakery(BaseModel):
    id: int
    name: str
    address: str
    mood: list[str]        # 예: ["아늑한", "모던한"]
    purpose: list[str]     # 예: ["브런치", "선물", "케이크"]
    signature_menu: list[str]
    price_range: str       # "일반" / "프리미엄"
    description: str
    parking: bool | None = None         # 주차 가능 여부 (None = 미확인)
    custom_order: bool | None = None    # 주문 제작 케이크 가능 여부 (None = 미확인)
    distance: float = 0.0        # 문정역 기준 거리 (km)
    lat: float = 0.0             # 위도
    lon: float = 0.0             # 경도
    flavor_profile: str = ""       # 대표 메뉴 맛 프로필 (식감, 맛, 향)
    image_url: str = ""            # 빵집 일러스트 이미지 경로
    photo_url: str = ""            # 빵집 실제 사진 URL (외부 이미지)
    reviews: list[str] = []
    tags: list[str] = []          # 리뷰 분석으로 생성된 특징 태그
    kakao_id: str = ""           # 카카오 플레이스 ID
    hours: str | None = None     # 영업시간 (예: "21:00 까지")


class RecommendRequest(BaseModel):
    mood: str | None = None
    purpose: str | None = None
    price_range: str | None = None
    parking: bool | None = None
    custom_order: bool | None = None
    max_distance: float | None = None
    min_distance: float | None = None


class RecommendResponse(BaseModel):
    bakeries: list[Bakery]
    total: int
