# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 프로젝트 개요

문정동 베이커리 추천 웹 서비스. Python FastAPI 기반, TDD(pytest) 개발 방식.
리뷰 텍스트에서 키워드를 추출해 베이커리 특징 태그를 자동 생성하고, 분위기·목적·가격대·주차·주문제작·거리 조건으로 베이커리를 추천한다.

- **GitHub**: https://github.com/jamieqa0/moonbbang-station

## 개발 명령어

```bash
# 의존성 설치
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

## 아키텍처

- **app/main.py** — FastAPI 앱 엔트리포인트. HTML 라우트(Jinja2)와 API 라우터 등록. `.env`에서 `KAKAO_JS_KEY` 로딩
- **app/models.py** — Pydantic 모델: `Bakery`, `RecommendRequest`, `RecommendResponse`
- **app/data.py** — 카카오맵 API 시드 데이터(10곳) + 공공데이터 CSV 로더(6곳). `MOONJEONG_STATION = (127.1225, 37.4858)`. TM→WGS84 좌표 변환 포함
- **app/recommender.py** — 추천 로직. 조건별 가중 점수 계산 후 정렬 반환
- **app/review_analyzer.py** — 리뷰 키워드 → 태그 매핑 (`KEYWORD_TAG_MAP` 딕셔너리 기반)
- **app/sensory.py** — 감각 기반 추천 매핑 (식감×맛→purpose, 분위기→mood)
- **app/routers/** — API 엔드포인트 분리 (`cafes.py`→베이커리 라우터, `recommend.py`)
- **scripts/fetch_public_data.py** — 서울 열린데이터광장 API 수집 스크립트

### 추천 로직 (`recommender.recommend()`)

1. **필터링 단계**: parking, custom_order는 정확 일치 필터. max_distance는 `<= max_distance`로 반경 필터.
2. **점수 계산**: `rating × 0.5` + mood 일치 `+2` + purpose 일치 `+2` + price_range 일치 `+1` + 거리 보너스 `(max_distance - distance) / max_distance`
3. **정렬**: 점수 내림차순, 상위 max_results개 반환 (기본 3)

### 데이터 흐름

```
리뷰 텍스트 → review_analyzer.extract_tags() → Cafe.tags
사용자 조건 → recommender.recommend() → 필터링 → 점수 계산 → 정렬된 Cafe 리스트
```

### API 엔드포인트

| 메서드 | 경로 | 용도 |
|--------|------|------|
| GET | `/` | 메인 페이지 — 칩 기반 조건 선택 폼 (HTML) |
| POST | `/recommend` | 폼 제출 → 2컬럼 결과 페이지: 카카오맵 + 카드 (HTML) |
| GET | `/sensory` | 감각 기반 추천 폼 (HTML) |
| POST | `/sensory` | 감각 폼 제출 → 결과 페이지 (HTML) |
| GET | `/api/bakeries` | 전체 베이커리 목록 (JSON) |
| GET | `/api/bakeries/{id}` | 단일 베이커리 조회 (JSON) |
| POST | `/api/recommend` | 추천 요청 (JSON) |

### 프론트엔드

- **templates/base.html** — 레이아웃 셸. "문정동 빵 안내소" 타이틀, 네비게이션(추천받기/감각으로 찾기), 파비콘
- **templates/index.html** — 히어로 섹션 + 지구 음식 가이드(details/summary) + 칩/배지 선택 폼 (분위기·목적·가격대)
- **templates/sensory.html** — 3단계 이진 질문 UI (식감/맛/분위기 라디오)
- **templates/results.html** — 2컬럼 레이아웃: 카카오맵(좌, sticky) + 카드 리스트(우). 카드 호버 시 마커 인포윈도우 연동
- **templates/404.html** — 커스텀 404 ("이 빵집은 아직 이 우주에 없어요")
- **static/style.css** — 따뜻한 앰버/크러스트 색상 팔레트 (`--cream`, `--ink`, `--amber`, `--crust`). 라디알 그래디언트 별 배경, 칩 그룹, 커스텀 라디오/체크박스
- **static/favicon.png** — 32×32 빵 아이콘

### 외부 연동

- **카카오맵 JS SDK** — `KAKAO_JS_KEY` 환경변수 필요. results.html에서 지도 렌더링
- **공공데이터 CSV** — `data/public_bakery_sample.csv`. `PUBLIC_DATA_SOURCE_PATH` 환경변수로 경로 지정 가능

## 테스트 구조

TDD 기반. 테스트를 먼저 작성하고 구현한다. 현재 92개 테스트.

- `tests/test_models.py` — 모델 유효성
- `tests/test_recommender.py` — 추천 로직 단위 테스트 (BasicFilter, ParkingFilter, CustomOrderFilter, DistanceFilter, ScoreCalculation)
- `tests/test_review_analyzer.py` — 리뷰 분석 단위 테스트
- `tests/test_sensory.py` — 감각 기반 매핑 로직 단위 테스트
- `tests/test_data.py` — 데이터 무결성 (좌표, 리뷰, 태그, ID 유일성, haversine, TM→WGS84, CSV 로더)
- `tests/test_api.py` — API + HTML 통합 테스트
- `tests/conftest.py` — 공통 fixture (`client`, `sample_cafes`)
