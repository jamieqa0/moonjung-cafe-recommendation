"""
Playwright로 네이버 지도 장소 상세 정보 스크래핑.
입력: data/public_bakeries.csv (fetch_seoul_bakeries.py 실행 결과)
출력: data/naver_details.json (메뉴, 후기, 영업시간, 사진 URL)

수집 항목 (kakao_details.json 과 동일 구조):
  name        상호명
  naver_id    네이버 장소 ID
  photo_url   대표 사진 URL (og:image)
  hours       영업시간 텍스트
  menus       메뉴 리스트
  reviews     방문자 리뷰 리스트

검색 흐름:
  1. search.naver.com/search.naver?query={name}+문정동 에서 /p/entry/place/{id} 링크 추출
  2. m.place.naver.com/place/{id}/home        → og:image, 영업시간
  3. m.place.naver.com/place/{id}/review/visitor → 방문자 리뷰
  4. m.place.naver.com/place/{id}/menu           → 메뉴

확인된 CSS 셀렉터 (2026-03 기준):
  영업시간:  .A_cdD
  리뷰:      div.pui__vn15t2
  메뉴:      .GXS1X 가 포함된 li (li.innerText.split('\\n')[0] 이 메뉴명)
"""

import asyncio
import csv
import json
import random
import re
import sys
from pathlib import Path
from urllib.parse import quote

from playwright.async_api import async_playwright

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).parent.parent
INPUT_CSV = ROOT / "data" / "public_bakeries.csv"
OUTPUT = ROOT / "data" / "naver_details.json"

DESKTOP_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/122.0.0.0 Safari/537.36"
)

# ── 필터링 상수 (fetch_seoul_bakeries.py 와 동일) ──────────────────────────────
EXCLUDE_BIZ_TYPES = {
    "편의점", "패스트푸드", "백화점", "키즈카페", "다방",
    "아이스크림", "일반조리판매", "탁주/약주", "주점",
}
BLACKLIST_NAME_KEYWORDS = [
    "세븐일레븐", "GS25", "CU편의점", "이마트24", "미니스톱",
    "스타벅스", "롯데리아", "맥도날드", "버거킹", "KFC", "서브웨이",
    "이디야", "메가커피", "메가엠지씨", "빽다방", "공차", "투썸플레이스",
    "할리스", "탐앤탐스", "엔제리너스", "커피빈",
    "편의점", "PC방", "마트", "슈퍼", "영화관", "노래방",
    "김밥", "떡볶이", "스시", "초밥", "피자", "치킨", "국밥",
    "삼겹살", "갈비", "분식", "냉면", "설렁탕", "곱창", "순대",
    "족발", "라면", "얌차",
]
BAKERY_NAME_KEYWORDS = [
    "빵", "베이커리", "베이크", "제과", "케이크", "크루아상",
    "스콘", "파티세리", "제빵", "쿠키", "마카롱", "카롱", "타르트",
    "도넛", "와플", "브레드", "bread", "bakery", "bake", "cake",
    "쇼콜라", "파운드", "포카치아", "바게트", "소금빵", "앙버터",
    "치아바타", "머핀", "카눌레", "피낭시에", "휘낭시에",
    "갈레트", "크레이프", "페이스트리",
    "베이글", "프레즐", "프리즐", "bagel", "pretzel",
    "빌리엔젤",  # 생크림빵 전문 체인
]


def _is_bakery(name: str, biz_type: str) -> bool:
    nl = name.lower()
    if biz_type in EXCLUDE_BIZ_TYPES:
        return False
    if any(kw.lower() in nl for kw in BLACKLIST_NAME_KEYWORDS):
        return False
    return any(kw.lower() in nl for kw in BAKERY_NAME_KEYWORDS)


def load_candidates() -> list[dict]:
    """CSV에서 필터링된 빵집 후보를 로드한다."""
    if not INPUT_CSV.exists():
        print(f"CSV 없음: {INPUT_CSV}")
        print("먼저 scripts/fetch_seoul_bakeries.py를 실행하세요.")
        return []

    candidates = []
    seen_names: set[str] = set()
    try:
        with open(INPUT_CSV, encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                name = row.get("사업장명", "").strip()
                biz_type = row.get("위생업태명", "").strip()
                addr = (row.get("도로명전체주소") or row.get("소재지전체주소", "")).strip()
                if not name or name in seen_names:
                    continue
                if _is_bakery(name, biz_type):
                    candidates.append({"name": name, "address": addr})
                    seen_names.add(name)
    except Exception as e:
        print(f"CSV 읽기 오류: {e}")
    return candidates


def _clean_search_name(name: str) -> str:
    """검색 정확도를 높이기 위해 상호명을 정제한다.
    - 괄호 안 영문 제거: '꾸미케이크 KKUMI CAKE' → '꾸미케이크'
    - 점포 구분자 이후 제거: '루시카토 베이크 카페 NC송파가든파이브점' → '루시카토 베이크 카페'
    - 단독 영문 단어 제거
    """
    # 괄호 안 내용 제거
    cleaned = re.sub(r"\s*[\(\[（][^\)\]）]*[\)\]）]", "", name).strip()
    # 점포명 제거 (NC, 가든파이브, 현대시티몰 등)
    cleaned = re.sub(r"\s+(NC|현대|가든파이브|아울렛|백화점|몰|마트|파크|타운|센터|타워|빌딩|지식산업|법조)\S*.*$",
                     "", cleaned).strip()
    # 연속된 영문 단어만 제거 (한글 유지)
    words = cleaned.split()
    korean_words = [w for w in words if re.search(r"[가-힣]", w)]
    if korean_words:
        cleaned = " ".join(korean_words)
    return cleaned or name


async def search_naver_id(page, name: str) -> str | None:
    """네이버 통합검색에서 장소 ID를 추출한다. 실패 시 정제된 이름으로 재시도한다."""
    search_queries = [name]
    cleaned = _clean_search_name(name)
    if cleaned != name:
        search_queries.append(cleaned)

    for query_name in search_queries:
        query = quote(f"{query_name} 문정동")
        url = f"https://search.naver.com/search.naver?where=nexearch&query={query}"
        try:
            await page.goto(url, wait_until="networkidle", timeout=20000)
            await page.wait_for_timeout(1500)

            hrefs = await page.evaluate("""() =>
                Array.from(document.querySelectorAll('a[href*="/p/entry/place/"]'))
                    .map(a => a.href)
            """)
            for href in hrefs:
                m = re.search(r"/p/entry/place/(\d+)", href)
                if m:
                    return m.group(1)
        except Exception as e:
            print(f"  검색 오류 ({query_name}): {e}", flush=True)

    return None


async def fetch_detail(page, naver_id: str, name: str) -> dict:
    """네이버 장소 상세 페이지에서 정보를 수집한다."""
    result = {
        "name": name,
        "naver_id": naver_id,
        "photo_url": None,
        "hours": None,
        "menus": [],
        "reviews": [],
    }
    base = f"https://m.place.naver.com/place/{naver_id}"

    # ── 홈: og:image + 영업시간 ─────────────────────────────────────────────
    try:
        await page.goto(f"{base}/home", wait_until="networkidle", timeout=20000)
        await page.wait_for_timeout(2000)

        og = await page.query_selector('meta[property="og:image"]')
        if og:
            result["photo_url"] = await og.get_attribute("content")

        hours_el = await page.query_selector(".A_cdD")
        if hours_el:
            result["hours"] = (await hours_el.inner_text()).strip()[:200]

    except Exception as e:
        print(f"  홈 오류 ({name}): {e}", flush=True)

    # ── 리뷰: 방문자 리뷰 ────────────────────────────────────────────────────
    try:
        await page.goto(f"{base}/review/visitor", wait_until="networkidle", timeout=15000)
        await page.wait_for_timeout(2000)

        items = await page.query_selector_all("div.pui__vn15t2")
        for item in items[:5]:
            text = (await item.inner_text()).strip().replace(" 더보기", "")
            if len(text) > 10:
                result["reviews"].append(text[:150])
    except Exception:
        pass

    # ── 메뉴 ─────────────────────────────────────────────────────────────────
    try:
        await page.goto(f"{base}/menu", wait_until="networkidle", timeout=15000)
        await page.wait_for_timeout(2000)

        # .GXS1X(가격)가 포함된 li의 첫 줄 = 메뉴명
        menu_texts = await page.evaluate("""() => {
            const items = document.querySelectorAll('li');
            const results = [];
            for (const li of items) {
                if (li.querySelector('.GXS1X')) {
                    const name = li.innerText.trim().split('\\n')[0].trim();
                    if (name && name.length < 40) results.push(name);
                }
                if (results.length >= 10) break;
            }
            return results;
        }""")
        result["menus"] = menu_texts
    except Exception:
        pass

    return result


async def main():
    candidates = load_candidates()
    if not candidates:
        print("수집할 빵집이 없습니다.")
        return

    print(f"총 {len(candidates)}개 빵집 네이버 수집 시작", flush=True)

    results = []
    not_found = []

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        context = await browser.new_context(
            locale="ko-KR",
            user_agent=DESKTOP_UA,
        )
        page = await context.new_page()

        for i, bakery in enumerate(candidates, 1):
            name = bakery["name"]
            print(f"[{i}/{len(candidates)}] {name} ...", end=" ", flush=True)

            naver_id = await search_naver_id(page, name)
            if not naver_id:
                print("ID 못 찾음", flush=True)
                not_found.append(name)
                results.append({
                    "name": name, "naver_id": None,
                    "photo_url": None, "hours": None,
                    "menus": [], "reviews": [],
                })
                await asyncio.sleep(random.uniform(1.0, 2.0))
                continue

            detail = await fetch_detail(page, naver_id, name)
            results.append(detail)

            print(
                f"ID={naver_id} | 메뉴 {len(detail['menus'])}개 | "
                f"리뷰 {len(detail['reviews'])}개 | "
                f"사진={'있음' if detail['photo_url'] else '없음'} | "
                f"시간={'있음' if detail['hours'] else '없음'}",
                flush=True,
            )
            await asyncio.sleep(random.uniform(2.0, 3.5))

        await browser.close()

    OUTPUT.parent.mkdir(exist_ok=True)
    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    found = [r for r in results if r["naver_id"]]
    print(f"\n─── 완료 ───────────────────────────────────────────")
    print(f"전체: {len(results)}개  |  ID 발견: {len(found)}개  |  미발견: {len(not_found)}개")
    print(f"사진: {sum(1 for r in found if r['photo_url'])}  "
          f"메뉴: {sum(1 for r in found if r['menus'])}  "
          f"리뷰: {sum(1 for r in found if r['reviews'])}  "
          f"시간: {sum(1 for r in found if r['hours'])}")
    if not_found:
        print(f"\n미발견: {', '.join(not_found)}")
    print(f"저장: {OUTPUT}", flush=True)


if __name__ == "__main__":
    asyncio.run(main())
