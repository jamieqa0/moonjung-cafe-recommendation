"""
Playwright로 카카오맵 장소 상세 정보 스크래핑.
입력: data/kakao_bakeries.json (fetch_kakao_bakeries.py 실행 결과)
출력: data/kakao_details.json (메뉴, 후기, 영업시간, 사진 URL)

셀렉터 (place.map.kakao.com 기준):
  후기 텍스트: .desc_review
  메뉴 이름:   .list_goods .tit_item
  메뉴 가격:   .list_goods .desc_item
  영업시간:    .info_runtime
  메뉴 탭:     a[href="#menuInfo"]
"""

import asyncio
import json
import random
import sys
from pathlib import Path

from playwright.async_api import async_playwright

ROOT = Path(__file__).parent.parent
INPUT = ROOT / "data" / "kakao_bakeries.json"
OUTPUT = ROOT / "data" / "kakao_details.json"


async def fetch_place(page, kakao_id: str, name: str) -> dict:
    url = f"https://place.map.kakao.com/{kakao_id}"
    result = {
        "kakao_id": kakao_id,
        "name": name,
        "hours": None,
        "menus": [],
        "reviews": [],
        "photo_url": None,
    }

    try:
        # 홈 탭 로드
        await page.goto(url, wait_until="domcontentloaded", timeout=20000)
        await page.wait_for_timeout(2500)

        # 사진 URL (og:image)
        og_image = await page.eval_on_selector(
            'meta[property="og:image"]', "el => el.content"
        ) if await page.query_selector('meta[property="og:image"]') else None
        if og_image:
            result["photo_url"] = og_image.replace("//", "https://", 1)

        # 영업시간
        hours_el = await page.query_selector(".info_runtime")
        if hours_el:
            result["hours"] = (await hours_el.inner_text()).strip()

        # 후기 (홈 탭에 미리보기 있음)
        review_items = await page.query_selector_all(".desc_review")
        for item in review_items[:5]:
            text = (await item.inner_text()).strip()
            # "더보기" 접미사 제거, 150자 제한
            text = text.replace(" 더보기", "").strip()
            if len(text) > 5:
                result["reviews"].append(text[:150])

        # 메뉴 탭 이동
        menu_tab = await page.query_selector('a[href="#menuInfo"]')
        if menu_tab:
            await menu_tab.click()
            await page.wait_for_timeout(2000)

            tit_items = await page.query_selector_all(".list_goods .tit_item")
            desc_items = await page.query_selector_all(".list_goods .desc_item")

            for i, tit in enumerate(tit_items[:15]):
                menu_name = (await tit.inner_text()).strip()
                price = ""
                if i < len(desc_items):
                    price = (await desc_items[i].inner_text()).strip()
                if menu_name:
                    result["menus"].append(f"{menu_name} {price}".strip())

    except Exception as e:
        print(f"  !! 오류: {name} ({kakao_id}): {e}", flush=True)

    return result


async def main():
    with open(INPUT, encoding="utf-8") as f:
        bakeries = json.load(f)

    print(f"총 {len(bakeries)}개 가게 수집 시작", flush=True)
    results = []

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        context = await browser.new_context(
            locale="ko-KR",
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0.0.0 Safari/537.36"
            ),
        )
        page = await context.new_page()

        for i, bakery in enumerate(bakeries, 1):
            kakao_id = bakery["kakao_id"]
            name = bakery["name"]
            print(f"[{i}/{len(bakeries)}] {name} ...", end=" ", flush=True)

            detail = await fetch_place(page, kakao_id, name)
            results.append(detail)

            print(
                f"메뉴 {len(detail['menus'])}개, "
                f"후기 {len(detail['reviews'])}개, "
                f"영업시간: {'있음' if detail['hours'] else '없음'}",
                flush=True,
            )

            await asyncio.sleep(random.uniform(1.5, 2.5))

        await browser.close()

    OUTPUT.parent.mkdir(exist_ok=True)
    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    got_menus = sum(1 for r in results if r["menus"])
    got_reviews = sum(1 for r in results if r["reviews"])
    got_hours = sum(1 for r in results if r["hours"])
    print(
        f"\n완료! 메뉴: {got_menus}/{len(results)}, "
        f"후기: {got_reviews}/{len(results)}, "
        f"영업시간: {got_hours}/{len(results)}"
    )
    print(f"저장: {OUTPUT}", flush=True)


if __name__ == "__main__":
    asyncio.run(main())
