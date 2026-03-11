# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 프로젝트 개요

문정동 카페 추천 웹 서비스. Python FastAPI 기반, TDD(pytest) 개발 방식.
리뷰 텍스트에서 키워드를 추출해 카페 특징 태그를 자동 생성하고, 분위기·목적·가격대·조용함·콘센트·거리 조건으로 카페를 추천한다.

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

- **app/main.py** — FastAPI 앱 엔트리포인트. HTML 라우트(Jinja2)와 API 라우터 등록
- **app/models.py** — Pydantic 모델: `Cafe`, `RecommendRequest`, `RecommendResponse`
- **app/data.py** — 인메모리 시드 데이터. 앱 시작 시 `review_analyzer`로 태그 자동 생성
- **app/recommender.py** — 추천 로직. 조건별 가중 점수 계산 후 정렬 반환
- **app/review_analyzer.py** — 리뷰 키워드 → 태그 매핑 (`KEYWORD_TAG_MAP` 딕셔너리 기반)
- **app/routers/** — API 엔드포인트 분리 (`cafes.py`, `recommend.py`)

### 추천 로직 (`recommender.recommend()`)

1. **필터링 단계**: quiet, power_socket은 정확 일치 필터. max_distance는 `<= max_distance`로 반경 필터.
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
| GET | `/` | 메인 페이지 (HTML) |
| POST | `/recommend` | 폼 제출 → 결과 페이지 (HTML) |
| GET | `/api/cafes` | 전체 카페 목록 (JSON) |
| GET | `/api/cafes/{id}` | 단일 카페 조회 (JSON) |
| POST | `/api/recommend` | 추천 요청 (JSON) |

## 테스트 구조

TDD 기반. 테스트를 먼저 작성하고 구현한다.

- `tests/test_models.py` — 모델 유효성
- `tests/test_recommender.py` — 추천 로직 단위 테스트 (BasicFilter, QuietFilter, PowerSocketFilter, DistanceFilter, ScoreCalculation)
- `tests/test_review_analyzer.py` — 리뷰 분석 단위 테스트
- `tests/test_api.py` — API 통합 테스트
- `tests/conftest.py` — 공통 fixture (`client`, `sample_cafes`)
