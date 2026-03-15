"""카카오 이미지 검색 API로 베이커리 사진 URL을 수집한다.

사용법:
    python scripts/fetch_kakao_photos.py

필요 환경변수:
    KAKAO_REST_API_KEY — 카카오 REST API 키 (.env 파일에 설정)

결과:
    data/kakao_photos.json — {bakery_id: photo_url} 매핑 파일 생성
"""

import io
import json
import os
import sys
import time
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

from dotenv import load_dotenv
from PIL import Image
import requests

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

KAKAO_REST_API_KEY = os.environ.get("KAKAO_REST_API_KEY", "")
IMAGE_SEARCH_URL = "https://dapi.kakao.com/v2/search/image"

# 전체 베이커리 목록 가져오기 (시드 + 카카오 API + 공공데이터)
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from app.data import BAKERIES

# 이름 단독 검색을 먼저 시도하고, 실패 시 지역명 조합으로 재시도
QUERY_TEMPLATES = [
    "{name}",
    "{name} 문정동",
    "{name} 빵집",
    "{name} 송파",
]

# 신뢰할 수 없는 URL 패턴 (스티커, 아이콘, 리사이즈된 썸네일 등)
BLOCKED_URL_PATTERNS = [
    "storep-phinf.pstatic.net",   # 네이버 스티커/이모지
    "dthumb-phinf.pstatic.net",   # 네이버 프록시 썸네일 (깨지기 쉬움)
    "simg.pstatic.net/static.map",  # 네이버 정적 지도 이미지
    "type=p100_100",              # 100x100 아이콘 크기
    "type=f50_50",                # 50x50 아이콘 크기
    "kamp/source/",               # Kakao KAMP 서명 URL (베이커리 비관련 콘텐츠)
    "cafeattach",                 # Daum 카페 첨부파일 (내용 예측 불가)
    "rest_main_photo",            # 식당 공통 플레이스홀더 이미지
    "daumcdn.net/news/",          # Daum 뉴스 기사 이미지 (빵집 비관련)
    "daumcdn.net/blogfile/",      # Daum 구 블로그 파일 (품질 불안정)
    "kpenews.com",                # 식품 뉴스 사이트 이미지
]


def _is_valid_url(url: str) -> bool:
    """URL이 유효한 베이커리 사진인지 검증한다."""
    # 차단 패턴 필터링
    for pattern in BLOCKED_URL_PATTERNS:
        if pattern in url:
            return False

    # PNG 파일 차단 (로고/일러스트가 많음, 실제 사진은 jpg/webp)
    url_path = url.split("?")[0].lower()
    if url_path.endswith(".png"):
        return False

    # HEAD 요청으로 실제 이미지인지 확인 (referrer 없이)
    try:
        r = requests.head(
            url, timeout=5, allow_redirects=True,
            headers={"Referer": ""},
        )
        if r.status_code != 200:
            return False
        content_type = r.headers.get("content-type", "")
        # content-type이 있으면 image여야 함
        if content_type and "image" not in content_type:
            return False
        # 너무 작은 파일 제외 (1KB 미만 = 아이콘/placeholder)
        content_length = r.headers.get("content-length", "")
        if content_length and int(content_length) < 1024:
            return False
    except Exception:
        return False

    return True


# 따뜻한 색상 판별 기준 (HSV)
# 빵/베이커리: 갈색, 황금색, 크림색, 베이지, 따뜻한 나무톤
# H: 0~50 (빨강~주황~노랑 계열), S: 자유, V: 자유
# 추가로 저채도 따뜻한 톤 (크림색, 베이지): S < 40, V > 150
WARM_HUE_MIN = 0
WARM_HUE_MAX = 50
MIN_WARM_RATIO = 0.15  # 전체 픽셀 중 15% 이상이 따뜻한 톤이면 통과


def _has_warm_tones(url: str) -> bool:
    """이미지를 다운로드하여 갈색/따뜻한 색상 비율이 충분한지 판별한다."""
    try:
        resp = requests.get(
            url, timeout=10, headers={"Referer": ""},
            stream=True,
        )
        if resp.status_code != 200:
            return False

        # 메모리에서 이미지 열기, 축소해서 빠르게 분석
        img = Image.open(io.BytesIO(resp.content))
        img = img.convert("RGB")
        img = img.resize((80, 80))  # 80x80으로 축소 (속도)

        pixels = list(img.getdata())
        total = len(pixels)
        if total == 0:
            return False

        warm_count = 0
        for r, g, b in pixels:
            # RGB → HSV 간이 변환
            max_c = max(r, g, b)
            min_c = min(r, g, b)
            diff = max_c - min_c

            # 무채색(회색/흰색/검정)은 건너뜀
            if diff < 15:
                # 저채도지만 따뜻한 크림/베이지 (R > G > B, 밝은 톤)
                if r > 150 and g > 130 and r >= g >= b and max_c > 170:
                    warm_count += 1
                continue

            # Hue 계산
            if max_c == r:
                h = 60 * ((g - b) / diff % 6)
            elif max_c == g:
                h = 60 * ((b - r) / diff + 2)
            else:
                h = 60 * ((r - g) / diff + 4)
            if h < 0:
                h += 360

            # 따뜻한 색상 범위: 0~50도 (빨강~주황~노랑)
            if WARM_HUE_MIN <= h <= WARM_HUE_MAX:
                warm_count += 1

        ratio = warm_count / total
        return ratio >= MIN_WARM_RATIO

    except Exception:
        return False


def search_bakery_image(name: str, api_key: str) -> str:
    """카카오 이미지 검색 API로 베이커리 사진 URL을 검색한다.

    여러 쿼리를 시도하고, 각 결과에서 최대 5개 후보를 검증한다.
    """
    headers = {"Authorization": f"KakaoAK {api_key}"}

    for template in QUERY_TEMPLATES:
        query = template.format(name=name)
        params = {
            "query": query,
            "size": 5,
        }

        try:
            resp = requests.get(IMAGE_SEARCH_URL, headers=headers, params=params, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            documents = data.get("documents", [])
            for doc in documents:
                url = doc.get("image_url", "")
                if url and _is_valid_url(url):
                    if _has_warm_tones(url):
                        return url
                    else:
                        print(f"    ✗ 따뜻한 톤 부족, 스킵: {url[:60]}...")
        except Exception as e:
            print(f"    오류 ({query}): {e}")

        time.sleep(0.2)

    return ""


def main():
    if not KAKAO_REST_API_KEY:
        print("KAKAO_REST_API_KEY 환경변수를 설정하세요.")
        print(".env 파일에 KAKAO_REST_API_KEY=your_key 형태로 추가")
        sys.exit(1)

    output_path = Path(__file__).resolve().parent.parent / "data" / "kakao_photos.json"
    output_path.parent.mkdir(exist_ok=True)

    # 기존 데이터가 있으면 로드
    existing = {}
    if output_path.exists():
        with open(output_path, "r", encoding="utf-8") as f:
            existing = json.load(f)

    print(f"카카오 이미지 검색 API로 베이커리 사진을 수집합니다... (전체 {len(BAKERIES)}곳)\n")

    photos = {}
    for bakery in BAKERIES:
        bakery_id = str(bakery.id)
        name = bakery.name

        # 이미 수집된 사진이 있고 유효하면 스킵
        if bakery_id in existing and existing[bakery_id]:
            if _is_valid_url(existing[bakery_id]):
                if _has_warm_tones(existing[bakery_id]):
                    print(f"  [{bakery_id}] {name} — 기존 사진 유지")
                    photos[bakery_id] = existing[bakery_id]
                    continue
                else:
                    print(f"  [{bakery_id}] {name} — 기존 사진 색상 부적합, 재검색...")
            else:
                print(f"  [{bakery_id}] {name} — 기존 사진 깨짐, 재검색...")

        print(f"  [{bakery_id}] {name} 검색 중...")
        url = search_bakery_image(name, KAKAO_REST_API_KEY)

        if url:
            print(f"    → {url[:80]}...")
            photos[bakery_id] = url
        else:
            print(f"    → 사진 없음 (SVG 일러스트 폴백)")
            photos[bakery_id] = ""

        time.sleep(0.3)  # API 호출 간격

    # JSON 저장
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(photos, f, ensure_ascii=False, indent=2)

    found = sum(1 for v in photos.values() if v)
    print(f"\n완료: {found}/{len(photos)}곳 사진 수집")
    print(f"사진 없는 곳은 SVG 일러스트가 자동 표시됩니다.")
    print(f"저장: {output_path}")


if __name__ == "__main__":
    main()
