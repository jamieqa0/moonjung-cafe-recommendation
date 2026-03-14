"""카카오 이미지 검색 API로 베이커리 사진 URL을 수집한다.

사용법:
    python scripts/fetch_bakery_photos.py

필요 환경변수:
    KAKAO_REST_API_KEY — 카카오 REST API 키 (.env 파일에 설정)

결과:
    data/bakery_photos.json — {bakery_id: photo_url} 매핑 파일 생성
"""

import json
import os
import sys
import time
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

from dotenv import load_dotenv
import requests

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

KAKAO_REST_API_KEY = os.environ.get("KAKAO_REST_API_KEY", "")
IMAGE_SEARCH_URL = "https://dapi.kakao.com/v2/search/image"

# 시드 데이터에서 베이커리 이름과 ID 가져오기
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from app.data import _RAW_BAKERIES


def search_bakery_image(name: str, api_key: str) -> str:
    """카카오 이미지 검색 API로 베이커리 사진 URL을 검색한다."""
    headers = {"Authorization": f"KakaoAK {api_key}"}
    params = {
        "query": f"{name} 빵집",
        "size": 1,
    }

    try:
        resp = requests.get(IMAGE_SEARCH_URL, headers=headers, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        documents = data.get("documents", [])
        if documents:
            return documents[0].get("image_url", "")
    except Exception as e:
        print(f"  오류: {e}")

    return ""


def main():
    if not KAKAO_REST_API_KEY:
        print("KAKAO_REST_API_KEY 환경변수를 설정하세요.")
        print(".env 파일에 KAKAO_REST_API_KEY=your_key 형태로 추가")
        sys.exit(1)

    output_path = Path(__file__).resolve().parent.parent / "data" / "bakery_photos.json"
    output_path.parent.mkdir(exist_ok=True)

    # 기존 데이터가 있으면 로드
    existing = {}
    if output_path.exists():
        with open(output_path, "r", encoding="utf-8") as f:
            existing = json.load(f)

    print("카카오 이미지 검색 API로 베이커리 사진을 수집합니다...\n")

    photos = {}
    for bakery in _RAW_BAKERIES:
        bakery_id = str(bakery["id"])
        name = bakery["name"]

        # 이미 수집된 사진이 있으면 스킵
        if bakery_id in existing and existing[bakery_id]:
            print(f"  [{bakery_id}] {name} — 기존 사진 유지")
            photos[bakery_id] = existing[bakery_id]
            continue

        print(f"  [{bakery_id}] {name} 검색 중...")
        url = search_bakery_image(name, KAKAO_REST_API_KEY)

        if url:
            print(f"    → {url[:80]}...")
            photos[bakery_id] = url
        else:
            print(f"    → 사진 없음")
            photos[bakery_id] = ""

        time.sleep(0.3)  # API 호출 간격

    # JSON 저장
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(photos, f, ensure_ascii=False, indent=2)

    found = sum(1 for v in photos.values() if v)
    print(f"\n완료: {found}/{len(photos)}곳 사진 수집")
    print(f"저장: {output_path}")
    print("\n수집된 URL을 확인하고, 부적절한 이미지는 빈 문자열로 수정하세요.")


if __name__ == "__main__":
    main()
