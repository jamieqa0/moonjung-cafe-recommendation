# Maintenance Guide - Bakery Data

이 가이드는 베이커리 데이터(메뉴, 후기, 영업시간, 사진 등)를 최신 상태로 유지하는 방법을 설명합니다.

---

## 1. 시드 데이터 수동 수정 (id 1~10)

핵심 10개 베이커리는 `app/data.py`의 `_RAW_BAKERIES` 리스트에 하드코딩되어 있습니다.

```python
# app/data.py → _RAW_BAKERIES
{
    "id": 1,
    "name": "더 브레드 레지던스",
    "kakao_id": "1234567",   # 카카오 플레이스 ID
    ...
}
```

- `kakao_id`를 올바르게 유지하면, 아래 Playwright 수집 시 자동으로 사진·메뉴·후기가 덮어씌워집니다.

---

## 2. 카카오 수집 데이터 갱신 (id 11+)

`data/kakao_bakeries.json` — 카카오맵 API로 수집한 베이커리 목록 (kakao_id 포함).

갱신 방법:
```bash
python scripts/fetch_kakao_bakeries.py   # KAKAO_REST_API_KEY 필요
# 이후 반드시 scrape_kakao_details.py 도 재실행해야 details 데이터가 갱신됨
python scripts/scrape_kakao_details.py
```

---

## 3. 상세 데이터 재수집 (메뉴 · 후기 · 영업시간 · 사진)

`data/kakao_details.json` — Playwright로 수집한 실제 데이터.

```bash
# playwright 브라우저 초기 설치 (최초 1회)
playwright install chromium

# 재수집 실행 (~2분, headless Chromium)
python scripts/scrape_kakao_details.py
```

- 입력: `data/kakao_bakeries.json`
- 출력: `data/kakao_details.json` (덮어쓰기)
- 수집 항목: 메뉴(`.list_goods`), 후기(`.desc_review`), 영업시간(`.info_runtime`), 사진(`og:image`)
- 사진 URL은 `img1.kakaocdn.net/cthumb/local/` (카카오맵 공식 CDN) — 이미지 검색 결과와 달리 안정적

앱은 재시작 시 자동으로 새 JSON을 로딩합니다 (`_load_place_details()`).

---

## 4. 공공데이터 CSV

`data/public_bakeries.csv` — 서울 열린데이터광장 데이터.

현재 **비활성화** 상태 (데이터 품질 문제: 편의점·PC방 등 비빵집 다수 포함). 코드(`_load_public_bakeries`)는 잔존. 재활성화 시 `app/data.py`에서 `BAKERIES` 빌드 로직 수정 필요.

---

## 5. 런타임 데이터 흐름

```
data/kakao_bakeries.json ──→ _load_kakao_bakeries()
data/kakao_details.json ──→ _load_place_details()   ← Playwright 수집 결과
                              │
                              ▼ 메뉴·후기·영업시간·photo_url 병합
                              ↓
app/data.py → BAKERIES 리스트 (인메모리)
```
