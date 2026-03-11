from app.models import Cafe


def recommend(
    cafes: list[Cafe],
    mood: str | None = None,
    purpose: str | None = None,
    price_range: str | None = None,
    quiet: bool | None = None,
    power_socket: bool | None = None,
    max_distance: float | None = None,
    max_results: int = 3,
) -> list[Cafe]:
    # 1. 불리언/거리 필터링
    filtered = cafes
    if quiet is not None:
        filtered = [c for c in filtered if c.quiet == quiet]
    if power_socket is not None:
        filtered = [c for c in filtered if c.power_socket == power_socket]
    if max_distance is not None:
        filtered = [c for c in filtered if c.distance <= max_distance]

    # 2. 점수 계산
    scored: list[tuple[float, Cafe]] = []
    for cafe in filtered:
        score = cafe.rating * 0.5

        if mood and mood in cafe.mood:
            score += 2
        if purpose and purpose in cafe.purpose:
            score += 2
        if price_range and cafe.price_range == price_range:
            score += 1

        # 거리 보너스: 가까울수록 높은 점수
        if max_distance and max_distance > 0:
            score += max(0, (max_distance - cafe.distance) / max_distance)

        scored.append((score, cafe))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [cafe for _, cafe in scored[:max_results]]
