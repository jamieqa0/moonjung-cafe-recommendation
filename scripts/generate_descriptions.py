"""상호명 + 주소 + 리뷰 기반으로 Claude API를 이용해 베이커리 설명을 생성한다.

사용법:
    python scripts/generate_descriptions.py

필요 환경변수:
    ANTHROPIC_API_KEY — Anthropic API 키 (.env 파일에 설정)

결과:
    data/descriptions.json — {bakery_name: description} 매핑 파일 생성/갱신
"""

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

OUTPUT = Path(__file__).resolve().parent.parent / "data" / "descriptions.json"


def generate_description(client: anthropic.Anthropic, name: str, address: str, reviews: list[str]) -> str:
    """Claude API로 베이커리 한 줄 설명을 생성한다."""
    if reviews:
        reviews_text = "\n".join(f"- {r}" for r in reviews[:3])
    else:
        reviews_text = "리뷰 없음"

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


def main():
    existing: dict[str, str] = {}
    if OUTPUT.exists():
        with open(OUTPUT, "r", encoding="utf-8") as f:
            existing = json.load(f)

    client = anthropic.Anthropic()
    descriptions = dict(existing)

    print(f"총 {len(BAKERIES)}곳 설명 생성 시작\n")

    for bakery in BAKERIES:
        if bakery.name in descriptions and descriptions[bakery.name]:
            print(f"  [{bakery.name}] 기존 설명 유지")
            continue

        print(f"  [{bakery.name}] 생성 중...", end=" ", flush=True)
        desc = generate_description(client, bakery.name, bakery.address, bakery.reviews)
        descriptions[bakery.name] = desc
        print(desc)
        time.sleep(0.3)

    OUTPUT.parent.mkdir(exist_ok=True)
    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(descriptions, f, ensure_ascii=False, indent=2)

    print(f"\n저장: {OUTPUT}")
    print(f"생성 완료: {len(descriptions)}곳")


if __name__ == "__main__":
    main()
