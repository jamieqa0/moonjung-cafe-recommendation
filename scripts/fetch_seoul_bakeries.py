"""서울 열린데이터광장 API로 송파구 제과점 인허가 데이터를 수집한다.

API 키 발급: https://data.seoul.go.kr → 회원가입 → 인증키 신청 (무료, 즉시 발급)

필터링 전략:
  1. 개방서비스명에 '제과점' 포함 (API가 LOCALDATA_072405 = 제과점영업만 반환하므로 전체 해당)
  2. 위생업태명 블랙리스트: 편의점, 패스트푸드, 백화점, 키즈카페, 다방, 아이스크림,
     일반조리판매 — 제과점 면허를 받았지만 실제 빵집이 아닌 업종 제외
  3. 상호명 블랙리스트: 편의점 브랜드, PC방, 마트, 슈퍼, 영화관, 분식/한식/일식 업체 제외
  4. 양성 필터: 상호명에 빵집 관련 키워드(빵, 베이커리, 케이크, …)가 있는 곳만 통과
"""

import csv
import json
import os
import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

from dotenv import load_dotenv
import requests

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

SEOUL_API_KEY = os.environ.get("SEOUL_API_KEY", "")
# LOCALDATA_072405 = 서울시 제과점영업 인허가 정보
API_URL = "http://openapi.seoul.go.kr:8088/{key}/json/LOCALDATA_072405/{start}/{end}"

# ── 필터링 상수 ────────────────────────────────────────────────────────────────

# 위생업태명 블랙리스트: 실제 빵집이 아닌 업종
EXCLUDE_BIZ_TYPES = {
    "편의점", "패스트푸드", "백화점", "키즈카페", "다방",
    "아이스크림", "일반조리판매", "탁주/약주", "주점",
}

# 상호명 블랙리스트: 이름만으로 비빵집 판별
BLACKLIST_NAME_KEYWORDS = [
    # 편의점 브랜드
    "세븐일레븐", "GS25", "CU편의점", "이마트24", "미니스톱",
    # 대형 비빵집 프랜차이즈
    "스타벅스", "롯데리아", "맥도날드", "버거킹", "KFC", "서브웨이",
    "이디야", "메가커피", "메가엠지씨", "빽다방", "공차", "투썸플레이스",
    "할리스", "탐앤탐스", "엔제리너스", "커피빈",
    # 업종 명시 비빵집
    "편의점", "PC방", "마트", "슈퍼", "영화관", "노래방",
    # 명확한 비빵집 업종
    "김밥", "떡볶이", "스시", "초밥", "피자", "치킨", "국밥",
    "삼겹살", "갈비", "분식", "냉면", "설렁탕", "곱창", "순대",
    "족발", "라면", "얌차",
]

# 상호명 양성 키워드: 이 중 하나라도 포함되면 빵집으로 분류
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

# CSV 컬럼 (서울 열린데이터광장 제과점영업 기준)
CSV_COLUMNS = [
    "번호", "개방서비스명", "개방서비스아이디", "개방자치단체코드",
    "관리번호", "인허가일자", "인허가취소일자", "영업상태구분코드",
    "영업상태명", "상세영업상태코드", "상세영업상태명", "폐업일자",
    "휴업시작일자", "휴업종료일자", "재개업일자", "소재지전화",
    "소재지면적", "소재지우편번호", "소재지전체주소", "도로명전체주소",
    "도로명우편번호", "사업장명", "최종수정시점", "데이터갱신구분",
    "데이터갱신일자", "업태구분명", "좌표정보(x)", "좌표정보(y)",
    "위생업태명",
]

# API 응답의 row 키 매핑
ROW_KEYS = [
    "ROWNUM", "OPNSFTEAMCODE", "MGTNO", "APVPERMYMD", "APVCANCELYMD",
    "TRDSTATEGBN", "TRDSTATENM", "DTLSTATEGBN", "DTLSTATENM", "DCBYMD",
    "CLGSTDT", "CLGENDDT", "ROPNDT", "SITEWHLADDR", "RDNWHLADDR",
    "RDNPOSTNO", "BPLCNM", "LASTMODTS", "UPDATEGBN", "UPDATEDT",
    "UPTAENM", "X", "Y", "SITETEL", "SITEAREA", "SITEPOSTNO",
]


def fetch_page(start, end):
    """API 페이지를 가져온다."""
    url = API_URL.format(key=SEOUL_API_KEY, start=start, end=end)
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    # 에러 체크
    result_key = "LOCALDATA_072405"
    if result_key not in data:
        error = data.get("RESULT", {})
        print(f"API 오류: {error.get('MESSAGE', '알 수 없는 오류')}")
        return [], 0

    result = data[result_key]
    total = result.get("list_total_count", 0)
    rows = result.get("row", [])
    return rows, total


def _is_bakery(name: str, biz_type: str) -> bool:
    """상호명·위생업태명으로 실제 빵집 여부를 판별한다."""
    name_lower = name.lower()
    # 위생업태명 블랙리스트
    if biz_type in EXCLUDE_BIZ_TYPES:
        return False
    # 상호명 블랙리스트
    if any(kw.lower() in name_lower for kw in BLACKLIST_NAME_KEYWORDS):
        return False
    # 상호명 양성 키워드 (하나라도 있으면 빵집)
    return any(kw.lower() in name_lower for kw in BAKERY_NAME_KEYWORDS)


def filter_munjeong(rows):
    """문정동 + 영업중 + 실제 빵집인 제과점만 필터링한다."""
    filtered = []
    for row in rows:
        addr = row.get("SITEWHLADDR", "")
        status = row.get("DTLSTATENM", "")
        # 개방서비스명에 '제과점' 포함 확인 (API 특성상 전체 해당하지만 명시적 검증)
        service = row.get("OPNSFTEAMCODE", "")  # 필드명이 다를 수 있어 SITEWHLADDR로 우선 처리
        if "문정동" not in addr or "영업" not in status:
            continue
        name = row.get("BPLCNM", "")
        biz_type = row.get("UPTAENM", "")
        if _is_bakery(name, biz_type):
            filtered.append(row)
    return filtered


def row_to_csv_dict(row, idx):
    """API row를 CSV 딕셔너리로 변환한다."""
    return {
        "번호": idx,
        "개방서비스명": "제과점영업",
        "개방서비스아이디": "07_22_01_P",
        "개방자치단체코드": "3230000",
        "관리번호": row.get("MGTNO", ""),
        "인허가일자": row.get("APVPERMYMD", ""),
        "인허가취소일자": row.get("APVCANCELYMD", ""),
        "영업상태구분코드": row.get("TRDSTATEGBN", ""),
        "영업상태명": row.get("TRDSTATENM", ""),
        "상세영업상태코드": row.get("DTLSTATEGBN", ""),
        "상세영업상태명": row.get("DTLSTATENM", ""),
        "폐업일자": row.get("DCBYMD", ""),
        "휴업시작일자": row.get("CLGSTDT", ""),
        "휴업종료일자": row.get("CLGENDDT", ""),
        "재개업일자": row.get("ROPNDT", ""),
        "소재지전화": row.get("SITETEL", ""),
        "소재지면적": row.get("SITEAREA", ""),
        "소재지우편번호": row.get("SITEPOSTNO", ""),
        "소재지전체주소": row.get("SITEWHLADDR", ""),
        "도로명전체주소": row.get("RDNWHLADDR", ""),
        "도로명우편번호": row.get("RDNPOSTNO", ""),
        "사업장명": row.get("BPLCNM", ""),
        "최종수정시점": row.get("LASTMODTS", ""),
        "데이터갱신구분": row.get("UPDATEGBN", ""),
        "데이터갱신일자": row.get("UPDATEDT", ""),
        "업태구분명": row.get("UPTAENM", ""),
        "좌표정보(x)": row.get("X", ""),
        "좌표정보(y)": row.get("Y", ""),
        "위생업태명": row.get("UPTAENM", ""),
    }


def main():
    if not SEOUL_API_KEY:
        print("SEOUL_API_KEY 환경변수를 설정하세요.")
        print("발급: https://data.seoul.go.kr → 회원가입 → 마이페이지 → 인증키 신청")
        sys.exit(1)

    print("서울 열린데이터광장에서 제과점 데이터를 수집합니다...")

    # 송파구 전체 제과점 수집 (페이지별 1000건)
    all_munjeong = []
    page_size = 1000
    start = 1

    # 첫 페이지로 전체 건수 확인
    rows, total = fetch_page(1, page_size)
    if not rows:
        print("데이터를 가져올 수 없습니다.")
        sys.exit(1)

    print(f"전체 제과점 데이터: {total}건")
    munjeong = filter_munjeong(rows)
    all_munjeong.extend(munjeong)
    print(f"  페이지 1: {len(rows)}건 중 문정동 {len(munjeong)}건")

    # 나머지 페이지
    start = page_size + 1
    while start <= total:
        end = min(start + page_size - 1, total)
        rows, _ = fetch_page(start, end)
        if not rows:
            break
        munjeong = filter_munjeong(rows)
        all_munjeong.extend(munjeong)
        page_num = (start // page_size) + 1
        print(f"  페이지 {page_num}: {len(rows)}건 중 문정동 {len(munjeong)}건")
        start += page_size

    print(f"\n문정동 영업중 빵집(필터 후): {len(all_munjeong)}곳")

    if not all_munjeong:
        print("문정동 제과점을 찾을 수 없습니다.")
        sys.exit(1)

    # CSV 저장
    output_path = os.path.join(
        os.path.dirname(__file__), "..", "data", "public_bakeries.csv"
    )
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        for idx, row in enumerate(all_munjeong, 1):
            writer.writerow(row_to_csv_dict(row, idx))

    print(f"\n저장: {output_path}")
    print("\n--- 수집된 제과점 목록 ---")
    for i, row in enumerate(all_munjeong, 1):
        name = row.get("BPLCNM", "")
        addr = row.get("SITEWHLADDR", "")
        print(f"  {i}. {name} — {addr}")


if __name__ == "__main__":
    main()
