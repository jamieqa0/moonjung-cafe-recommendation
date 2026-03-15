# 문빵 스테이션 — 개발 계획

> **We Are The Universe** — 우주 어디서든 환영합니다.

---

## 개요

문정동 베이커리 추천 웹 서비스. 분위기·목적·가격대 조건으로 **TOP 3 베이커리**를 추천한다.

| 항목 | 내용 |
|------|------|
| 기술 스택 | Python 3.11, FastAPI, Jinja2, pytest (TDD) |
| 데이터 | 인메모리 시드 데이터 10곳 (카카오맵 API 기반) |
| 배포 | Render (무료 티어) |
| GitHub | https://github.com/jamieqa0/moonbbang-station |

```bash
pip install -r requirements.txt          # 의존성 설치
uvicorn app.main:app --reload            # 개발 서버 (http://localhost:8000)
python -m pytest tests/ -v               # 테스트 실행
```

---

## 완료된 단계

### Phase 1~3. 핵심 엔진

데이터 모델, 리뷰 분석, 추천 로직의 기반을 TDD로 구축.

| Phase | 내용 | 테스트 |
|:-----:|------|--------|
| 1 | **데이터 모델** — Bakery, RecommendRequest, RecommendResponse (Pydantic) | `test_models.py` |
| 2 | **리뷰 태그 추출** — 8종 키워드-태그 매핑 (`extract_tags()`) | `test_review_analyzer.py` |
| 3 | **추천 로직** — 필터링(주차/주문제작/거리) → 점수 계산 → TOP 3 반환 | `test_recommender.py` |

점수 계산 공식:

```
score = (mood 일치 +2) + (purpose 일치 +2) + (price_range 일치 +1)
      + (거리 보너스 × 3) + (랜덤 다양화 0~1.5)
```

---

### Phase 4~6. 서비스 골격

시드 데이터, API, 프론트엔드를 연결하여 동작하는 웹 서비스 완성.

| Phase | 내용 | 테스트 |
|:-----:|------|--------|
| 4 | **시드 데이터** — 문정동 베이커리 8곳 하드코딩, 앱 시작 시 태그 자동 생성 | — |
| 5 | **API** — `GET /api/bakeries`, `GET /api/bakeries/{id}`, `POST /api/recommend` | `test_api.py` |
| 6 | **프론트엔드** — `index.html` (조건 선택 폼), `results.html` (카드 리스트) | `test_api.py` |

---

### Phase 7~9. We Are The Universe

외계인 친화 콘셉트 적용 + 추가 필터 기능.

| Phase | 내용 |
|:-----:|------|
| 7 | **톤 전환** — 환영 메시지, 지구 음식 가이드, 맛 프로필, 랜덤 초대 메시지, 커스텀 404 |
| 8 | **필터 확장** — RecommendRequest에 parking/custom_order/max_distance 추가, API·HTML 반영 |
| 9 | **폼 보강** — 주차/주문제작 체크박스, 거리 셀렉트(300m~2km), 결과 카드에 정보 표시 |

---

### Phase 10. 감각 기반 추천

지구의 오감에 익숙하지 않은 사용자를 위한 대안 추천 경로.

- `GET /sensory`, `POST /sensory` 라우트
- 3단계 이진 질문: 식감(바삭/부드러움) → 맛(달콤/고소) → 분위기(혼자/여럿)
- 결과를 mood/purpose로 변환하여 기존 추천 로직에 전달

| 테스트 | 내용 |
|--------|------|
| `test_sensory.py` | 매핑 로직 단위 테스트 7개 |
| `test_api.py` | 감각 페이지 통합 테스트 3개 |

---

### Phase 11~12. 데이터 고도화

하드코딩 → 실제 문정동 베이커리 데이터로 교체.

| Phase | 내용 |
|:-----:|------|
| 11 | **리뷰 보강** — 리뷰 3→5개, 8개 태그 전부 활성화, 최소 2곳 이상 분포 |
| 12 | **카카오맵 API 수집** — 49곳 검색 → 10곳 선정, haversine 거리 계산, 리뷰 5개씩 작성 |

현재 시드 데이터 (10곳):

| # | 이름 | 거리 | 가격대 | 주차 | 주문제작 |
|---|------|:----:|:----:|:----:|:------:|
| 1 | 더 브레드 레지던스 | 0.16km | 일반 | — | — |
| 2 | 오밀조밀베이크샵 | 0.23km | 일반 | — | — |
| 3 | 주빌리꽃케이크 | 0.28km | 프리미엄 | — | O |
| 4 | 그루메 | 0.29km | 프리미엄 | — | — |
| 5 | 그라동빵집 | 0.37km | 일반 | — | — |
| 6 | 파리바게뜨 문정중앙점 | 0.37km | 일반 | O | — |
| 7 | 8084제빵소 | 0.37km | 프리미엄 | — | — |
| 8 | 엘모리아케이크 | 0.34km | 프리미엄 | O | O |
| 9 | 뚜레쥬르 카페송파파크하비오점 | 0.51km | 일반 | O | O |
| 10 | 삼송빵집 현대시티몰가든파이브점 | 0.85km | 일반 | O | — |

---

### Phase 13~14. 외부 데이터 연동

| Phase | 내용 |
|:-----:|------|
| 13 | **카카오맵 지도** — Bakery에 lat/lon 추가, results.html에 JS SDK 지도 삽입, 마커+인포윈도우 |
| 14 | **공공데이터** — 서울 열린데이터광장 API 수집(413곳→15곳 필터), TM→WGS84 변환. 강화된 필터로 서비스 활성화 |

---

### Phase 15. UI 디자인 개편

Mah-Ze-Dahr Bakery (Awwwards) 스타일 지향.

- 앰버/크러스트 색상 팔레트 (`--cream`, `--ink`, `--amber`, `--crust`)
- 칩(Chip) 기반 라디오 그룹으로 폼 UI 전환
- 결과 페이지: 2컬럼 그리드 (sticky 지도 + 카드 리스트), 카드 호버↔마커 연동
- 카와이 스타일 SVG 아이콘·일러스트 세트
- tsparticles 별 파티클 배경

---

### Phase 16. 디자인 깊이감 개선

CSS-only 변경으로 플랫한 디자인에 깊이감, 인터랙션, 시각적 완성도 추가.

- **엘리베이션 시스템** — `--shadow-sm/md/lg/glow`, `--radius-sm/md`, `--transition-spring` 변수 도입
- **카드 리디자인** — 기본 그림자 + 호버 시 `translateY(-4px)` + `shadow-lg`, 좌측 바 항상 표시(호버 시 amber), 일러스트 72→96px + 호버 스케일, CSS counter 번호 배지, 태그 호버 효과
- **버튼 & 칩** — active 눌림 효과, focus-visible 아웃라인(접근성), 칩 선택 시 `scale(1.03)` + 스프링 이징
- **폼/섹션 깊이감** — recommend-form, sensory-form, intro-welcome에 `shadow-md`, details open 시 그림자 전환
- **배경 텍스처** — body에 미세한 radial-gradient 오버레이
- **헤더/푸터** — 헤더 상단 amber 그라데이션, 푸터 가운데서 퍼지는 amber 라인 애니메이션
- **상세 페이지** — 일러스트 80→100px, 리뷰 호버 시 좌측 amber 바 + 인덴트
- **cardSlideIn 애니메이션** — scale(0.98)→1 등장 효과
- **초대 메시지** — 그라데이션 배경 강화 + 장식용 큰따옴표

---

### Phase 17. 카카오 지도 커스터마이징

지도 UI를 사이트 디자인 톤에 맞춰 전면 개편.

- **커스텀 마커** — SVG data URI 마커 (앰버 핀 + 넘버링). 문정역 마커 별도 디자인 (다크 잉크 핀)
- **CustomOverlay 카드** — 기본 InfoWindow 대신 사이트 스타일의 카드형 오버레이. 닫기 버튼 + 마커 클릭/카드 호버 연동
- **지도 색감 오버레이** — `mix-blend-mode: multiply` 틴트 + 비네팅으로 따뜻한 브라운 톤 적용
- **detail.html 동일 적용** — 상세 페이지 지도에도 커스텀 마커·오버레이·틴트 통일

---

### Phase 18. 타이포그래피 Spacing 시스템

페이지 간 텍스트 간격 불일치 해소. 4px 기반 spacing 스케일 도입.
1
**문제**: line-height 7종, heading margin 4종, paragraph margin 6종+, gap 9종 — 체계 없이 ad-hoc 값 사용

**도입된 CSS 변수**:

| 변수 | 값 | 용도 |
|------|-----|------|
| `--leading-tight` | 1.3 | 제목, 카드 타이틀, 라벨 |
| `--leading-normal` | 1.6 | 본문, 설명 텍스트 |
| `--leading-relaxed` | 1.8 | 긴 산문, 인트로 |
| `--space-1` | 0.25rem | 미세 간격 (리스트 아이템, 태그 gap) |
| `--space-2` | 0.5rem | heading margin-bottom, 아이콘-텍스트 gap |
| `--space-3` | 0.75rem | 단락 간격, 카드 내부 요소 |
| `--space-4` | 1rem | 섹션 내부, 카드 패딩(세로) |
| `--space-5` | 1.5rem | 섹션 간, 카드 패딩(가로), 폼 필드 라벨 |
| `--space-6` | 2rem | 레이아웃 gap, 폼 패딩, 주요 섹션 간격 |
| `--space-8` | 3rem | 히어로 패딩 |
| `--space-10` | 4rem | 페이지 단위 여백 (footer, hero) |

**적용 규칙**:

- body `line-height: --leading-normal` (1.6)
- 모든 heading(h1~h4): `line-height: --leading-tight`, `margin-bottom: --space-2`
- 카드 내부 p: `margin: --space-1 0`, `line-height: --leading-normal`
- 카드 패딩: `--space-4 --space-5` (세로 가로)
- 인라인 스타일 → `.map-fallback` CSS 클래스 전환

---

## 향후 작업

> 우선순위: 🔴 높음 → 🟡 중간 → 🟢 낮음

### 🔴 최종점검 (배포 전 필수)

- [x] ~~웹 반응형 확인~~ — 5개 수정: no-map 레이아웃 버그, nav wrap, address overflow, 전체빵집 heading·정렬
- [ ] 크리티컬 오류 수정 — 500 에러, 렌더링 깨짐 등
- [ ] TDD 커버리지 유지 — 신규 기능 테스트 작성 여부 확인

### 🟡 기능 확장 (PRD 명세 미완료)
- [x] ~~결과 빵집 카드 extra-info~~ — 가격대·거리 한 줄 표시 + 주차가능/불가/주문제작가능 인라인 태그. 주문제작 불가는 미표시
- [x] ~~대표 메뉴 괄호 제거~~ — `strip_parens` Jinja2 필터로 `(HOT)`, `(시즌)` 등 괄호 내용 제거. results/bakeries/detail 전체 적용
- [x] 카카오지도에서 말풍선에서 - overlay-menu는 안보여도 돼. 가게이름만 노출되게 해줘
- [x] ~~빵집 이미지가 빵집과 관련없는 이미지가 나오는 문제가 해결안됨~~ → Playwright 수집 `kakao_details.json`의 `photo_url`(카카오맵 공식 og:image)로 전면 교체. 시드 1~10번 포함 전체 적용. 이미지 검색 API 폴백으로만 사용
- [x] ~~시드 데이터(1~10번)는 전부 정확한 값이라도 한다. 근데, 카카오 API 추가분(100번대)에서 정확하지 않은 값이 있음, 대표 메뉴: 대표 빵으로 나오는 등-전수 확인 필요~~ → `_infer_attributes()` 리팩터: 이름 직접 포함 시만 메뉴 추론, 프랜차이즈·기본값 "다양한 빵"으로 통일, 한스/외계인방앗간 오류 수정. Playwright로 `kakao_details.json` 수집(49곳 메뉴 42개·후기 42개·영업시간 38개), `hours` 모델 필드 추가, 실제 데이터 우선 적용
- [x] ~~문정동 전체 빵집을 볼수 있는 페이지 요청~~ → `GET /bakeries` 추가, 거리순 그리드, 네이버·카카오 링크 포함
- [ ] **빵집 기억해두기** — 결과 페이지에서 즐겨찾기 기능 (PRD US-6)
- [ ] **지구 초보 모드 토글** — 활성화 시 모든 용어에 부가 설명 표시 (PRD FR-5.4)
- [ ] **사용자 리뷰 등록** → 태그 실시간 재계산

### 🟢 기술 개선 (기술 부채)

- [ ] SQLite + SQLAlchemy로 데이터 영속화
- [ ] 다국어/다종족 지원 — 영어 UI 옵션

#### 리뷰 태그 추출 개선 (`review_analyzer.py`)

- [x] ~~**키워드 빈도 가중치 도입**~~ — 리뷰별 개별 카운팅. 리뷰 3개 이상인 빵집은 `min_reviews=2` 적용 (2개 이상 리뷰에 등장해야 태그 생성)
- [x] ~~**형태소 분석기 연동**~~ — kiwipiepy 연동. 원본 텍스트 OR 형태소 분리 텍스트 양쪽 검색. Windows 한글 경로 이슈(`C:/kiwi_model` 복사 우회, `KIWI_MODEL_PATH` 환경변수 지원)
- [ ] **키워드 관리 자동화** — 신규 메뉴·신조어 등장 시 수동 추가 의존. 리뷰 빈출 단어 추출로 키워드 후보 자동 제안

#### 감각 기반 추천 개선 (`sensory.py`)

- [x] ~~**매핑 표현력 확장**~~ — `(바삭, 고소)` → `식사빵`으로 변경 (기존 브런치와 분리). `(부드러움, 고소)` → `브런치` 유지
- [x] ~~**mood 커버리지 확대**~~ — `모던한`, `감성적인`은 감각 폼과 결이 맞지 않음(카테고리 개념). 조건으로 찾기(index.html)의 분위기 칩에서 이미 선택 가능하므로 감각 폼은 혼자/여럿 2개 유지
- [x] ~~**기본값 고정 개선**~~ — 미매칭 시 `None` 반환으로 변경. recommend()에서 None = 필터 미적용으로 자연스럽게 처리

#### 검색 조건 구조 재편

- [x] ~~**`빵구경` 완전 제거**~~ — 모든 빵집이 빵구경 대상이므로 구별력 없음. purpose 칩·시드 데이터·`_infer_attributes()`·sensory 매핑 전체에서 제거
- [x] ~~**`동네 단골`·`대형빵집`을 purpose → mood로 이동**~~ — 이 두 값은 방문 목적이 아닌 빵집의 분위기·규모 속성. index.html 분위기 칩으로 이동. 시드 데이터·`_infer_attributes()`·`review_analyzer._PURPOSE_TAG_MAP`→`_MOOD_TAG_MAP`·`sensory` 전체 반영

---

### Phase 19. 공공데이터 품질 고도화 + 네이버 스크래핑

공공데이터 필터링 강화 및 네이버 맵 상세 정보 통합.

| 작업 | 내용 |
|------|------|
| **공공데이터 필터 강화** | `fetch_seoul_bakeries.py`: 위생업태명 블랙리스트(편의점·패스트푸드·백화점 등) + 상호명 블랙리스트(편의점 브랜드·비빵집 업종) + 빵집 이름 양성 키워드 필터 3단계 적용. 413곳 → 15곳으로 신뢰성 확보. 추가 키워드: 베이글·카롱·프레즐·빌리엔젤 |
| **네이버 스크래퍼 추가** | `scripts/scrape_naver_details.py` 신규: Playwright로 네이버 통합검색(`search.naver.com`) → `/p/entry/place/{id}` 추출 → 상세 페이지 수집 (og:image, `.A_cdD` 영업시간, `div.pui__vn15t2` 방문자 리뷰, `.GXS1X` 메뉴). 15개 중 10개 수집 성공. 출력: `data/naver_details.json` |
| **공공데이터 서비스 활성화** | `data.py`: `_load_naver_details()` 추가, `_load_public_bakeries()` 강화된 필터 + 네이버 데이터 통합으로 실제 사진·메뉴·리뷰 보강. 전체 빵집 수 60개 |

**데이터 수집 순서 (공공데이터 경로)**:
```
fetch_seoul_bakeries.py → data/public_bakeries.csv
scrape_naver_details.py → data/naver_details.json
(자동) data.py _load_public_bakeries() → BAKERIES 통합
```

---

### 완료 내역 (기능 확장)

- [x] ~~평점이 실제 데이터와 안맞음~~ → 평점 필드 제거 (정확하지 않아 추천 점수·UI에서 제외)
- [x] ~~**분위기 툴팁**~~ — 칩 호버 시 감각적 설명 툴팁 표시 (PRD FR-5.2)
- [x] ~~**빵목적 툴팁**~~ — 칩 호버 시 감각적 설명 툴팁 표시
- [x] ~~**"잘 모르겠어요" 옵션**~~ — 기본 옵션을 "무엇이든지" / "어디든지"로 변경 (PRD FR-5.5)
- [x] ~~베이커리 상세 페이지 (`/bakery/{id}`)~~ — 상세 페이지 추가, 결과 카드에서 링크 연결
- [x] ~~**베이커리 이미지**~~ — `photo_url` 필드 추가, 카카오 이미지 검색 API 스크립트(`scripts/fetch_bakery_photos.py`)로 수집, `data/kakao_photos.json`에 저장. 사진 있으면 표시, 없으면 SVG 일러스트 폴백
- [x] ~~**디자인 밋밋**~~ — Phase 16에서 엘리베이션·인터랙션·텍스처 개선 완료
- [x] ~~**폰트일관성**~~ — 8단계 타입 스케일(--text-xs~3xl) 정의, 23종 font-size를 CSS 변수로 통일
- [x] ~~**베이커리 이미지 개선**~~ — 전체 52곳 대상으로 확대 (기존 시드 10곳만 수집 → 전체). 스크립트 검증 강화(스티커/지도이미지/깨진URL 필터링), 검색어 다양화, `referrerpolicy="no-referrer"` 핫링크 차단 우회. 사진 없는 곳은 SVG 일러스트 자동 폴백. 최종 30/52곳 실사진 적용
- [x] ~~**베이커리 이미지 필터링**~~ — Pillow 기반 따뜻한 색조 분석(`_has_warm_tones()`). 이미지를 80×80 축소 후 RGB→HSV 변환, Hue 0~50° (빨강~주황~노랑) 비율이 15% 이상이면 통과. 저채도 크림/베이지 톤도 별도 판별. 기존 30장 중 25장 통과, 5장 필터링. `scripts/fetch_bakery_photos.py`에 통합
- [x] ~~결과 페이지에서 제목 선택하면 상세페이지로 가는데 정보가 크게 다르지않아서 개선 필요~~ → 상호명 링크 제거, 네이버 검색 N 버튼으로 대체
- [x] ~~**태그 일관성**~~ — 리뷰 없는 빵집(카카오 API 추가분)에 태그가 비어있던 문제. `generate_fallback_tags()` 함수 추가: mood/purpose에서 자동 태그 생성. 테스트 6개 추가
- [x] ~~**카카오 지도** 디자인이 어울리지않음~~ → Phase 17에서 커스텀 마커·오버레이·색감 오버레이 적용

### 완료 내역 (기술 개선)

- [x] ~~테스트 커버리지 측정 (`pytest-cov`)~~ — 94% 커버리지 달성, requirements.txt에 추가

### 버그 리포트

- 추가예정
