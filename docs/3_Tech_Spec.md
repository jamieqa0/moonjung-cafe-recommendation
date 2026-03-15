# 문빵 스테이션 — 기술 명세서

---

## 1. 기술 스택

### 백엔드

- Python 3.11
- FastAPI
- Uvicorn
- Pydantic (데이터 모델 검증)
- python-dotenv (환경변수)
- python-multipart (HTML 폼 파싱)
- pandas (공공데이터 CSV 로딩)
- kiwipiepy (한국어 형태소 분석 — 리뷰 태그 추출)

### 프론트엔드

- Jinja2 템플릿
- HTML / CSS (CSS Grid, CSS 변수 기반 디자인 시스템)
- 카카오맵 JS SDK (지도 렌더링)
- tsparticles (별 파티클 배경 효과, CDN)

### 데이터 수집 (스크립트)

- Playwright (headless Chromium, 비동기) — 카카오맵·네이버 장소 페이지 스크래핑
- Pillow (이미지 색조 분석 — 따뜻한 톤 필터링)
- Anthropic Claude API (`generate_descriptions.py` 전용 — 베이커리 설명 자동 생성)

### 테스트

- pytest
- pytest-cov (커버리지 측정)
- httpx (FastAPI TestClient 의존성)

---

## 2. 시스템 아키텍처

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 [오프라인 — 스크립트 수동 실행]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  ┌──────────────────────────────┐   ┌──────────────────────────────────────┐
  │      카카오 경로               │   │           공공데이터 경로               │
  │                              │   │                                      │
  │  fetch_kakao_bakeries.py     │   │  fetch_seoul_bakeries.py             │
  │  카카오 로컬 API               │   │  서울 열린데이터광장 API                  │
  │  키워드: 문정동 베이커리/빵집/제과  │   │  제과점 인허가 데이터                     │
  │  반경 2km, kakao_id 포함       │   │  3단계 필터:                           │
  │           │                  │   │  ① 위생업태명 블랙리스트 (편의점·패스트푸드)  │
  │           ▼                  │   │  ② 상호명 블랙리스트 (편의점 브랜드 등)      │
  │  kakao_bakeries.json         │   │  ③ 빵집 양성 키워드 (베이커리·빵집·제과 등)  │
  │  (이름·주소·kakao_id·좌표)     │   │  413건 → 15곳 필터링                    │
  │           │                  │   │           │                           │
  │  ← kakao_id 입력 (순서 의존)   │   │           ▼                           │
  │           │                  │   │  public_bakeries.csv                  │
  │           ▼                  │   │  (사업장명·주소·좌표·영업상태)              │
  │  scrape_kakao_details.py     │   │           │                           │
  │  Playwright headless         │   │  ← 네이버 검색으로 장소 매핑 (순서 의존)    │
  │  place.map.kakao.com/{id}    │   │           │                           │
  │  ├─ .list_goods → 메뉴        │   │           ▼                           │
  │  ├─ .desc_review → 후기       │   │  scrape_naver_details.py             │
  │  ├─ .info_runtime → 영업시간   │   │  Playwright headless                 │
  │  └─ og:image → photo_url     │   │  search.naver.com → /p/entry/place   │
  │           │                  │   │  ├─ og:image → photo_url             │
  │           ▼                  │   │  ├─ .A_cdD → 영업시간                  │
  │  kakao_details.json          │   │  ├─ div.pui__vn15t2 → 방문자 리뷰       │
  │  (메뉴·후기·영업시간·photo_url  │   │  └─ .GXS1X → 메뉴                    │
  │   × 49개)                    │   │  15곳 중 10곳 수집 성공                  │
  └──────────────────────────────┘   │           │                           │
                                     │           ▼                           │
                                     │  naver_details.json                  │
                                     │  (og:image·영업시간·리뷰·메뉴 × 10개)   │
                                     └──────────────────────────────────────┘

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 [런타임 — 앱 기동 시 app/data.py 1회 실행]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  _RAW_BAKERIES (코드 내 시드 10곳, 수동 작성)
  + kakao_bakeries.json ──→ _load_kakao_bakeries()
  + kakao_details.json ──→   ↳ _infer_attributes()  mood·purpose·price_range 추론
                              ↳ _pick_menus()         음료 제외 대표메뉴 최대 3개
                              ↳ _load_place_details() 메뉴·후기·영업시간·photo_url 병합
  + public_bakeries.csv ─→ _load_public_bakeries()  [활성화]
  + naver_details.json ──→   ↳ _load_naver_details() photo_url·영업시간·리뷰·메뉴 병합
                              ↳ 3단계 필터 재검증 후 통합
         │  중복 이름 제거
         │  extract_tags()     리뷰 → 태그 자동 생성
         │  _get_illust_url()  대표메뉴 → 일러스트 자동 매핑
         │  _load_descriptions() descriptions.json 캐시 로딩
         ▼
  BAKERIES: list[Bakery]  (인메모리, 총 60곳)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 [요청 처리]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  클라이언트 (브라우저)
      │
      ├─ HTML 라우트 ──→ FastAPI → Jinja2 템플릿 렌더링
      │                               ├─ 카카오맵 JS SDK (비동기 로딩)
      │                               └─ tsparticles (CDN)
      │
      └─ JSON API ─────→ FastAPI 라우터
                              │
                              ▼
                       recommender.py
                       필터링 → 점수 계산 → 정렬
```

> **스크립트 실행 순서 (카카오 경로)**:
> `fetch_kakao_bakeries.py` → `scrape_kakao_details.py`
> `scrape_kakao_details.py`는 `kakao_bakeries.json`의 `kakao_id`를 입력으로 사용하므로 순서 의존.
>
> **스크립트 실행 순서 (공공데이터 경로)**:
> `fetch_seoul_bakeries.py` → `scrape_naver_details.py`
> `scrape_naver_details.py`는 `public_bakeries.csv`의 사업장명을 네이버 검색 쿼리로 사용.
>
> **두 경로는 독립적**으로 수집되며 런타임에 `_build_bakeries()`가 중복 제거 후 합산한다.

---

## 3. 프로젝트 구조

```
app/
├── main.py            ← FastAPI 앱 엔트리포인트, HTML 라우트, .env 로딩
├── models.py          ← Pydantic 모델 (Bakery, RecommendRequest, RecommendResponse)
├── data.py            ← 시드 데이터 10곳 + 카카오 수집 데이터 로딩 파이프라인
│                         _build_bakeries() → _load_kakao_bakeries() → _load_place_details()
├── recommender.py     ← 추천 로직 (필터링 → 점수 계산 → 정렬)
├── review_analyzer.py ← 리뷰 키워드 → 태그 매핑
├── sensory.py         ← 감각 기반 추천 매핑 (식감×맛→purpose, 분위기→mood)
└── routers/
    ├── cafes.py       ← GET /api/bakeries, GET /api/bakeries/{id}
    └── recommend.py   ← POST /api/recommend

data/
├── kakao_bakeries.json   ← 카카오 로컬 API로 수집한 문정동 베이커리 목록 (kakao_id 포함)
├── kakao_details.json    ← Playwright로 수집한 카카오맵 상세 정보 (메뉴·후기·영업시간·photo_url × 49개)
├── kakao_photos.json     ← (레거시) 카카오 이미지 검색 API로 수집한 사진 URL
├── naver_details.json    ← Playwright로 수집한 네이버 상세 정보 (photo_url·영업시간·리뷰·메뉴 × 10개)
├── public_bakeries.csv   ← 서울 열린데이터광장 인허가 데이터 (3단계 필터링 후 15곳)
└── descriptions.json     ← Claude Haiku API로 생성한 베이커리 설명 캐시

scripts/
├── fetch_kakao_bakeries.py   ← 카카오 로컬 API → kakao_bakeries.json 생성
├── scrape_kakao_details.py   ← Playwright headless → kakao_details.json 생성 (fetch_kakao_bakeries 이후 실행)
├── fetch_seoul_bakeries.py   ← 서울 열린데이터광장 API → public_bakeries.csv 생성 (3단계 필터 적용)
├── scrape_naver_details.py   ← Playwright headless → naver_details.json 생성 (fetch_seoul_bakeries 이후 실행)
├── generate_descriptions.py  ← Claude Haiku API로 베이커리 설명 자동 생성 → descriptions.json (ANTHROPIC_API_KEY 필요)
└── fetch_kakao_photos.py     ← (레거시) 카카오 이미지 검색 API → kakao_photos.json 생성

templates/
├── base.html          ← 레이아웃 셸 (헤더, 네비, 푸터, tsparticles)
├── index.html         ← 2컬럼: 소개+히어로 / 튜토리얼+칩 선택 폼
├── sensory.html       ← 2컬럼: 소개 / 3단계 이진 질문 폼
├── results.html       ← 3영역 그리드: 제목 + 카카오맵(sticky) + 카드 리스트
├── detail.html        ← 베이커리 상세: 실제 사진 + 일러스트 + 메뉴·영업시간·후기
├── bakeries.html      ← 전체 빵집 목록 (거리순 카드 그리드)
└── 404.html           ← 커스텀 404 페이지

static/
├── style.css          ← 앰버/크러스트 색상 팔레트, CSS Grid, 칩 그룹
├── icons/             ← 우주 테마 SVG 아이콘 세트 (18종)
├── illust/            ← 빵 종류별 SVG 일러스트 (croissant/cake/loaf/scone/macaron)
├── images/            ← 정적 이미지 디렉터리 (현재 미사용)
├── bg-croissant.jpg   ← 배경용 크루아상 이미지
├── hero-alien.svg     ← 히어로 일러스트 (빵을 든 우주인)
└── favicon.svg        ← SVG 파비콘

tests/
├── conftest.py        ← 공통 fixture (client, sample_cafes)
├── test_models.py     ← 모델 유효성
├── test_recommender.py← 추천 로직 단위 테스트
├── test_review_analyzer.py ← 리뷰 분석 단위 테스트
├── test_sensory.py    ← 감각 매핑 단위 테스트
├── test_data.py       ← 데이터 무결성 (좌표, ID 유일성, haversine, TM→WGS84, CSV 로더)
└── test_api.py        ← API + HTML 통합 테스트
```

---

## 4. API 설계

### HTML 라우트

| 메서드 | 경로 | 용도 |
|--------|------|------|
| GET | `/` | 메인 페이지 — 칩 기반 조건 선택 폼 |
| POST | `/recommend` | 폼 제출 → 카카오맵 + 카드 결과 페이지 |
| GET | `/bakery/{id}` | 베이커리 상세 페이지 |
| GET | `/bakeries` | 전체 빵집 목록 (거리순) |
| GET | `/sensory` | 감각 기반 추천 폼 |
| POST | `/sensory` | 감각 폼 제출 → 결과 페이지 |

### JSON API

#### 베이커리 목록 조회

```
GET /api/bakeries

응답:
[
  {
    "id": 1,
    "name": "더 브레드 레지던스",
    "address": "서울 송파구 문정로 19",
    "mood": ["모던한", "감성적인"],
    "purpose": ["빵구경", "브런치"],
    "signature_menu": "소금빵",
    "price_range": "일반",
    "description": "문정역 바로 앞, 갓 구운 빵 향이 퍼지는 동네 명소",
    "parking": false,
    "custom_order": false,
    "distance": 0.16,
    "lat": 37.4863,
    "lon": 127.1247,
    "flavor_profile": "겉은 바삭, 속에서 짭짤한 버터가 흘러나온다...",
    "image_url": "/static/illust/croissant.svg",
    "photo_url": "https://img1.kakaocdn.net/cthumb/local/...",
    "reviews": ["소금빵이 진짜 맛있어요...", ...],
    "tags": ["줄서는집", "선물하기좋은", ...],
    "kakao_id": "12345678",
    "hours": "21:00 까지"
  },
  ...
]
```

#### 베이커리 상세 조회

```
GET /api/bakeries/{id}

200: Bakery 객체 (위와 동일 구조)
404: {"detail": "Bakery not found"}
```

#### 추천 요청

```
POST /api/recommend

요청:
{
  "mood": "아늑한",
  "purpose": "브런치",
  "price_range": "일반",
  "parking": true,
  "custom_order": false,
  "max_distance": 1.0,
  "min_distance": 0.5
}
(모든 필드 선택사항. min_distance: 이 거리 미만 가게 제외)

응답:
{
  "bakeries": [ ... ],
  "total": 5
}
```

---

## 5. 데이터 모델

```python
class Bakery(BaseModel):
    # ── 기본 식별 정보 ──────────────────────────────────────────
    id: int                      # 고유 ID. 시드 1~10, 카카오 100번대, 공공데이터 200번대
    name: str                    # 상호명
    address: str                 # 도로명 주소
    kakao_id: str = ""           # 카카오 플레이스 ID. 카카오맵 링크·지도 마커에 사용

    # ── 추천 필터링 기준 ────────────────────────────────────────
    mood: list[str]              # 분위기 태그. ["아늑한"|"모던한"|"감성적인"|"편안한"|"동네 단골"|"대형빵집"] 복수 가능
    purpose: list[str]           # 방문 목적. ["브런치"|"선물"|"케이크"|"식사빵"|"모임"] 복수 가능
    price_range: str             # 가격대. "일반"(~2만원) | "프리미엄"(3만원~)
    parking: bool | None = None  # 주차 가능 여부. None = 미확인
    custom_order: bool | None = None  # 주문 제작 케이크 가능 여부. None = 미확인

    # ── 위치 정보 ───────────────────────────────────────────────
    distance: float = 0.0        # 문정역 기준 직선거리 (km). haversine 계산
    lat: float = 0.0             # WGS84 위도
    lon: float = 0.0             # WGS84 경도

    # ── 소개 텍스트 ─────────────────────────────────────────────
    description: str             # 베이커리 소개. Claude Haiku 생성 or 수동 작성
    signature_menu: list[str]    # 대표 메뉴 목록. 스크래핑 데이터 기반, 추론·생성 금지
    flavor_profile: str = ""     # 대표 메뉴 맛·식감 감각 묘사. 빈 문자열 = 미작성

    # ── 이미지 ──────────────────────────────────────────────────
    image_url: str = ""          # 빵 종류별 SVG 일러스트 경로. _get_illust_url()로 자동 매핑
    photo_url: str = ""          # 실제 사진 URL. 카카오맵 og:image 또는 네이버 og:image

    # ── 리뷰 & 태그 ─────────────────────────────────────────────
    reviews: list[str] = []      # 방문자 리뷰. 스크래핑 데이터 기반, 추론·생성 금지
    tags: list[str] = []         # 특징 태그. review_analyzer.extract_tags()로 자동 생성

    # ── 운영 정보 ───────────────────────────────────────────────
    hours: str | None = None     # 영업시간 문자열 (예: "21:00 까지"). None = 미확인


class RecommendRequest(BaseModel):
    mood: str | None = None           # 원하는 분위기
    purpose: str | None = None        # 방문 목적
    price_range: str | None = None    # 가격대 선호
    parking: bool | None = None       # 주차 필요 여부
    custom_order: bool | None = None  # 주문 제작 필요 여부
    max_distance: float | None = None # 최대 거리 (km). 이 반경 내 빵집만 포함
    min_distance: float | None = None # 최소 거리 (km). 이 거리 미만 빵집 제외 (폼 "far" → 0.5km)


class RecommendResponse(BaseModel):
    bakeries: list[Bakery]  # 추천 결과 목록 (점수 내림차순, 최대 5개)
    total: int              # 반환된 빵집 수
```

---

## 6. 추천 엔진

`recommender.recommend()` 함수가 전체 BAKERIES 리스트를 받아 필터링 → 점수 계산 → 정렬 순서로 처리한다.

### Step 1. 필터링

조건이 `None`이면 해당 필터는 건너뛴다 (선택하지 않은 조건은 제약 없음).

| 파라미터 | 조건 | 비고 |
|----------|------|------|
| `parking` | `bakery.parking == parking` 정확 일치 | `True` 요청 시 `None`(미확인) 빵집은 탈락 |
| `custom_order` | `bakery.custom_order == custom_order` 정확 일치 | 위와 동일 |
| `max_distance` | `bakery.distance <= max_distance` | 반경 내 빵집만 포함 |
| `min_distance` | `bakery.distance >= min_distance` | 너무 가까운 곳 제외. 폼에서 "조금 멀리" 선택 시 0.5km 적용 |

### Step 2. 점수 계산

필터를 통과한 빵집 각각에 점수를 계산한다. 최대 이론점수는 `2 + 2 + 1 + 3 + 1.5 = 9.5`.

```
score = 0

# 분위기 일치 (+2)
# mood는 bakery.mood 리스트 안에 포함 여부로 판단
if mood and mood in bakery.mood:
    score += 2

# 목적 일치 (+2)
# purpose는 bakery.purpose 리스트 또는 tags 리스트에서 검색
# tags에서도 찾는 이유: 리뷰 분석 태그("케이크맛집" 등)가 purpose를 보완하기 때문
if purpose and (purpose in bakery.purpose or purpose in bakery.tags):
    score += 2

# 가격대 일치 (+1)
if price_range and bakery.price_range == price_range:
    score += 1

# 거리 보너스 (+0 ~ +3)
# 문정역 인근 빵집들은 거리 차이가 작아 이 보너스로 자연스럽게 가까운 곳을 우선 노출
# max_distance가 없으면 거리 보너스 없음
if max_distance and max_distance > 0:
    score += max(0, (max_distance - bakery.distance) / max_distance) * 3

# 랜덤 다양화 (+0 ~ +1.5)
# 점수가 동점이거나 근접할 때 매번 같은 결과가 나오는 것을 방지
# 문정동처럼 밀집된 상권에서 다양한 빵집이 노출되도록 폭을 넓게 설정
score += random.uniform(0, 1.5)
```

### Step 3. 정렬 및 반환

```
scored.sort(key=lambda x: x[0], reverse=True)  # 점수 내림차순
return scored[:max_results]                      # 상위 N개 반환
```

| 호출 경로 | max_results |
|----------|-------------|
| HTML 라우트 (`POST /recommend`, `POST /sensory`) | 5 |
| JSON API (`POST /api/recommend`) | 5 (기본값, 요청에서 변경 불가) |

---

## 7. 리뷰 태그 추출

태그 생성 경로는 리뷰 보유 여부에 따라 두 가지로 나뉜다.

### 경로 A. 리뷰 있음 — `extract_tags()`

**ML/NLP 없음. 수동 정의된 규칙 기반.** 키워드는 실제 카카오·네이버 리뷰 텍스트를 보고 자주 등장하는 표현을 직접 추가한 것이다.

리뷰별 개별 카운팅 후 `min_reviews` 임계값 이상인 태그만 추출한다. 원본 텍스트와 형태소 분리 텍스트 양쪽에서 검색한다.

```python
morphed_reviews = [_morphemes(r) for r in reviews]
for tag, keywords in KEYWORD_TAG_MAP.items():
    match_count = sum(
        1 for raw, morphed in zip(reviews, morphed_reviews)
        if any(kw in raw or kw in morphed for kw in keywords)
    )
    if match_count >= min_reviews:   # 기본값 1, 상향 시 고신뢰 태그만 추출
        tags.append(tag)
```

| 태그 | 근거 키워드 |
|------|------------|
| 아늑한 | 아늑, 따뜻, 포근 |
| 케이크맛집 | 케이크, 생크림, 시트, 레이어, 생일케이크 |
| 마카롱맛집 | 마카롱, 꼬끄 |
| 소금빵맛집 | 소금빵 |
| 쿠키맛집 | 쿠키, 타르트, 까눌레, 두쫀쿠 |
| 베이글맛집 | 베이글 |
| 가성비좋은 | 가성비, 저렴, 가격 대비 |
| 줄서는집 | 줄, 웨이팅, 대기, 오픈런, 조기마감, 품절 |
| 선물하기좋은 | 선물, 포장, 예쁜 박스 |
| 브런치맛집 | 브런치, 샌드위치, 토스트, 스콘 |
| 식사빵 | 발효, 통밀, 치아바타, 깜빠뉴, 바게트, 호밀, 담백, 식사 |
| 동네 단골 | 동네, 단골, 편안한, 매일 |
| 대형빵집 | 대형, 넓은, 쾌적, 주차편한, 2층, 대규모 |
| 친절한 | 친절 |

### mood / purpose 출처

`mood`와 `purpose`는 수집 데이터에서 자동 추출되는 값이 아니다.

| 출처 | 결정 방식 |
|------|----------|
| 시드 데이터 (id 1~10) | `data.py`에 수동 하드코딩 |
| 카카오 API 추가분 (100번대) | `_infer_attributes(이름, 카테고리, 리뷰)`로 규칙 기반 추론 |
| 공공데이터 (200번대) | 동일하게 `_infer_attributes()` 추론 |

`_infer_attributes()`는 상호명·카테고리 키워드 패턴 매칭이 핵심이며, 리뷰는 보조적으로만 반영된다. 따라서 **mood/purpose는 순수 수집 데이터 기반이 아니라 규칙 기반 추론값**임을 유의.

### 경로 B. 리뷰 없음 — `generate_fallback_tags()`

스크래핑으로 리뷰를 수집하지 못한 빵집(주로 공공데이터 출처)은 이미 가지고 있는 `mood`/`purpose` 값으로 태그를 대체 생성한다.

| mood / purpose | 생성 태그 |
|----------------|----------|
| mood: 아늑한 | 아늑한 |
| mood: 편안한 | 동네 단골 |
| mood: 감성적인 | 선물하기좋은 |
| mood: 모던한 | 모던한 |
| mood: 동네 단골 | 동네 단골 |
| mood: 대형빵집 | 대형빵집 |
| purpose: 브런치 | 브런치맛집 |
| purpose: 선물 | 선물하기좋은 |
| purpose: 케이크 | 케이크맛집 |
| purpose: 식사빵 | 식사빵 |

### 한계

| 항목 | 상태 | 내용 |
|------|------|------|
| 형태소 분석 미적용 | ✅ 해결 | kiwipiepy 연동. 원본 OR 형태소 양쪽 검색으로 조사·어미 변형 감지 |
| 빈도·가중치 | ✅ 적용 중 | 리뷰별 개별 카운팅 + `min_reviews` 파라미터. `data.py` 호출부에서 리뷰 3개 이상이면 `min_reviews=2` 적용 — 2개 이상 리뷰에 등장한 키워드만 태그로 생성 |
| 키워드가 없으면 태그 누락 | 🔲 미해결 | 근본 한계. 키워드 목록 확충으로 완화 가능 |
| 키워드 목록 수동 관리 | 🔲 미해결 | 신조어·신메뉴 등장 시 직접 추가 필요. 빈출 단어 자동 제안 미구현 |

---

## 8. 감각 기반 추천 매핑

"빵집 용어를 모르는 사용자"를 위한 대안 추천 경로. 3단계 이진 질문(식감 → 맛 → 분위기)으로 `mood`/`purpose`를 추론해 기존 추천 엔진에 전달한다.

```python
def map_sensory_to_conditions(texture, taste, atmosphere) -> dict:
    return {
        "mood":    _MOOD_MAP.get(atmosphere),             # 미매칭 시 None → 필터 미적용
        "purpose": _PURPOSE_MAP.get((texture, taste)),    # 미매칭 시 None → 필터 미적용
    }
```

### 식감 × 맛 → purpose (2×2 조합)

| 식감 | 맛 | purpose | 해석 |
|------|-----|---------|------|
| 바삭 | 달콤 | *(None)* | 특정 목적 미결정 → 필터 미적용 (페이스트리·크루아상 범위가 purpose와 불일치) |
| 바삭 | 고소 | 식사빵 | 바게트·캄파뉴 등 담백한 식사 빵을 원하는 사람 |
| 부드러움 | 달콤 | 케이크 | 생크림·무스 케이크를 원하는 사람 |
| 부드러움 | 고소 | 브런치 | 소프트한 식사 빵·샌드위치를 원하는 사람 |

### 분위기 → mood

| 분위기 | mood | 해석 |
|--------|------|------|
| 혼자 | 아늑한 | 조용하고 아늑한 동네 빵집 선호 |
| 여럿 | 편안한 | 일행과 함께 가기 편한 넓은 빵집 선호 |

### 한계

| 항목 | 상태 | 내용 |
|------|------|------|
| `(바삭, 고소)`와 `(부드러움, 고소)` 브런치 수렴 | ✅ 해결 | `(바삭, 고소)` → `식사빵`으로 분리. 두 조합이 다른 purpose로 연결됨 |
| 하드코딩된 기본값 | ✅ 해결 | 미매칭 시 `None` 반환 → recommend()에서 필터 미적용으로 처리 |
| `(바삭, 달콤)` 목적 불분명 | ✅ 해결 | 기존 `빵구경` 매핑 제거 → `None` 반환. 빵구경은 모든 빵집이 해당하므로 구별력 없음 |
| 분위기 선택지 2개뿐 | 🔲 미해결 | `모던한`·`감성적인`·`동네 단골`·`대형빵집`은 감각 폼과 결이 다름. 조건으로 찾기(index.html)에서 선택 가능 |
| 단방향 변환 | 🔲 미해결 | 감각 입력 → mood/purpose 단방향만 지원. 역방향 미구현 |

---

## 9. 외부 연동

### 카카오맵 JS SDK

- `KAKAO_JS_KEY` 환경변수 필요 (없으면 지도 영역 미표시)
- `autoload=false` + `kakao.maps.load()` 콜백 패턴으로 비동기 로딩
- 문정역 기준 마커 + 베이커리 마커 + 인포윈도우
- SDK 실패 시 폴백 메시지 표시

### 일러스트 자동 매핑

- `_get_illust_url()` 함수가 대표 메뉴 키워드로 SVG 경로 결정
- croissant / cake / scone / macaron / loaf 5종

---

## 10. 성능 목표

- 추천 응답 시간: < 100ms (인메모리 데이터 기반)

---

## 11. 테스트 전략

pytest 기반 TDD. 외부 의존성 없이 독립 실행.

| 테스트 파일 | 대상 |
|------------|------|
| test_models.py | 모델 생성, 유효성 검증, Pydantic 에러 |
| test_recommender.py | 필터링(mood/purpose/price/parking/custom_order/distance), 점수 계산 |
| test_review_analyzer.py | 태그 추출, 복수 태그, 빈 리뷰, 미매칭 |
| test_sensory.py | 식감×맛 매핑, 분위기 매핑 |
| test_data.py | 좌표, 리뷰, 태그, ID 유일성, haversine, TM→WGS84, CSV 로더 |
| test_api.py | API 엔드포인트 + HTML 페이지 통합 테스트 |
