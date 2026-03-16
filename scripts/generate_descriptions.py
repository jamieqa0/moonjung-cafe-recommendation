"""상호명 + 주소 + 리뷰 기반으로 Claude API를 이용해 베이커리 설명과 맛 프로필을 생성한다.

사용법:
    python scripts/generate_descriptions.py           # 설명 + 맛 프로필 모두 생성
    python scripts/generate_descriptions.py --desc    # 설명만
    python scripts/generate_descriptions.py --flavor  # 맛 프로필만

필요 환경변수:
    ANTHROPIC_API_KEY — Anthropic API 키 (.env 파일에 설정)

결과:
    data/descriptions.json    — {bakery_name: description} 매핑
    data/flavor_profiles.json — {bakery_name: flavor_profile} 매핑
"""

import argparse
import json
import sys
import time
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import anthropic
from app.data import BAKERIES

DESC_OUTPUT = Path(__file__).resolve().parent.parent / "data" / "descriptions.json"
FLAVOR_OUTPUT = Path(__file__).resolve().parent.parent / "data" / "flavor_profiles.json"


def generate_description(client: anthropic.Anthropic, name: str, address: str, reviews: list[str]) -> str:
    """Claude API로 베이커리 한 줄 설명을 생성한다."""
    reviews_text = "\n".join(f"- {r}" for r in reviews[:3]) if reviews else "리뷰 없음"

    prompt = f"""다음 베이커리에 대한 한 줄 소개를 한국어로 작성해주세요.

상호명: {name}
주소: {address}
방문 리뷰:
{reviews_text}

조건:
- 40자 이내
- 실제 리뷰에서 언급된 특징 반영 (리뷰가 없으면 상호명과 위치 기반으로 작성)
- 과장 없이 담백한 톤
- 한 문장만 출력 (다른 설명 없이)"""

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=100,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text.strip()


def generate_flavor_profile(
    client: anthropic.Anthropic,
    name: str,
    signature_menu: list[str],
    reviews: list[str],
) -> str:
    """Claude API로 대표 메뉴의 맛·식감·향 프로필을 생성한다."""
    menu_text = ", ".join(signature_menu) if signature_menu else "미확인"
    reviews_text = "\n".join(f"- {r}" for r in reviews[:3]) if reviews else "리뷰 없음"

    prompt = f"""다음 베이커리 대표 메뉴의 맛과 식감을 짧고 감각적으로 묘사해주세요.

상호명: {name}
대표 메뉴: {menu_text}
방문 리뷰:
{reviews_text}

조건:
- 1~2문장, 50자 이내
- 식감(바삭·쫄깃·촉촉 등), 맛(달콤·짭조름·고소 등), 향 위주로 묘사
- 리뷰에 맛 언급이 없으면 상호명·메뉴 이름에서 유추
- 과장 없이 담백하고 감각적인 한국어로
- 묘사 문장만 출력 (다른 설명 없이)"""

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=120,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text.strip()


def run_descriptions(client: anthropic.Anthropic) -> None:
    existing: dict[str, str] = {}
    if DESC_OUTPUT.exists():
        with open(DESC_OUTPUT, "r", encoding="utf-8") as f:
            existing = json.load(f)

    descriptions = dict(existing)
    print(f"=== 설명 생성 (총 {len(BAKERIES)}곳) ===\n")

    for bakery in BAKERIES:
        if bakery.name in descriptions and descriptions[bakery.name]:
            print(f"  [{bakery.name}] 기존 유지")
            continue

        print(f"  [{bakery.name}] 생성 중...", end=" ", flush=True)
        desc = generate_description(client, bakery.name, bakery.address, bakery.reviews)
        descriptions[bakery.name] = desc
        print(desc)
        time.sleep(0.3)

    DESC_OUTPUT.parent.mkdir(exist_ok=True)
    with open(DESC_OUTPUT, "w", encoding="utf-8") as f:
        json.dump(descriptions, f, ensure_ascii=False, indent=2)
    print(f"\n저장: {DESC_OUTPUT} ({len(descriptions)}곳)")


def run_flavor_profiles(client: anthropic.Anthropic) -> None:
    existing: dict[str, str] = {}
    if FLAVOR_OUTPUT.exists():
        with open(FLAVOR_OUTPUT, "r", encoding="utf-8") as f:
            existing = json.load(f)

    flavor_profiles = dict(existing)
    print(f"=== 맛 프로필 생성 (총 {len(BAKERIES)}곳) ===\n")

    for bakery in BAKERIES:
        if bakery.name in flavor_profiles and flavor_profiles[bakery.name]:
            print(f"  [{bakery.name}] 기존 유지")
            continue

        print(f"  [{bakery.name}] 생성 중...", end=" ", flush=True)
        fp = generate_flavor_profile(client, bakery.name, bakery.signature_menu, bakery.reviews)
        flavor_profiles[bakery.name] = fp
        print(fp)
        time.sleep(0.3)

    FLAVOR_OUTPUT.parent.mkdir(exist_ok=True)
    with open(FLAVOR_OUTPUT, "w", encoding="utf-8") as f:
        json.dump(flavor_profiles, f, ensure_ascii=False, indent=2)
    print(f"\n저장: {FLAVOR_OUTPUT} ({len(flavor_profiles)}곳)")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--desc", action="store_true", help="설명만 생성")
    parser.add_argument("--flavor", action="store_true", help="맛 프로필만 생성")
    args = parser.parse_args()

    client = anthropic.Anthropic()

    if args.desc:
        run_descriptions(client)
    elif args.flavor:
        run_flavor_profiles(client)
    else:
        run_descriptions(client)
        print()
        run_flavor_profiles(client)


if __name__ == "__main__":
    main()
