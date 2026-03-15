import random

from app.models import Bakery


def recommend(
    bakeries: list[Bakery],
    mood: str | None = None,
    purpose: str | None = None,
    price_range: str | None = None,
    parking: bool | None = None,
    custom_order: bool | None = None,
    max_distance: float | None = None,
    min_distance: float | None = None,
    max_results: int = 5,
) -> list[Bakery]:
    # 1. 불리언/거리 필터링
    filtered = bakeries
    if parking is not None:
        filtered = [b for b in filtered if b.parking == parking]
    if custom_order is not None:
        filtered = [b for b in filtered if b.custom_order == custom_order]
    if max_distance is not None:
        filtered = [b for b in filtered if b.distance <= max_distance]
    if min_distance is not None:
        filtered = [b for b in filtered if b.distance >= min_distance]

    # 2. 점수 계산
    scored: list[tuple[float, Bakery]] = []
    for bakery in filtered:
        score = 0.0

        if mood and mood in bakery.mood:
            score += 2
        if purpose and (purpose in bakery.purpose or purpose in bakery.tags):
            score += 2
        if price_range and bakery.price_range == price_range:
            score += 1

        # 거리 보너스: 가까울수록 높은 점수 (최대 +3)
        if max_distance and max_distance > 0:
            score += max(0, (max_distance - bakery.distance) / max_distance) * 3

        # 랜덤 요소: 결과 다양화 (문정동 빵집들이 밀집해 있어 점수차가 작으므로 폭 넓게)
        score += random.uniform(0, 1.5)

        scored.append((score, bakery))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [bakery for _, bakery in scored[:max_results]]
