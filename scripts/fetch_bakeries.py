"""카카오 로컬 API로 문정동 베이커리 데이터를 수집한다."""

import json
import math
import os
import sys

# Windows 콘솔 한글 깨짐 방지
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

import requests

KAKAO_API_KEY = os.environ.get("KAKAO_REST_API_KEY", "")
SEARCH_URL = "https://dapi.kakao.com/v2/local/search/keyword.json"

# 문정역 좌표
MOONJEONG_STATION = (127.1264, 37.4857)  # (x=경도, y=위도)


def haversine(lon1, lat1, lon2, lat2):
    """두 좌표 사이의 거리를 km로 계산한다."""
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )
    return R * 2 * math.asin(math.sqrt(a))


def search_bakeries(keyword, page=1):
    """카카오 로컬 API로 키워드 검색한다."""
    headers = {"Authorization": f"KakaoAK {KAKAO_API_KEY}"}
    params = {
        "query": keyword,
        "x": str(MOONJEONG_STATION[0]),
        "y": str(MOONJEONG_STATION[1]),
        "radius": 2000,  # 2km 반경
        "size": 15,
        "page": page,
        "sort": "distance",
    }
    resp = requests.get(SEARCH_URL, headers=headers, params=params)
    resp.raise_for_status()
    return resp.json()


def main():
    if not KAKAO_API_KEY:
        print("KAKAO_REST_API_KEY 환경변수를 설정하세요.")
        sys.exit(1)

    keywords = ["문정동 베이커리", "문정동 빵집", "문정동 제과"]
    seen_ids = set()
    results = []

    for keyword in keywords:
        print(f"검색: {keyword}")
        for page in range(1, 4):
            data = search_bakeries(keyword, page)
            documents = data.get("documents", [])
            if not documents:
                break
            for doc in documents:
                place_id = doc["id"]
                if place_id in seen_ids:
                    continue
                seen_ids.add(place_id)

                lon = float(doc["x"])
                lat = float(doc["y"])
                dist = haversine(
                    MOONJEONG_STATION[0], MOONJEONG_STATION[1], lon, lat
                )

                results.append(
                    {
                        "kakao_id": place_id,
                        "name": doc["place_name"],
                        "address": doc.get("road_address_name")
                        or doc.get("address_name", ""),
                        "category": doc.get("category_name", ""),
                        "phone": doc.get("phone", ""),
                        "url": doc.get("place_url", ""),
                        "distance_km": round(dist, 2),
                        "lat": lat,
                        "lon": lon,
                    }
                )

    results.sort(key=lambda x: x["distance_km"])

    print(f"\n총 {len(results)}곳 수집 완료\n")
    print(f"{'#':>3} {'이름':<25} {'거리':>6} {'주소'}")
    print("-" * 80)
    for i, r in enumerate(results, 1):
        print(f"{i:>3} {r['name']:<25} {r['distance_km']:>5.2f}km {r['address']}")

    output_path = os.path.join(
        os.path.dirname(__file__), "..", "data", "kakao_bakeries.json"
    )
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n저장: {output_path}")


if __name__ == "__main__":
    main()
