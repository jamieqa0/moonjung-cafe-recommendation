# 문정동 빵 안내소 — 개발 계획

> **We Are The Universe** — 우주 어디서든 환영합니다.

## 목표

지구에 처음 온 외계인도 편하게 쓸 수 있는 **문정동 베이커리 추천 웹 서비스**.
사용자가 분위기·목적·가격대를 선택하면 리뷰 기반 특징 분석을 거쳐 **TOP 3 베이커리**를 추천한다.

## 기술 스택

- Python, FastAPI, Jinja2
- pytest (TDD)
- 인메모리 데이터 (DB 없음, MVP)
- 배포: Render (무료 티어)

## 링크

- **GitHub**: https://github.com/jamieqa0/moonbbang-station

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

- `Bakery` 모델 — id, name, address, mood, purpose, signature_menu, price_range, rating, description, parking, custom_order, distance, reviews, tags
- `RecommendRequest` 모델 — mood, purpose, price_range (모두 optional)
- `RecommendResponse` 모델 — bakeries(list), total(int)

TDD 사이클:
1. Bakery 필수 필드 누락 시 ValidationError 발생 테스트
2. reviews, tags 기본값 빈 리스트 테스트
3. RecommendRequest 빈 요청 / 부분 요청 테스트
4. 모델 구현

현재 상태: **완료**

---

### Phase 2. 리뷰 기반 베이커리 특징 분석

> 테스트: `tests/test_review_analyzer.py`

`review_analyzer.py`의 `extract_tags(reviews: list[str]) -> list[str]` 함수 구현.

키워드-태그 매핑 규칙:

| 태그 | 매칭 키워드 |
|------|------------|
| 아늑한 | 아늑, 따뜻, 포근 |
| 빵맛집 | 빵, 식빵, 바게트, 크루아상, 소금빵 |
| 케이크맛집 | 케이크, 생크림, 시트, 레이어 |
| 마카롱맛집 | 마카롱, 꼬끄 |
| 가성비좋은 | 가성비, 저렴, 가격 대비 |
| 줄서는집 | 줄, 웨이팅, 대기 |
| 선물하기좋은 | 선물, 포장, 예쁜 박스 |
| 브런치맛집 | 브런치, 샌드위치, 토스트, 스콘 |

TDD 사이클:
1. 빈 리뷰 → 빈 태그 테스트
2. 매칭 키워드 없는 리뷰 → 빈 태그 테스트
3. 각 태그별 추출 테스트 (빵맛집, 케이크맛집, 아늑한, 가성비좋은, 선물하기좋은)
4. 복수 태그 동시 추출 테스트
5. 구현

현재 상태: **완료**

---

### Phase 3. TOP 3 추천 로직

> 테스트: `tests/test_recommender.py`

`recommender.py`의 `recommend()` 함수 구현.

#### 필터링

1. `parking` (bool | None) — 주차 가능 필터. None이면 무시
2. `custom_order` (bool | None) — 주문 제작 케이크 필터. None이면 무시
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
- `TestParkingFilter` — 주차 가능 필터
- `TestCustomOrderFilter` — 주문 제작 케이크 필터
- `TestDistanceFilter` — 거리 필터 + 거리 보너스
- `TestScoreCalculation` — 점수 누적, 순위 변동 검증

현재 상태: **완료**

---

### Phase 4. 시드 데이터

> 파일: `app/data.py`

문정동 베이커리 8곳 하드코딩. 앱 시작 시 `extract_tags()`로 각 베이커리의 tags 자동 생성.

| # | 이름 | 가격대 | 주차 | 주문제작 |
|---|------|:----:|:----:|:------:|
| 1 | 파리바게뜨 문정법조타운점 | 중가 | O | X |
| 2 | 뚜레쥬르 문정역점 | 중가 | X | O |
| 3 | 밀도 문정점 | 고가 | X | X |
| 4 | 봄봄 베이커리 | 중가 | X | X |
| 5 | 르뱅 문정 | 고가 | O | X |
| 6 | 크루아상하우스 문정 | 중가 | X | X |
| 7 | 마리 케이크 문정 | 고가 | O | O |
| 8 | 땅콩베이커리 문정 | 저가 | X | X |

현재 상태: **완료**

---

### Phase 5. API 엔드포인트

> 테스트: `tests/test_api.py`

| 메서드 | 경로 | 설명 |
|--------|------|------|
| GET | `/api/bakeries` | 전체 베이커리 목록 (JSON) |
| GET | `/api/bakeries/{id}` | 단일 베이커리 조회 (JSON, 404 처리) |
| POST | `/api/recommend` | 추천 요청 → TOP 3 반환 (JSON) |

현재 상태: **완료**

---

### Phase 6. 웹 프론트엔드 (Jinja2)

> 테스트: `tests/test_api.py::TestHTMLPages`

| 경로 | 템플릿 | 설명 |
|------|--------|------|
| GET `/` | index.html | 조건 선택 폼 (분위기/목적/가격대) |
| POST `/recommend` | results.html | TOP 3 베이커리 카드 리스트 |

현재 상태: **완료**

---

### Phase 7. We Are The Universe — 톤 & 외계인 친화 기능

> 테스트: `tests/test_api.py::TestHTMLPages` (8개 테스트 추가)

서비스 전체를 "우주 어디서든 환영합니다" 콘셉트로 전환.

- [x] `base.html` — "문정동 빵 안내소" 타이틀 + "우주 어디서든 환영합니다" 서브카피 + footer "We Are The Universe."
- [x] `index.html` — 환영 메시지 ("어서 와, 우주에서 온 친구"), "잘 모르겠어요" 기본 옵션, "내 빵집 찾기" 버튼
- [x] `index.html` — 지구 음식 가이드 도움말 섹션 (접이식 details/summary)
- [x] `results.html` — "당신을 위해 고른 문정동의 빵집" 헤더, 맛 프로필 표시
- [x] `results.html` — 랜덤 초대 메시지 ("문정동은 항상 여기서 기다릴게요"), "다른 빵집도 궁금하다면" 링크
- [x] `404.html` — "이 빵집은 아직 이 우주에 없어요" 커스텀 404 페이지
- [x] `app/models.py` — `Bakery`에 `flavor_profile` 필드 추가
- [x] `app/data.py` — 8개 베이커리에 맛 프로필 텍스트 추가
- [x] `app/main.py` — 랜덤 초대 메시지 풀 (5개), 404 핸들러
- [x] `static/style.css` — welcome, guide, flavor-profile, invitation, 404, footer 스타일

현재 상태: **완료**

---

## 남은 작업

### Phase 8. API 계층에 새 필터 반영

> 테스트: `tests/test_api.py` (TDD)

- [x] `RecommendRequest`에 `parking`, `custom_order`, `max_distance` 필드 추가
- [x] `routers/recommend.py`에서 새 파라미터를 `recommend()`에 전달
- [x] HTML POST `/recommend` 라우트에서도 새 폼 필드 처리
- [x] 새 필터 파라미터 API 통합 테스트 추가 (parking, custom_order, max_distance, 복합 필터)

현재 상태: **완료**

---

### Phase 9. 프론트엔드 — 새 필터 폼 + 결과 보강

> 파일: `templates/index.html`, `templates/results.html`

- [x] `index.html` 폼에 주차/주문제작 체크박스 추가 (외계인 친화 설명 포함)
- [x] `index.html` 폼에 문정역 거리 셀렉트 추가 (300m/500m/1km/2km)
- [x] `results.html`에 주차/주문제작/거리 정보 표시

현재 상태: **완료**

---

### Phase 10. 감각 기반 추천 (PRD FR-6)

> "감각으로 찾기" — 지구의 오감에 익숙하지 않은 사용자를 위한 대안 추천 경로

- [x] `app/sensory.py` — 매핑 로직: (식감×맛→purpose, 분위기→mood)
- [x] `templates/sensory.html` — 3단계 이진 질문 UI (라디오 버튼 + 감각 설명)
- [x] `app/main.py` — GET `/sensory`, POST `/sensory` 라우트 추가
- [x] `index.html`에 "감각으로 찾기" 링크 추가
- [x] `tests/test_sensory.py` — 매핑 로직 단위 테스트 7개
- [x] `tests/test_api.py` — 감각 페이지 통합 테스트 3개

매핑 규칙:

| 식감 | 맛 | → purpose |
|------|-----|-----------|
| 바삭 | 달콤 | 빵구경 |
| 바삭 | 고소 | 브런치 |
| 부드러움 | 달콤 | 케이크 |
| 부드러움 | 고소 | 브런치 |

| 분위기 | → mood |
|--------|--------|
| 혼자 | 아늑한 |
| 여럿 | 편안한 |

현재 상태: **완료**

---

### Phase 11. 시드 데이터 보강

> 파일: `app/data.py`

- [x] 리뷰 3개 → 5개로 증가 (전 베이커리)
- [x] 미사용 태그 **마카롱맛집** 활성화 (3곳)
- [x] **줄서는집** 1곳 → 5곳, **브런치맛집** 1곳 → 5곳으로 분포 개선
- [x] 8개 태그 전부 활성화, 최소 2곳 이상 분포

보강 후 태그 분포:

| 태그 | 보강 전 | 보강 후 |
|------|:------:|:------:|
| 빵맛집 | 6 | 6 |
| 브런치맛집 | 1 | 5 |
| 줄서는집 | 1 | 5 |
| 선물하기좋은 | 3 | 4 |
| 마카롱맛집 | 0 | 3 |
| 가성비좋은 | 2 | 3 |
| 아늑한 | 2 | 3 |
| 케이크맛집 | 2 | 2 |

- [ ] 8개 베이커리 `distance` 실제 값 확인 (카카오맵 기준) — Phase 12에서 처리

현재 상태: **완료**

---

### Phase 12. 실제 베이커리 데이터 수집 (카카오맵 API)

> 하드코딩 시드 데이터 → 실제 문정동 베이커리 데이터로 교체

1. [x] https://developers.kakao.com 에서 앱 등록 + **REST API 키** 발급
2. [x] 카카오 로컬 API로 "문정동 베이커리/빵집" 검색 → 이름/주소/좌표 수집 (`scripts/fetch_bakeries.py`)
3. [x] 좌표로 문정역(37.4858, 127.1225) 기준 거리(km) 계산 (haversine 공식)
4. [x] 수집된 49곳 중 10곳 선정, 리뷰 5개씩 작성 (8개 태그 전부 활성화)
5. [x] 수집 데이터를 `app/data.py` 형식으로 변환 — 74개 테스트 전부 통과

수집 결과:

| # | 이름 | 거리 | 가격대 | 주차 | 주문제작 |
|---|------|:----:|:----:|:----:|:------:|
| 1 | 더 브레드 레지던스 | 0.16km | 중가 | X | X |
| 2 | 오밀조밀베이크샵 | 0.23km | 중가 | X | X |
| 3 | 주빌리꽃케이크 | 0.28km | 고가 | X | O |
| 4 | 그루메 | 0.29km | 고가 | X | X |
| 5 | 그라동빵집 | 0.37km | 저가 | X | X |
| 6 | 파리바게뜨 문정중앙점 | 0.37km | 중가 | O | X |
| 7 | 8084제빵소 | 0.37km | 고가 | X | X |
| 8 | 엘모리아케이크 | 0.34km | 고가 | O | O |
| 9 | 뚜레쥬르 카페송파파크하비오점 | 0.51km | 중가 | O | O |
| 10 | 삼송빵집 현대시티몰가든파이브점 | 0.85km | 중가 | O | X |

태그 분포:

| 태그 | 분포 |
|------|:----:|
| 빵맛집 | 8 |
| 브런치맛집 | 7 |
| 선물하기좋은 | 6 |
| 줄서는집 | 5 |
| 가성비좋은 | 4 |
| 아늑한 | 3 |
| 케이크맛집 | 3 |
| 마카롱맛집 | 3 |

현재 상태: **완료**

---

### Phase 13. 카카오맵 지도 연동

> 테스트: `tests/test_api.py::TestHTMLPages::test_results_has_map`, `tests/test_data.py`

- [x] `Bakery` 모델에 `lat`, `lon` 좌표 필드 추가
- [x] 10개 베이커리에 카카오맵 API 좌표 데이터 반영
- [x] `results.html`에 카카오맵 JS SDK 지도 삽입 (추천 결과 + 문정역 마커)
- [x] `.env`에 `KAKAO_JS_KEY` 추가, `main.py`에서 `dotenv` 로딩
- [x] 데이터 무결성 테스트 추가 (`tests/test_data.py` — 좌표, 리뷰, 태그, ID 유일성)
- [x] 82개 테스트 전부 통과

현재 상태: **완료**

---

### Phase 14. 공공데이터 연동

> 파일: `app/data.py`, `scripts/fetch_public_data.py`, `tests/test_data.py`

- [x] 서울 열린데이터광장 API 수집 스크립트 (`scripts/fetch_public_data.py`)
- [x] 실제 데이터 수집: 문정동 제과점 413곳 → 빵집 키워드 필터 → 6곳 병합
- [x] TM 좌표(EPSG:2097) → WGS84 변환 (`_tm_to_wgs84()`)
- [x] 사업장명 기반 빵집 키워드 필터 (편의점·카페·PC방 등 제외)
- [x] 도로명 주소 우선 사용 + 문정역 거리 자동 계산
- [x] 카카오 10곳 + 공공 6곳 = 16곳 통합, 92개 테스트 통과

현재 상태: **완료**

---

### Phase 15. UI 디자인 대폭 개편

> 참고: Mah-Ze-Dahr Bakery (Awwwards) 스타일 지향

- [x] 따뜻한 앰버/크러스트 색상 팔레트로 전환 (`--cream`, `--ink`, `--amber`, `--crust` 등 CSS 변수)
- [x] 히어로 섹션: 파비콘 이미지 + 라디알 그래디언트 별 배경 + 앰버 디바이더
- [x] 폼 UI: 분위기/목적/가격대를 `<select>` → 칩(배지) 라디오 그룹으로 변경 (이모지 아이콘 포함)
- [x] 감각 페이지: 커스텀 라디오 버튼 (앰버 하이라이트, `:has(input:checked)` 활용)
- [x] 결과 페이지: 2컬럼 그리드 레이아웃 (왼쪽 sticky 지도 + 오른쪽 카드 리스트)
- [x] 카드 호버 ↔ 지도 마커 인포윈도우 연동
- [x] 푸터 강화: "We Are The Universe." 인용구 + 정보 라인
- [x] 파비콘 생성 (32×32 PNG, 빵 이미지)
- [x] 지구 음식 가이드를 폼 위로 재배치
- [x] 문정역 좌표 보정: (127.1264, 37.4857) → (127.1225, 37.4858)
- [x] 카카오맵 SDK URL https 프로토콜 적용

현재 상태: **완료**

---

### 선택 (향후 확장)

- [ ] SQLite + SQLAlchemy로 데이터 영속화
- [ ] 베이커리 상세 페이지 (`/bakery/{id}`)
- [ ] 사용자 리뷰 등록 기능 → tags 실시간 재계산
- [ ] 키워드 가중치 도입 (빈도 기반 태그 신뢰도)
- [ ] 테스트 커버리지 측정 (`pytest-cov`)
- [ ] 지구 초보 모드 토글 (JS) — 활성화 시 모든 용어에 부가 설명 표시 (PRD FR-5.4)
- [ ] 다국어/다종족 지원 — 영어 UI 옵션
