from app.models import Cafe
from app.review_analyzer import extract_tags

_RAW_CAFES = [
    {
        "id": 1,
        "name": "스타벅스 문정법조타운점",
        "address": "문정동 642-3",
        "mood": ["모던한", "활기찬"],
        "purpose": ["작업", "대화"],
        "signature_menu": "콜드브루",
        "price_range": "중가",
        "rating": 4.1,
        "description": "넓은 좌석과 안정적인 와이파이",
        "reviews": [
            "노트북 작업하기 좋아요",
            "콘센트가 많아서 편해요",
            "커피 맛은 평범하지만 공간이 넉넉해요",
        ],
    },
    {
        "id": 2,
        "name": "투썸플레이스 문정역점",
        "address": "문정동 55-7",
        "mood": ["아늑한"],
        "purpose": ["대화", "디저트"],
        "signature_menu": "스트로베리 초콜릿 생크림",
        "price_range": "중가",
        "rating": 4.0,
        "description": "디저트가 맛있는 대화 카페",
        "reviews": [
            "케이크가 진짜 맛있어요",
            "분위기가 아늑하고 따뜻해요",
            "디저트 종류가 다양해요",
        ],
    },
    {
        "id": 3,
        "name": "블루보틀 문정점",
        "address": "문정동 290-1",
        "mood": ["모던한", "조용한"],
        "purpose": ["작업", "커피"],
        "signature_menu": "싱글 오리진 드립커피",
        "price_range": "고가",
        "rating": 4.6,
        "description": "스페셜티 원두의 깊은 풍미",
        "reviews": [
            "원두 퀄리티가 최고예요",
            "조용하고 집중하기 좋아요",
            "커피 맛만큼은 여기가 최고",
        ],
    },
    {
        "id": 4,
        "name": "이디야커피 문정로데오점",
        "address": "문정동 101-5",
        "mood": ["편안한"],
        "purpose": ["작업", "대화"],
        "signature_menu": "토피넛라떼",
        "price_range": "저가",
        "rating": 3.7,
        "description": "가성비 좋은 동네 카페",
        "reviews": [
            "가성비가 최고예요",
            "저렴한 가격에 커피 한 잔 하기 좋아요",
            "자리가 좀 좁지만 괜찮아요",
        ],
    },
    {
        "id": 5,
        "name": "카페 문정",
        "address": "문정동 78-12",
        "mood": ["아늑한", "조용한"],
        "purpose": ["데이트", "대화"],
        "signature_menu": "바닐라 플랫화이트",
        "price_range": "중가",
        "rating": 4.4,
        "description": "로컬 감성의 숨은 보석",
        "reviews": [
            "분위기가 너무 좋아요 데이트 추천",
            "커피도 맛있고 아늑해요",
            "조용해서 이야기하기 좋아요",
        ],
    },
    {
        "id": 6,
        "name": "할리스 문정역점",
        "address": "문정동 33-9",
        "mood": ["편안한", "활기찬"],
        "purpose": ["대화", "디저트"],
        "signature_menu": "허니브레드",
        "price_range": "중가",
        "rating": 3.9,
        "description": "허니브레드로 유명한 카페",
        "reviews": [
            "허니브레드 맛집이에요",
            "디저트 종류가 많아요",
            "넓어서 단체 모임에도 좋아요",
        ],
    },
    {
        "id": 7,
        "name": "앤트러사이트 문정점",
        "address": "문정동 150-3",
        "mood": ["모던한", "조용한"],
        "purpose": ["작업", "커피"],
        "signature_menu": "에스프레소",
        "price_range": "고가",
        "rating": 4.5,
        "description": "로스터리 카페의 정석",
        "reviews": [
            "에스프레소가 훌륭해요",
            "인테리어가 모던하고 멋져요",
            "조용히 작업하기 최고",
        ],
    },
    {
        "id": 8,
        "name": "크로플하우스",
        "address": "문정동 212-8",
        "mood": ["활기찬"],
        "purpose": ["디저트", "대화"],
        "signature_menu": "크로플 세트",
        "price_range": "저가",
        "rating": 4.2,
        "description": "크로플 전문 디저트 카페",
        "reviews": [
            "크로플이 바삭하고 맛있어요",
            "가성비 좋은 디저트 카페",
            "학생들에게 추천",
        ],
    },
]


def _build_cafes() -> list[Cafe]:
    cafes = []
    for raw in _RAW_CAFES:
        tags = extract_tags(raw["reviews"])
        cafes.append(Cafe(**raw, tags=tags))
    return cafes


CAFES: list[Cafe] = _build_cafes()
