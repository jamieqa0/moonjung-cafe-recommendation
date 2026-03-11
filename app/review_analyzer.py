KEYWORD_TAG_MAP: dict[str, list[str]] = {
    "조용한": ["조용", "집중", "혼자"],
    "아늑한": ["아늑", "따뜻", "포근"],
    "디저트맛집": ["디저트", "케이크", "마카롱", "크로플", "빵"],
    "커피맛집": ["커피", "원두", "드립", "에스프레소"],
    "가성비좋은": ["가성비", "저렴", "가격 대비"],
    "뷰맛집": ["뷰", "전망", "야경", "창밖"],
    "넓은": ["넓", "공간이 넉넉", "좌석이 많"],
    "작업하기좋은": ["노트북", "작업", "콘센트", "와이파이"],
}


def extract_tags(reviews: list[str]) -> list[str]:
    if not reviews:
        return []

    combined = " ".join(reviews)
    tags = []

    for tag, keywords in KEYWORD_TAG_MAP.items():
        if any(kw in combined for kw in keywords):
            tags.append(tag)

    return tags
