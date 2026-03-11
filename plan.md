# 문정동 카페 추천 시스템 개발 계획

## 목표

사용자가 분위기·목적·가격대를 선택하면 리뷰 기반 특징 분석을 거쳐 **TOP 3 카페**를 추천하는 웹 서비스.

## 기술 스택

- Python, FastAPI, Jinja2
- pytest (TDD)
- 인메모리 데이터 (DB 없음, MVP)

## 실행 명령어

```bash
# 의존성 설치
pip install -r requirements.txt

# 개발 서버 실행 (http://localhost:8000)
uvicorn app.main:app --reload

# 테스트 전체 실행
python -m pytest tests/ -v
```

---

## 개발 단계

### Phase 1. 데이터 모델 정의

> 테스트: `tests/test_models.py`

- `Cafe` 모델 — id, name, address, mood, purpose, signature_menu, price_range, rating, description, reviews, tags
- `RecommendRequest` 모델 — mood, purpose, price_range (모두 optional)
- `RecommendResponse` 모델 — cafes(list), total(int)

TDD 사이클:
1. Cafe 필수 필드 누락 시 ValidationError 발생 테스트
2. reviews, tags 기본값 빈 리스트 테스트
3. RecommendRequest 빈 요청 / 부분 요청 테스트
4. 모델 구현

현재 상태: **완료**

---

### Phase 2. 리뷰 기반 카페 특징 분석

> 테스트: `tests/test_review_analyzer.py`

`review_analyzer.py`의 `extract_tags(reviews: list[str]) -> list[str]` 함수 구현.

키워드-태그 매핑 규칙:

| 태그 | 매칭 키워드 |
|------|------------|
| 조용한 | 조용, 집중, 혼자 |
| 아늑한 | 아늑, 따뜻, 포근 |
| 디저트맛집 | 디저트, 케이크, 마카롱, 크로플, 빵 |
| 커피맛집 | 커피, 원두, 드립, 에스프레소 |
| 가성비좋은 | 가성비, 저렴, 가격 대비 |
| 뷰맛집 | 뷰, 전망, 야경, 창밖 |
| 넓은 | 넓, 공간이 넉넉, 좌석이 많 |
| 작업하기좋은 | 노트북, 작업, 콘센트, 와이파이 |

TDD 사이클:
1. 빈 리뷰 → 빈 태그 테스트
2. 매칭 키워드 없는 리뷰 → 빈 태그 테스트
3. 각 태그별 추출 테스트 (조용한, 아늑한, 디저트맛집, 커피맛집, 가성비좋은)
4. 복수 태그 동시 추출 테스트
5. 구현

현재 상태: **완료**

---

### Phase 3. TOP 3 추천 로직

> 테스트: `tests/test_recommender.py`

`recommender.py`의 `recommend()` 함수 구현.

#### 필터링

1. `quiet` (bool | None) — 조용한 카페 필터. None이면 무시
2. `power_socket` (bool | None) — 콘센트 유무 필터. None이면 무시
3. `max_distance` (float | None) — 문정역 기준 반경(km) 필터. `distance <= max_distance`

#### 점수 계산 공식

```
score = rating × 0.5
      + (mood 일치 시 +2)
      + (purpose 일치 시 +2)
      + (price_range 일치 시 +1)
      + (거리 보너스: (max_distance - distance) / max_distance)
```

점수 내림차순 정렬 후 **상위 3개** 반환 (max_results 기본값 3).
조건 미입력 시 rating 순 정렬.

테스트 클래스:
- `TestRecommendBasicFilter` — 기본 필터 (mood, purpose, price_range, max_results)
- `TestQuietFilter` — 조용한 카페 필터
- `TestPowerSocketFilter` — 콘센트 필터
- `TestDistanceFilter` — 거리 필터 + 거리 보너스
- `TestScoreCalculation` — 점수 누적, 순위 변동 검증

현재 상태: **완료**

---

### Phase 4. 시드 데이터

> 파일: `app/data.py`

문정동 카페 8곳 하드코딩. 앱 시작 시 `extract_tags()`로 각 카페의 tags 자동 생성.

현재 상태: **완료**

---

### Phase 5. API 엔드포인트

> 테스트: `tests/test_api.py`

| 메서드 | 경로 | 설명 |
|--------|------|------|
| GET | `/api/cafes` | 전체 카페 목록 (JSON) |
| GET | `/api/cafes/{id}` | 단일 카페 조회 (JSON, 404 처리) |
| POST | `/api/recommend` | 추천 요청 → TOP 3 반환 (JSON) |

TDD 사이클:
1. GET /api/cafes → 200 + 리스트 반환 테스트
2. GET /api/cafes/1 → 200 + 해당 카페 반환 테스트
3. GET /api/cafes/9999 → 404 테스트
4. POST /api/recommend 빈 조건 → 200 + cafes/total 포함 테스트
5. POST /api/recommend 각 조건별 테스트
6. 라우터 구현

현재 상태: **완료**

---

### Phase 6. 웹 프론트엔드 (Jinja2)

> 테스트: `tests/test_api.py::TestHTMLPages`

| 경로 | 템플릿 | 설명 |
|------|--------|------|
| GET `/` | index.html | 조건 선택 폼 (분위기/목적/가격대) |
| POST `/recommend` | results.html | TOP 3 카페 카드 리스트 |

현재 상태: **완료**

---

## 남은 작업

### Phase 7. 시드 데이터 보강

> 파일: `app/data.py`

- [ ] 8개 카페에 `quiet`, `power_socket`, `distance` 실제 값 추가 (현재 기본값 `False`/`0.0`)

### Phase 8. API 계층에 새 필터 반영

> 테스트: `tests/test_api.py`

- [ ] `RecommendRequest`에 `quiet`, `power_socket`, `max_distance` 필드 추가
- [ ] `routers/recommend.py`에서 새 파라미터를 `recommend()`에 전달
- [ ] HTML POST `/recommend` 라우트에서도 새 폼 필드 처리
- [ ] 새 필터 파라미터 API 통합 테스트 추가 (TDD)

### Phase 9. 프론트엔드 업데이트

> 파일: `templates/index.html`, `templates/results.html`

- [ ] `index.html` 폼에 조용한/콘센트 체크박스, 거리 슬라이더(또는 셀렉트) 추가
- [ ] `results.html`에 조용한/콘센트/거리 정보 표시
- [ ] `results.html`에 "TOP 3" 명시 표시

### Phase 10. 실제 카페 데이터 수집 (카카오맵 API)

> 하드코딩 시드 데이터 → 실제 문정동 카페 데이터로 교체

1. [ ] https://developers.kakao.com 에서 앱 등록 + **REST API 키** 발급
2. [ ] 카카오 로컬 API (`/v2/local/search/keyword`)로 "문정동 카페" 검색 → 이름/주소/좌표 수집
3. [ ] 좌표로 문정역(37.4857, 127.1264) 기준 거리(km) 계산
4. [ ] 리뷰 크롤링으로 리뷰 텍스트 보충 (카카오맵 or 네이버 지도)
5. [ ] 수집 데이터를 `app/data.py` 형식으로 변환
6. [ ] mood, purpose, price_range, quiet, power_socket 값은 리뷰/카테고리 기반으로 매핑

### 선택 (향후 확장)

- [ ] SQLite + SQLAlchemy로 데이터 영속화
- [ ] 카페 상세 페이지 (`/cafe/{id}`)
- [ ] 카카오맵 API 연동 (지도에 카페 위치 표시)
- [ ] 사용자 리뷰 등록 기능 → tags 실시간 재계산
- [ ] 키워드 가중치 도입 (빈도 기반 태그 신뢰도)
- [ ] 테스트 커버리지 측정 (`pytest-cov`)
