"""감각 기반 추천 매핑 — 3단계 질문을 mood/purpose 조건으로 변환한다."""

_PURPOSE_MAP = {
    # ("바삭", "달콤") 매핑 없음 — None 반환, 특정 목적 필터 미적용
    ("바삭", "고소"): "식사빵",   # 바게트·캄파뉴 등 담백한 식사 빵
    ("부드러움", "달콤"): "케이크",  # 생크림·무스 케이크
    ("부드러움", "고소"): "브런치",  # 샌드위치·소프트 식사 빵
}

_MOOD_MAP = {
    "혼자": "아늑한",   # 조용한 동네 빵집
    "여럿": "편안한",   # 일행과 함께하기 편한 넓은 곳
}


def map_sensory_to_conditions(
    texture: str, taste: str, atmosphere: str
) -> dict[str, str | None]:
    """감각 입력을 mood/purpose 조건으로 변환한다.

    미매칭 시 None 반환 — recommend()에서 None은 해당 필터 미적용으로 처리된다.
    (기존: 미매칭 시 "편안한"/"빵구경" 하드코딩 → 의도치 않은 필터 적용 가능성 있었음)
    """
    return {
        "mood": _MOOD_MAP.get(atmosphere),
        "purpose": _PURPOSE_MAP.get((texture, taste)),
    }
