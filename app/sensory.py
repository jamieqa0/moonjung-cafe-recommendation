"""감각 기반 추천 매핑 — 3단계 이진 질문을 mood/purpose 조건으로 변환한다."""

_PURPOSE_MAP = {
    ("바삭", "달콤"): "빵구경",
    ("바삭", "고소"): "브런치",
    ("부드러움", "달콤"): "케이크",
    ("부드러움", "고소"): "브런치",
}

_MOOD_MAP = {
    "혼자": "아늑한",
    "여럿": "편안한",
}


def map_sensory_to_conditions(
    texture: str, taste: str, atmosphere: str
) -> dict[str, str]:
    return {
        "mood": _MOOD_MAP.get(atmosphere, "편안한"),
        "purpose": _PURPOSE_MAP.get((texture, taste), "빵구경"),
    }
