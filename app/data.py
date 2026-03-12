from app.models import Bakery
from app.review_analyzer import extract_tags
import pandas as pd
import os

# 카카오맵 API로 수집한 실제 문정동 베이커리 데이터 (2026-03-12 기준)
_RAW_BAKERIES = [
    {
        "id": 1,
        "name": "더 브레드 레지던스",
        "address": "서울 송파구 문정로 19",
        "mood": ["모던한", "감성적인"],
        "purpose": ["빵구경", "브런치"],
        "signature_menu": "소금빵",
        "flavor_profile": "겉은 바삭, 속에서 짭짤한 버터가 흘러나온다. 한 입이면 지구가 좋아진다.",
        "price_range": "중가",
        "rating": 4.6,
        "description": "문정역 바로 앞, 갓 구운 빵 향이 퍼지는 동네 명소",
        "parking": False,
        "custom_order": False,
        "distance": 0.16,
        "lat": 37.4863683827294,
        "lon": 127.124732118681,
        "reviews": [
            "소금빵이 진짜 맛있어요 꼭 드세요",
            "크루아상도 바삭하고 버터 향이 진해요",
            "아침에 웨이팅 있지만 기다릴 가치 있어요",
            "브런치 세트가 든든하고 샌드위치 추천",
            "선물용 포장도 깔끔하게 해줘요",
        ],
    },
    {
        "id": 2,
        "name": "오밀조밀베이크샵",
        "address": "서울 송파구 동남로2길 27-16",
        "mood": ["아늑한", "빈티지한"],
        "purpose": ["빵구경", "선물"],
        "signature_menu": "앙버터 스콘",
        "flavor_profile": "겉은 바삭하고 속은 촉촉한 스콘에 달콤한 앙금과 버터 한 덩이. 완벽한 조합.",
        "price_range": "중가",
        "rating": 4.4,
        "description": "골목 안 숨은 수제 베이커리. 소량 생산의 정성.",
        "parking": False,
        "custom_order": False,
        "distance": 0.23,
        "lat": 37.486875294906,
        "lon": 127.12421397126,
        "reviews": [
            "스콘이 겉바속촉 그 자체예요",
            "아늑하고 따뜻한 분위기가 좋아요",
            "빵 종류마다 다 맛있어요 소금빵도 맛집",
            "포장도 예쁘게 해줘서 선물하기 좋아요",
            "브런치로 토스트 세트 강추",
        ],
    },
    {
        "id": 3,
        "name": "주빌리꽃케이크",
        "address": "서울 송파구 동남로6길 25-27",
        "mood": ["감성적인", "아늑한"],
        "purpose": ["케이크", "선물"],
        "signature_menu": "플라워 레터링 케이크",
        "flavor_profile": "부드러운 시트 위에 생크림 꽃이 핀다. 보는 것만으로도 행복해지는 맛.",
        "price_range": "고가",
        "rating": 4.7,
        "description": "꽃 장식 주문 제작 케이크 전문. 예약 필수.",
        "parking": False,
        "custom_order": True,
        "distance": 0.28,
        "lat": 37.4882293861933,
        "lon": 127.126873400704,
        "reviews": [
            "케이크가 너무 예쁘고 맛있어요",
            "생일 케이크 주문 제작 강추해요",
            "예쁜 박스에 선물 포장도 완벽",
            "레이어 케이크 시트가 폭신해요",
            "마카롱도 판매하는데 꼬끄가 맛있어요",
        ],
    },
    {
        "id": 4,
        "name": "그루메",
        "address": "서울 송파구 동남로6길 26",
        "mood": ["모던한"],
        "purpose": ["브런치", "빵구경"],
        "signature_menu": "크루아상",
        "flavor_profile": "겹겹이 쌓인 페이스트리가 입안에서 사르르 녹는다. 버터 향의 정수.",
        "price_range": "고가",
        "rating": 4.5,
        "description": "프렌치 스타일 아티잔 베이커리. 크루아상의 성지.",
        "parking": False,
        "custom_order": False,
        "distance": 0.29,
        "lat": 37.4881375602553,
        "lon": 127.125111588866,
        "reviews": [
            "크루아상이 정말 바삭해요 파리에서 먹는 맛",
            "바게트와 식빵 퀄리티가 최고예요",
            "항상 웨이팅이 있지만 기다릴 가치 있어요",
            "브런치 세트에 샌드위치가 맛있어요",
            "가격은 좀 있지만 퀄리티로 보면 가성비 좋아요",
        ],
    },
    {
        "id": 5,
        "name": "그라동빵집",
        "address": "서울 송파구 동남로8길 29",
        "mood": ["아늑한", "편안한"],
        "purpose": ["빵구경", "브런치"],
        "signature_menu": "우유 식빵",
        "flavor_profile": "폭신하고 부드러운 식빵에서 은은한 우유 향이 난다. 소박하지만 자꾸 생각나는 맛.",
        "price_range": "저가",
        "rating": 4.3,
        "description": "동네 단골들이 매일 찾는 가성비 빵집",
        "parking": False,
        "custom_order": False,
        "distance": 0.37,
        "lat": 37.4889417144691,
        "lon": 127.127216085529,
        "reviews": [
            "가성비가 최고예요 매일 와도 부담 없어요",
            "식빵이 맛있고 저렴해서 자주 사가요",
            "아늑하고 포근한 동네 빵집 느낌",
            "샌드위치도 있어서 브런치로 좋아요",
            "아침에 줄 서서 사가는 사람도 있어요",
        ],
    },
    {
        "id": 6,
        "name": "파리바게뜨 문정중앙점",
        "address": "서울 송파구 새말로 140",
        "mood": ["편안한", "모던한"],
        "purpose": ["브런치", "선물"],
        "signature_menu": "버터크루아상",
        "flavor_profile": "겉은 바삭, 속은 겹겹이 부드러운 버터 향. 한 입 베어 물면 고소한 바람이 분다.",
        "price_range": "중가",
        "rating": 4.0,
        "description": "언제나 믿을 수 있는 프랜차이즈 빵집",
        "parking": True,
        "custom_order": False,
        "distance": 0.37,
        "lat": 37.4834394692039,
        "lon": 127.12951214262407,
        "reviews": [
            "크루아상이 바삭하고 맛있어요",
            "선물용으로 포장도 예쁘게 해줘요",
            "주차 편하고 접근성 좋아요",
            "토스트랑 커피 세트가 브런치로 딱이에요",
            "마카롱도 꽤 괜찮아요 종류가 다양함",
        ],
    },
    {
        "id": 7,
        "name": "8084제빵소",
        "address": "서울 송파구 송파대로 155",
        "mood": ["빈티지한", "감성적인"],
        "purpose": ["빵구경", "모임"],
        "signature_menu": "통밀 캄파뉴",
        "flavor_profile": "투박한 겉면 아래 촉촉하고 쫀득한 속살. 씹을수록 고소한 곡물 향이 퍼진다.",
        "price_range": "고가",
        "rating": 4.5,
        "description": "천연 발효종으로 만드는 정통 수제 빵",
        "parking": False,
        "custom_order": False,
        "distance": 0.37,
        "lat": 37.4840819695712,
        "lon": 127.122681830992,
        "reviews": [
            "바게트와 캄파뉴가 정말 맛있어요",
            "천연 발효빵 퀄리티가 최고예요",
            "빈티지한 인테리어가 분위기 있어요",
            "주말에 웨이팅 있지만 기다릴 만해요",
            "스콘과 토스트도 맛있어서 브런치로 좋아요",
        ],
    },
    {
        "id": 8,
        "name": "엘모리아케이크",
        "address": "서울 송파구 송파대로22길 24",
        "mood": ["감성적인", "아늑한"],
        "purpose": ["케이크", "선물", "모임"],
        "signature_menu": "딸기 생크림 케이크",
        "flavor_profile": "신선한 딸기의 상큼함과 생크림의 부드러움. 보는 것만으로도 행복해지는 맛.",
        "price_range": "고가",
        "rating": 4.6,
        "description": "정성껏 만드는 주문 제작 케이크 전문점",
        "parking": True,
        "custom_order": True,
        "distance": 0.34,
        "lat": 37.4882960337149,
        "lon": 127.124356532836,
        "reviews": [
            "케이크가 너무 예쁘고 맛있어요",
            "생일 케이크 주문 제작 강추해요",
            "선물용 예쁜 박스 포장 완벽해요",
            "마카롱도 판매하는데 꼬끄가 쫀득해요",
            "따뜻하고 아늑한 분위기에서 케이크 고르기 좋아요",
        ],
    },
    {
        "id": 9,
        "name": "뚜레쥬르 카페송파파크하비오점",
        "address": "서울 송파구 송파대로 111",
        "mood": ["편안한"],
        "purpose": ["브런치", "빵구경"],
        "signature_menu": "생크림케이크",
        "flavor_profile": "폭신한 시트 위에 부드러운 생크림. 달콤하지만 무겁지 않아서 자꾸 손이 간다.",
        "price_range": "중가",
        "rating": 3.9,
        "description": "다양한 빵이 매일 신선하게 나오는 프랜차이즈 베이커리",
        "parking": True,
        "custom_order": True,
        "distance": 0.51,
        "lat": 37.481481190336,
        "lon": 127.123994746745,
        "reviews": [
            "케이크 주문 제작이 가능해요",
            "빵 종류가 정말 다양해요",
            "생일 케이크 맡기기 좋아요",
            "아침에 토스트 사가기 좋아요 브런치 느낌",
            "가격 대비 퀄리티 좋아서 자주 와요",
        ],
    },
    {
        "id": 10,
        "name": "삼송빵집 현대시티몰가든파이브점",
        "address": "서울 송파구 충민로 66",
        "mood": ["편안한", "모던한"],
        "purpose": ["빵구경", "선물"],
        "signature_menu": "크림치즈빵",
        "flavor_profile": "바삭한 겉면 안에 진한 크림치즈가 가득. 한 입 베어 물면 고소한 행복이 터진다.",
        "price_range": "중가",
        "rating": 4.2,
        "description": "대전 명물 삼송빵집의 문정동 분점. 줄 서서 사가는 인기 맛집.",
        "parking": True,
        "custom_order": False,
        "distance": 0.85,
        "lat": 37.47823066560411,
        "lon": 127.12455239836027,
        "reviews": [
            "크림치즈빵이 정말 맛있어요 꼭 드세요",
            "항상 줄이 길어요 대기 20분은 기본",
            "선물용으로 포장도 깔끔해요",
            "식빵이랑 소금빵도 맛있어요",
            "가성비 좋은 빵집이에요 가격 대비 최고",
        ],
    },
]


def _load_public_bakeries() -> list[dict]:
    """공공데이터포털/서울 열린데이터광장 CSV 데이터를 로드합니다."""
    csv_path = os.getenv("PUBLIC_DATA_SOURCE_PATH", "data/public_bakery_sample.csv")
    if not os.path.exists(csv_path):
        return []

    try:
        # 공공데이터 CSV 로드 (CP949 또는 UTF-8)
        try:
            df = pd.read_csv(csv_path, encoding='cp949')
        except UnicodeDecodeError:
            df = pd.read_csv(csv_path, encoding='utf-8')

        # '문정동' 필터링 및 '영업/정상' 상태 필터링
        # 컬럼명은 샘플 CSV 기준: '소재지전체주소', '상세영업상태명', '사업장명'
        mask = (
            df['소재지전체주소'].astype(str).str.contains('문정동', na=False) & 
            df['상세영업상태명'].astype(str).str.contains('영업', na=False)
        )
        filtered_df = df[mask]

        public_bakeries = []
        for i, row in filtered_df.iterrows():
            # Bakery 모델 필드에 맞게 매핑 (최소 정보 위주)
            public_bakeries.append({
                "id": 1000 + i, # 기존 ID와 겹치지 않게
                "name": row['사업장명'],
                "address": row['소재지전체주소'],
                "mood": ["일반적인"],
                "purpose": ["빵구경"],
                "signature_menu": "기본 빵",
                "flavor_profile": "공공데이터 제공 정보입니다.",
                "price_range": "중가",
                "rating": 4.0,
                "description": f"공공데이터포털 제공: {row['사업장명']}",
                "parking": False,
                "custom_order": False,
                "distance": 0.5,
                "lat": 37.48, # 기본값
                "lon": 127.12, # 기본값
                "reviews": []
            })
        return public_bakeries
    except Exception as e:
        print(f"Error loading public data: {e}")
        return []


def _build_bakeries() -> list[Bakery]:
    bakeries = []
    # 기존 카카오 데이터 로드
    for raw in _RAW_BAKERIES:
        tags = extract_tags(raw["reviews"])
        bakeries.append(Bakery(**raw, tags=tags))
    
    # 공공데이터 병합
    public_raw = _load_public_bakeries()
    for raw in public_raw:
        # 중복 확인 (이름 기준)
        if any(b.name == raw["name"] for b in bakeries):
            continue
        bakeries.append(Bakery(**raw, tags=[]))
        
    return bakeries


BAKERIES: list[Bakery] = _build_bakeries()
