# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 프로젝트 개요

문정동 베이커리 추천 웹 서비스. Python FastAPI 기반, TDD(pytest) 개발 방식.
리뷰 텍스트에서 키워드를 추출해 베이커리 특징 태그를 자동 생성하고, 분위기·목적·가격대·주차·주문제작·거리 조건으로 베이커리를 추천한다.

- **GitHub**: https://github.com/jamieqa0/moonbbang-station

## 의존성 구조

- **`requirements.txt`** — 프로덕션(Render) 배포용. `kiwipiepy`, `playwright`, `pytest` 계열 제외
- **`requirements-dev.txt`** — 로컬 개발용 (`-r requirements.txt` 포함 + 테스트/스크래핑 도구)

> **kiwipiepy 제거 이유**: Render 무료 플랜 메모리(512MB) 초과로 OOM 발생.
> `review_analyzer.py`는 단순 부분 문자열 검색(`kw in text`)으로 대체. 한국어 키워드 특성상 정확도 차이 미미.

## 개발 명령어

```bash
# 의존성 설치 (로컬 개발)
pip install -r requirements-dev.txt

# 배포용만 설치할 때
pip install -r requirements.txt

# 개발 서버 실행 (http://localhost:8000)
uvicorn app.main:app --reload
# 또는 run.bat 더블클릭

# 테스트 전체 실행
python -m pytest tests/ -v

# 특정 테스트 파일 실행
python -m pytest tests/test_recommender.py -v

# 특정 테스트 함수 실행
python -m pytest tests/test_recommender.py::TestRecommendBasicFilter::test_filter_by_mood -v
```

## 환경 변수

`.env.sample` 참고. `.env` 파일에 설정:

- `KAKAO_JS_KEY` — 카카오맵 JS SDK 키 (results.html 지도 렌더링). 없으면 지도 영역 미표시
- `KAKAO_REST_API_KEY` — 카카오 REST API 키 (데이터 수집 스크립트 전용, 앱 실행에는 불필요)
- `PUBLIC_DATA_SOURCE_PATH` — 공공데이터 CSV 경로 (기본값: `data/public_bakeries.csv`. 강화된 필터로 서비스 활성화됨)
- `ANTHROPIC_API_KEY` — Claude API 키 (`scripts/generate_descriptions.py` 전용, 앱 실행에는 불필요)

## 아키텍처

- **app/main.py** — FastAPI 앱 엔트리포인트. HTML 라우트(Jinja2)와 API 라우터 등록. `.env`에서 `KAKAO_JS_KEY` 로딩
- **app/models.py** — Pydantic 모델: `Bakery`(image_url, photo_url 필드 포함), `RecommendRequest`, `RecommendResponse`
- **app/data.py** — 카카오맵 API 시드 데이터(10곳). `MOONJEONG_STATION = (127.1225, 37.4858)`. 대표 메뉴 키워드 기반 일러스트 자동 매핑(`_get_illust_url`). `_load_bakery_photos()`로 `data/kakao_photos.json`에서 실제 사진 URL 로딩. `_load_naver_details()`로 `data/naver_details.json`에서 공공데이터 빵집 실제 사진·메뉴·리뷰 로딩. `_load_public_bakeries()`에서 강화된 3단계 필터(위생업태명 블랙리스트 → 상호명 블랙리스트 → 빵집 이름 양성 키워드) 후 네이버 데이터 통합. `_load_descriptions()`로 `data/descriptions.json` 캐시 로딩. 전체 빵집 60곳
- **app/recommender.py** — 추천 로직. 조건별 가중 점수 계산 후 정렬 반환
- **app/review_analyzer.py** — 리뷰 키워드 → 태그 매핑 (`KEYWORD_TAG_MAP` 딕셔너리 기반)
- **app/sensory.py** — 감각 기반 추천 매핑 (식감×맛→purpose, 분위기→mood)
- **app/routers/** — API 엔드포인트 분리 (`cafes.py`→베이커리 라우터, `recommend.py`)
- **scripts/fetch_kakao_bakeries.py** — 카카오 로컬 API → `data/kakao_bakeries.json` 생성
- **scripts/fetch_seoul_bakeries.py** — 서울 열린데이터광장 API → `data/public_bakeries.csv` 생성 (3단계 필터링: 위생업태명 블랙리스트 + 상호명 블랙리스트 + 빵집 이름 양성 키워드)
- **scripts/scrape_kakao_details.py** — Playwright headless → `data/kakao_details.json` 생성 (`fetch_kakao_bakeries.py` 이후 실행 필수)
- **scripts/scrape_naver_details.py** — Playwright headless → `data/naver_details.json` 생성 (공공데이터 빵집 대상, `fetch_seoul_bakeries.py` 이후 실행 필수). 수집 항목: og:image, 영업시간, 방문자 리뷰, 메뉴
- **scripts/fetch_kakao_photos.py** — (레거시) 카카오 이미지 검색 API → `data/kakao_photos.json` 생성
- **scripts/generate_descriptions.py** — Claude Haiku API로 베이커리 설명 자동 생성 → `data/descriptions.json`. 이름+주소+리뷰 기반, 증분 저장(기존 항목 스킵). `ANTHROPIC_API_KEY` 필요

### 추천 로직 (`recommender.recommend()`)

- **분위기(mood) 카테고리**: 아늑한(동네빵집) / 모던한(전문 아티잔 베이커리) / 감성적인(포토제닉) / 편안한(프랜차이즈) / 동네 단골(단골 빵집 느낌) / 대형빵집(대형 매장)
- **가격대 기준**: 일반 / 프리미엄 (이름·카테고리 키워드 기반 자동 추론)

1. **필터링 단계**: parking, custom_order는 정확 일치 필터. max_distance는 `<= max_distance`로 반경 필터. min_distance는 `>= min_distance`로 가까운 곳 제외 필터 (폼에서 "far" 선택 시 0.5km 적용).
2. **점수 계산**: mood 일치 `+2` + purpose 일치 `+2` + price_range 일치 `+1` + 거리 보너스 `((max_distance - distance) / max_distance) × 3` + 랜덤 다양화 `0~1.5`
3. **정렬**: 점수 내림차순, 상위 max_results개 반환 (HTML 라우트: 5, API 기본: 5)

### 데이터 흐름

```
리뷰 텍스트 → review_analyzer.extract_tags() → Bakery.tags
사용자 조건 → recommender.recommend() → 필터링 → 점수 계산 → 정렬된 Bakery 리스트
감각 입력 → sensory.map_sensory_to_conditions() → mood/purpose → recommend()
```

### API 엔드포인트

| 메서드 | 경로 | 용도 |
|--------|------|------|
| GET | `/` | 메인 페이지 — 칩 기반 조건 선택 폼 (HTML) |
| POST | `/recommend` | 폼 제출 → 2컬럼 결과 페이지: 카카오맵 + 카드 (HTML) |
| GET | `/bakery/{id}` | 베이커리 상세 페이지 (HTML) |
| GET | `/bakeries` | 전체 빵집 목록 — 거리순 정렬 (HTML) |
| GET | `/sensory` | 감각 기반 추천 폼 (HTML) |
| POST | `/sensory` | 감각 폼 제출 → 결과 페이지 (HTML) |
| GET | `/api/bakeries` | 전체 베이커리 목록 (JSON) |
| GET | `/api/bakeries/{id}` | 단일 베이커리 조회 (JSON) |
| POST | `/api/recommend` | 추천 요청 (JSON) |

### 프론트엔드

- **templates/base.html** — 레이아웃 셸. 헤더, 네비게이션(추천받기/감각으로 찾기/전체 빵집), 푸터, tsparticles 별 배경
- **templates/index.html** — 2컬럼: 좌(소개+히어로) / 우(튜토리얼 details/summary + 칩 선택 폼)
- **templates/sensory.html** — 2컬럼: 좌(소개) / 우(3단계 이진 질문 폼)
- **templates/results.html** — 3영역 그리드: top(제목) + left(카카오맵 sticky) + right(카드 리스트). 카드에 일러스트 이미지 표시. 카드 호버 시 마커 인포윈도우 연동
- **templates/detail.html** — 베이커리 상세 페이지. 실제 사진(photo_url) + 일러스트 + 상세 정보 표시
- **templates/bakeries.html** — 전체 빵집 목록. 거리순 카드 그리드. Motion 라이브러리 hover 애니메이션(scale+rotate). 네이버·카카오 외부 링크 버튼
- **templates/404.html** — 커스텀 404 ("이 빵집은 아직 이 우주에 없어요")
- **static/style.css** — 따뜻한 앰버/크러스트 색상 팔레트 (`--cream`, `--ink`, `--amber`, `--crust`). CSS Grid 2컬럼 레이아웃, 칩 그룹, 커스텀 라디오/체크박스. **`font-size`는 반드시 CSS 변수 사용**: `--text-xs` / `--text-sm` / `--text-base` / `--text-md` / `--text-lg` / `--text-xl` / `--text-2xl` / `--text-3xl` — 하드코딩 절대 금지
- **static/icons/** — 카와이 스타일 우주 테마 SVG 아이콘 세트 (골든 앰버 #FBBD40 fill + 다크 퍼플 #3A1F54 outline). 헤더, 네비, 칩, 버튼, 폼 라벨 등에 사용
- **static/illust/** — 빵 종류별 카와이 SVG 일러스트 (croissant/cake/loaf/scone/macaron). 결과 카드에 표시. `_get_illust_url()`로 대표 메뉴 키워드 기반 자동 매핑
- **static/hero-alien.svg** — 히어로 일러스트 (빵을 든 우주인 캐릭터)
- **static/favicon.svg** — SVG 파비콘 (카와이 빵 아이콘)

### UI/UX 규칙

- **"빵맛집" 태그·용어 절대 사용 금지** — 서비스 자체가 빵집 추천이므로 중복 표현임. 대신 구체적인 특징 태그(예: "아늑한", "포토제닉") 사용.

### 데이터 무결성 원칙

- `signature_menu`, `reviews` — **절대 추론/생성 금지**. 스크래핑 데이터(`kakao_details.json`, `naver_details.json`)에 없으면 빈 배열 `[]`
- `description` — LLM 생성 OK. 반드시 상호명+위치+리뷰 기반. `"문정동 인근 베이커리"` 같은 고정 플레이스홀더 금지
- `mood`, `purpose` — 이름만으로 추론 금지; 이름+리뷰 텍스트 기반으로 `_infer_attributes(name, category, reviews)` 호출
- `flavor_profile` — 빈 문자열 `""` 기본값. 스크래핑 데이터 외에는 임의 생성 금지

### 외부 연동

- **카카오맵 JS SDK** — `KAKAO_JS_KEY` 환경변수 필요. results.html에서 `autoload=false` + `kakao.maps.load()` 콜백 패턴으로 비동기 로딩. SDK 실패 시 폴백 메시지 표시
- **공공데이터 CSV** — `data/public_bakeries.csv`. 413건 중 실제 빵집 15곳으로 필터링(3단계: 위생업태명 블랙리스트 → 상호명 블랙리스트 → 빵집 이름 양성 키워드). `_load_public_bakeries()`로 서비스에 통합됨
- **tsparticles** — CDN으로 로딩하는 별 파티클 배경 효과

## 테스트 구조

TDD 기반. 테스트를 먼저 작성하고 구현한다.

- `tests/test_models.py` — 모델 유효성
- `tests/test_recommender.py` — 추천 로직 단위 테스트 (BasicFilter, ParkingFilter, CustomOrderFilter, DistanceFilter, ScoreCalculation)
- `tests/test_review_analyzer.py` — 리뷰 분석 단위 테스트
- `tests/test_sensory.py` — 감각 기반 매핑 로직 단위 테스트
- `tests/test_data.py` — 데이터 무결성 (좌표, 리뷰, 태그, ID 유일성, haversine, TM→WGS84, CSV 로더)
- `tests/test_api.py` — API + HTML 통합 테스트
- `tests/conftest.py` — 공통 fixture (`client`, `sample_bakeries`)

## 배포

Render.com 배포 설정 (`render.yaml`):
- Python 3.11, `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
