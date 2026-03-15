from __future__ import annotations

from kiwipiepy import Kiwi

KEYWORD_TAG_MAP: dict[str, list[str]] = {
    "아늑한": ["아늑", "따뜻", "포근"],
    "케이크맛집": ["케이크", "생크림", "시트", "레이어", "생일케이크"],
    "마카롱맛집": ["마카롱", "꼬끄"],
    "소금빵맛집": ["소금빵"],
    "쿠키맛집": ["쿠키", "타르트", "까눌레", "두쫀쿠"],
    "베이글맛집": ["베이글"],
    "가성비좋은": ["가성비", "저렴", "가격 대비"],
    "줄서는집": ["줄", "웨이팅", "대기", "오픈런", "조기마감", "품절"],
    "선물하기좋은": ["선물", "포장", "예쁜 박스"],
    "브런치맛집": ["브런치", "샌드위치", "토스트", "스콘"],
    "식사빵": ["발효", "통밀", "치아바타", "깜빠뉴", "바게트", "호밀", "담백", "식사"],
    "동네 단골": ["동네", "단골", "편안한", "매일"],
    "대형빵집": ["대형", "넓은", "쾌적", "주차편한", "2층", "대규모"],
    "친절한": ["친절"],
}

# Kiwi 인스턴스 — 모듈 로드 시 1회 초기화 (모델 로딩 비용이 크므로 싱글턴)
_kiwi: Kiwi | None = None


def _get_kiwi() -> Kiwi:
    global _kiwi
    if _kiwi is None:
        # kiwipiepy 모델 경로 탐색 순서:
        # 1) 환경변수 KIWI_MODEL_PATH (배포 환경에서 설정)
        # 2) C:/kiwi_model (Windows 개발환경 — 사용자 경로에 한글이 있으면 C++ 확장이
        #    모델을 못 열기 때문에 한글 없는 경로로 복사 후 사용)
        # 3) kiwipiepy_model 패키지 기본 경로 (리눅스/Mac 등 ASCII 경로 환경)
        import os
        model_path: str | None = os.environ.get("KIWI_MODEL_PATH")
        if model_path is None:
            win_fallback = "C:/kiwi_model"
            if os.path.isdir(win_fallback):
                model_path = win_fallback
        _kiwi = Kiwi(model_path=model_path) if model_path else Kiwi()
    return _kiwi


def _morphemes(text: str) -> str:
    """텍스트를 형태소 단위로 분리해 공백 구분 문자열로 반환.

    예) "웨이팅이있어요" → "웨이팅 이 있 어요"
        "친절합니다"    → "친절 하 ㅂ니다"
        "가성비가최고"  → "가성비 가 최고"
    """
    tokens = _get_kiwi().tokenize(text)
    return " ".join(t.form for t in tokens)


def extract_tags(reviews: list[str], min_reviews: int = 1) -> list[str]:
    """리뷰 목록에서 태그를 추출한다.

    Args:
        reviews: 방문자 리뷰 문자열 목록
        min_reviews: 태그가 붙으려면 키워드가 등장해야 하는 최소 리뷰 수 (기본 1).
                     값을 높이면 신뢰도 높은 태그만 남긴다 (빈도 가중치).
    """
    if not reviews:
        return []

    # 리뷰별로 원본 + 형태소 분리 텍스트를 미리 준비
    morphed_reviews = [_morphemes(r) for r in reviews]

    tags = []
    for tag, keywords in KEYWORD_TAG_MAP.items():
        # 키워드가 등장한 리뷰 수 카운트
        # - 원본: "가격 대비", "예쁜 박스" 같은 복합 표현 보장
        # - 형태소: 조사·어미 결합으로 변형된 단어 감지 (예: "웨이팅이있어요" → "웨이팅")
        match_count = sum(
            1 for raw, morphed in zip(reviews, morphed_reviews)
            if any(kw in raw or kw in morphed for kw in keywords)
        )
        if match_count >= min_reviews:
            tags.append(tag)

    return tags


# mood/purpose → 태그 매핑 (리뷰 없는 빵집용 폴백)
_MOOD_TAG_MAP: dict[str, str] = {
    "아늑한": "아늑한",
    "편안한": "동네 단골",
    "감성적인": "선물하기좋은",
    "모던한": "모던한",
    "동네 단골": "동네 단골",
    "대형빵집": "대형빵집",
}

_PURPOSE_TAG_MAP: dict[str, str] = {
    "브런치": "브런치맛집",
    "선물": "선물하기좋은",
    "케이크": "케이크맛집",
    "식사빵": "식사빵",
}


def generate_fallback_tags(mood: list[str], purpose: list[str]) -> list[str]:
    """리뷰가 없을 때 mood/purpose에서 태그를 생성한다."""
    tags: list[str] = []
    for m in mood:
        if m in _MOOD_TAG_MAP and _MOOD_TAG_MAP[m] not in tags:
            tags.append(_MOOD_TAG_MAP[m])
    for p in purpose:
        if p in _PURPOSE_TAG_MAP and _PURPOSE_TAG_MAP[p] not in tags:
            tags.append(_PURPOSE_TAG_MAP[p])
    return tags
