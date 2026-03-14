import json
import math
import os

import pandas as pd

from app.models import Bakery
from app.review_analyzer import extract_tags


def _get_illust_url(signature_menu: str) -> str:
    """대표 메뉴 키워드로 일러스트 이미지 경로를 반환한다."""
    menu = signature_menu.lower()
    if any(k in menu for k in ["크루아상", "바게트", "캄파뉴"]):
        return "/static/illust/croissant.svg"
    if any(k in menu for k in ["케이크", "생크림"]):
        return "/static/illust/cake.svg"
    if any(k in menu for k in ["스콘", "앙버터"]):
        return "/static/illust/scone.svg"
    if any(k in menu for k in ["마카롱", "타르트"]):
        return "/static/illust/macaron.svg"
    return "/static/illust/loaf.svg"

# 문정역 좌표
MOONJEONG_STATION = (127.1225, 37.4858)  # (lon, lat)

"""
[데이터 관리 가이드]
1. 카카오 플레이스 연결: "kakao_id"를 업데이트하면 결과 페이지에서 [·] 버튼이 해당 페이지로 연결됩니다.
"""

# 카카오맵 API로 수집한 실제 문정동 베이커리 데이터 (2026-03-12 기준)
_RAW_BAKERIES = [
    {
        "id": 1,
        "name": "더 브레드 레지던스",
        "address": "서울 송파구 문정로 19",
        "mood": ["모던한", "감성적인"],
        "purpose": ["빵구경", "브런치", "식사빵"],
        "signature_menu": "소금빵",
        "flavor_profile": "겉은 바삭, 속에서 짭짤한 버터가 흘러나온다. 한 입이면 지구가 좋아진다.",
        "price_range": "일반",

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
        "kakao_id": "2088789791",
    },
    {
        "id": 2,
        "name": "오밀조밀베이크샵",
        "address": "서울 송파구 동남로2길 27-16",
        "mood": ["아늑한"],
        "purpose": ["빵구경", "선물", "동네 단골"],
        "signature_menu": "앙버터 스콘",
        "flavor_profile": "겉은 바삭하고 속은 촉촉한 스콘에 달콤한 앙금과 버터 한 덩이. 완벽한 조합.",
        "price_range": "일반",

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
        "kakao_id": "636209233",
    },
    {
        "id": 3,
        "name": "주빌리꽃케이크",
        "address": "서울 송파구 동남로6길 25-27",
        "mood": ["감성적인", "아늑한"],
        "purpose": ["케이크", "선물"],
        "signature_menu": "플라워 레터링 케이크",
        "flavor_profile": "부드러운 시트 위에 생크림 꽃이 핀다. 보는 것만으로도 행복해지는 맛.",
        "price_range": "프리미엄",

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
        "kakao_id": "1856377911",
    },
    {
        "id": 4,
        "name": "그루메",
        "address": "서울 송파구 동남로6길 26",
        "mood": ["모던한"],
        "purpose": ["브런치", "빵구경"],
        "signature_menu": "크루아상",
        "flavor_profile": "겹겹이 쌓인 페이스트리가 입안에서 사르르 녹는다. 버터 향의 정수.",
        "price_range": "프리미엄",

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
        "kakao_id": "1174657889",
    },
    {
        "id": 5,
        "name": "그라동빵집",
        "address": "서울 송파구 동남로8길 29",
        "mood": ["아늑한", "편안한"],
        "purpose": ["빵구경", "브런치", "동네 단골"],
        "signature_menu": "우유 식빵",
        "flavor_profile": "폭신하고 부드러운 식빵에서 은은한 우유 향이 난다. 소박하지만 자꾸 생각나는 맛.",
        "price_range": "일반",

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
        "kakao_id": "791885497",
    },
    {
        "id": 6,
        "name": "파리바게뜨 문정중앙점",
        "address": "서울 송파구 새말로 140",
        "mood": ["편안한", "모던한"],
        "purpose": ["브런치", "선물"],
        "signature_menu": "버터크루아상",
        "flavor_profile": "겉은 바삭, 속은 겹겹이 부드러운 버터 향. 한 입 베어 물면 고소한 바람이 분다.",
        "price_range": "일반",

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
        "kakao_id": "8114437",
    },
    {
        "id": 7,
        "name": "8084제빵소",
        "address": "서울 송파구 송파대로 155",
        "mood": ["모던한", "감성적인"],
        "purpose": ["빵구경", "모임", "식사빵"],
        "signature_menu": "통밀 캄파뉴",
        "flavor_profile": "투박한 겉면 아래 촉촉하고 쫀득한 속살. 씹을수록 고소한 곡물 향이 퍼진다.",
        "price_range": "프리미엄",

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
        "kakao_id": "1219420225",
    },
    {
        "id": 8,
        "name": "엘모리아케이크",
        "address": "서울 송파구 송파대로22길 24",
        "mood": ["감성적인", "아늑한"],
        "purpose": ["케이크", "선물", "모임"],
        "signature_menu": "딸기 생크림 케이크",
        "flavor_profile": "신선한 딸기의 상큼함과 생크림의 부드러움. 보는 것만으로도 행복해지는 맛.",
        "price_range": "프리미엄",

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
        "kakao_id": "285644079",
    },
    {
        "id": 9,
        "name": "뚜레쥬르 카페송파파크하비오점",
        "address": "서울 송파구 송파대로 111",
        "mood": ["편안한"],
        "purpose": ["브런치", "빵구경", "대형빵집"],
        "signature_menu": "생크림케이크",
        "flavor_profile": "폭신한 시트 위에 부드러운 생크림. 달콤하지만 무겁지 않아서 자꾸 손이 간다.",
        "price_range": "일반",

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
        "kakao_id": "470540287",
    },
    {
        "id": 10,
        "name": "삼송빵집 현대시티몰가든파이브점",
        "address": "서울 송파구 충민로 66",
        "mood": ["편안한", "모던한"],
        "purpose": ["빵구경", "선물", "대형빵집"],
        "signature_menu": "크림치즈빵",
        "flavor_profile": "바삭한 겉면 안에 진한 크림치즈가 가득. 한 입 베어 물면 고소한 행복이 터진다.",
        "price_range": "일반",

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
        "kakao_id": "589450462",
    },
]


def _haversine(lon1, lat1, lon2, lat2):
    """두 좌표 사이의 거리를 km로 계산한다."""
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )
    return R * 2 * math.asin(math.sqrt(a))


def _parse_coordinate(value, fallback):
    """좌표 문자열을 float로 변환한다. 실패 시 fallback 반환."""
    try:
        v = float(value)
        return v if v > 0 else fallback
    except (ValueError, TypeError):
        return fallback


def _tm_to_wgs84(x, y):
    """서울시 공공데이터 TM 좌표(EPSG:2097)를 WGS84(경도/위도)로 근사 변환한다.

    정밀 변환이 아닌 문정동 인근에서 유효한 선형 근사 공식.
    오차 범위: ~50m 이내.
    """
    # 서울 송파구 기준 보정 계수 (EPSG:2097 → WGS84)
    # 기준점: 문정역 TM(210900, 442400) ≈ WGS84(127.1225, 37.4858)
    ref_x, ref_y = 210900, 442400
    ref_lon, ref_lat = 127.1225, 37.4858

    # 1m당 경위도 변환 비율 (서울 위도 기준)
    m_per_deg_lon = 88740  # 경도 1도 ≈ 88.74km
    m_per_deg_lat = 111320  # 위도 1도 ≈ 111.32km

    lon = ref_lon + (x - ref_x) / m_per_deg_lon
    lat = ref_lat + (y - ref_y) / m_per_deg_lat
    return lon, lat


def _load_public_bakeries() -> list[dict]:
    """서울 열린데이터광장 CSV 데이터를 로드한다."""
    csv_path = os.getenv("PUBLIC_DATA_SOURCE_PATH", "data/public_bakery_sample.csv")
    if not os.path.exists(csv_path):
        return []

    try:
        try:
            df = pd.read_csv(csv_path, encoding="cp949")
        except UnicodeDecodeError:
            df = pd.read_csv(csv_path, encoding="utf-8")

        required = ["소재지전체주소", "상세영업상태명", "사업장명"]
        if not all(col in df.columns for col in required):
            return []

        # 문정동 + 영업중 필터
        mask = (
            df["소재지전체주소"].astype(str).str.contains("문정동", na=False)
            & df["상세영업상태명"].astype(str).str.contains("영업", na=False)
        )

        # 사업장명에 빵집/제과 관련 키워드가 있는 곳만 포함
        bakery_keywords = (
            "빵|베이커리|베이크|제과|케이크|크루아상|스콘|파티세리|제빵"
            "|쿠키|마카롱|타르트|도넛|호두과자|붕어빵|와플"
        )
        has_bakery_name = df["사업장명"].astype(str).str.contains(
            bakery_keywords, na=False
        )
        mask = mask & has_bakery_name
        filtered_df = df[mask]

        public_bakeries = []
        for i, row in filtered_df.iterrows():
            # 좌표 변환: 서울 열린데이터 좌표는 TM(EPSG:2097)
            raw_x = _parse_coordinate(row.get("좌표정보(x)"), 0)
            raw_y = _parse_coordinate(row.get("좌표정보(y)"), 0)
            if raw_x > 1000:  # TM 좌표 (값이 큼)
                lon, lat = _tm_to_wgs84(raw_x, raw_y)
            elif raw_x > 0:  # 이미 WGS84
                lon, lat = raw_x, raw_y
            else:  # 좌표 없음
                lon, lat = MOONJEONG_STATION[0], MOONJEONG_STATION[1]

            # 문정역 기준 거리 계산
            dist = round(
                _haversine(MOONJEONG_STATION[0], MOONJEONG_STATION[1], lon, lat),
                2,
            )

            # 도로명 주소 우선, 없으면 지번 주소
            road_addr = str(row.get("도로명전체주소", ""))
            addr = road_addr if road_addr and road_addr != "nan" else str(row["소재지전체주소"])

            # 공공데이터 업태에 따라 purpose/mood 추정
            biz_name = str(row["사업장명"])
            biz_type = str(row.get("위생업태명", ""))

            if "케이크" in biz_name:
                purpose = ["케이크", "선물"]
                mood = ["감성적인"]
                sig_menu = "케이크"
                price = "일반"
            elif "마카롱" in biz_name or "타르트" in biz_name:
                purpose = ["선물", "빵구경"]
                mood = ["감성적인"]
                sig_menu = "마카롱" if "마카롱" in biz_name else "타르트"
                price = "일반"
            elif "크루아상" in biz_name or "베이커리" in biz_name or "빵" in biz_name:
                purpose = ["빵구경", "브런치"]
                mood = ["아늑한"]
                sig_menu = "크루아상" if "크루아상" in biz_name else "대표 빵"
                price = "일반"
            else:
                purpose = ["빵구경"]
                mood = ["편안한"]
                sig_menu = "대표 빵"
                price = "일반"

            public_bakeries.append({
                "id": 1000 + i,
                "name": biz_name,
                "address": addr,
                "mood": mood,
                "purpose": purpose,
                "signature_menu": sig_menu,
                "flavor_profile": "",
                "price_range": price,
                "description": f"서울시 공공데이터 등록 제과점",
                "parking": False,
                "custom_order": "케이크" in biz_name,
                "distance": dist,
                "lat": lat,
                "lon": lon,
                "reviews": [],
            })
        return public_bakeries
    except Exception as e:
        print(f"공공데이터 로드 오류: {e}")
        return []


# 카카오 JSON에서 제외할 비빵집 카테고리/이름 패턴
_EXCLUDE_CATEGORIES = ["애견카페", "기업"]
_EXCLUDE_NAMES = ["고로케", "쌀고로케"]


def _infer_attributes(name: str, category: str) -> dict:
    """카카오 JSON 업체명/카테고리에서 mood, purpose, signature_menu 등을 추론한다."""
    name_lower = name.lower()

    if any(k in name_lower for k in ["케이크", "칼미아"]):
        return {
            "mood": ["감성적인"],
            "purpose": ["케이크", "선물"],
            "signature_menu": "케이크",
            "price_range": "일반",
            "custom_order": True,
        }
    if any(k in name_lower for k in ["마카롱", "타르트"]):
        return {
            "mood": ["감성적인"],
            "purpose": ["선물", "빵구경"],
            "signature_menu": "마카롱" if "마카롱" in name_lower else "타르트",
            "price_range": "일반",
            "custom_order": False,
        }
    if any(k in name_lower for k in ["크루아상", "브레드", "아티장"]):
        return {
            "mood": ["모던한"],
            "purpose": ["빵구경", "브런치"],
            "signature_menu": "크루아상",
            "price_range": "일반",
            "custom_order": False,
        }
    if any(k in name_lower for k in ["호두", "붕어빵", "꽈배기"]):
        return {
            "mood": ["편안한"],
            "purpose": ["빵구경"],
            "signature_menu": "대표 간식",
            "price_range": "일반",
            "custom_order": False,
        }
    if "방앗간" in name_lower:
        return {
            "mood": ["편안한"],
            "purpose": ["빵구경", "선물"],
            "signature_menu": "떡·한과",
            "price_range": "일반",
            "custom_order": False,
        }
    if any(k in name_lower for k in ["와플"]):
        return {
            "mood": ["편안한"],
            "purpose": ["빵구경", "브런치"],
            "signature_menu": "와플",
            "price_range": "일반",
            "custom_order": False,
        }
    # 프랜차이즈 판별
    franchises = ["파리바게뜨", "뚜레쥬르", "한스", "삼송", "아티제"]
    if any(f in name_lower for f in franchises):
        return {
            "mood": ["편안한", "모던한"],
            "purpose": ["브런치", "선물", "대형빵집"],
            "signature_menu": "대표 빵",
            "price_range": "일반",
            "custom_order": False,
        }
    # 기본: 동네 베이커리
    return {
        "mood": ["아늑한"],
        "purpose": ["빵구경", "브런치", "동네 단골"],
        "signature_menu": "대표 빵",
        "price_range": "일반",
        "custom_order": False,
    }


def _load_kakao_bakeries() -> list[dict]:
    """카카오 API JSON 파일에서 추가 베이커리를 로드한다."""
    json_path = os.path.join(os.path.dirname(__file__), "..", "data", "kakao_bakeries.json")
    if not os.path.exists(json_path):
        return []

    try:
        with open(json_path, "r", encoding="utf-8") as f:
            places = json.load(f)
    except Exception:
        return []

    # 시드 데이터 이름 목록 (중복 방지)
    seed_names = {b["name"] for b in _RAW_BAKERIES}

    kakao_bakeries = []
    next_id = 100  # 카카오 추가분은 100번대 ID

    for place in places:
        name = place["name"]
        category = place.get("category", "")

        # 이미 시드에 있으면 스킵
        if name in seed_names:
            continue

        # 비빵집 제외
        if any(exc in category for exc in _EXCLUDE_CATEGORIES):
            continue
        if any(exc in name for exc in _EXCLUDE_NAMES):
            continue

        attrs = _infer_attributes(name, category)

        kakao_bakeries.append({
            "id": next_id,
            "name": name,
            "address": place.get("address", ""),
            "mood": attrs["mood"],
            "purpose": attrs["purpose"],
            "signature_menu": attrs["signature_menu"],
            "flavor_profile": "",
            "price_range": attrs["price_range"],
    
            "description": f"문정동 인근 베이커리",
            "parking": False,
            "custom_order": attrs["custom_order"],
            "distance": place.get("distance_km", 0.0),
            "lat": place.get("lat", 0.0),
            "lon": place.get("lon", 0.0),
            "reviews": [],
            "kakao_id": place.get("kakao_id", ""),
        })
        next_id += 1

    return kakao_bakeries


def _load_bakery_photos() -> dict[str, str]:
    """data/bakery_photos.json에서 베이커리 사진 URL을 로드한다."""
    json_path = os.path.join(os.path.dirname(__file__), "..", "data", "bakery_photos.json")
    if not os.path.exists(json_path):
        return {}
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _build_bakeries() -> list[Bakery]:
    bakeries = []
    photos = _load_bakery_photos()

    # 1. 시드 데이터 (리치 데이터: 리뷰, 맛 프로필 등 보유)
    for raw in _RAW_BAKERIES:
        tags = extract_tags(raw["reviews"])
        image_url = _get_illust_url(raw["signature_menu"])
        photo_url = photos.get(str(raw["id"]), "")
        bakeries.append(Bakery(**raw, tags=tags, image_url=image_url, photo_url=photo_url))

    seen_names = {b.name for b in bakeries}

    # 2. 카카오 API JSON 추가분
    for raw in _load_kakao_bakeries():
        if raw["name"] in seen_names:
            continue
        tags = extract_tags(raw["reviews"])
        image_url = _get_illust_url(raw["signature_menu"])
        bakeries.append(Bakery(**raw, tags=tags, image_url=image_url))
        seen_names.add(raw["name"])

    # 3. 공공데이터 CSV 추가분
    for raw in _load_public_bakeries():
        if raw["name"] in seen_names:
            continue
        tags = extract_tags(raw["reviews"])
        image_url = _get_illust_url(raw["signature_menu"])
        bakeries.append(Bakery(**raw, tags=tags, image_url=image_url))
        seen_names.add(raw["name"])

    return bakeries


BAKERIES: list[Bakery] = _build_bakeries()
