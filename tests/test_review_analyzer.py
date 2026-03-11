from app.review_analyzer import extract_tags


class TestExtractTags:
    def test_extract_quiet_tag(self):
        reviews = ["조용하고 집중하기 좋아요", "노트북 작업하기 좋은 곳"]
        tags = extract_tags(reviews)
        assert "조용한" in tags

    def test_extract_dessert_tag(self):
        reviews = ["디저트가 정말 맛있어요", "케이크 추천합니다"]
        tags = extract_tags(reviews)
        assert "디저트맛집" in tags

    def test_extract_multiple_tags(self):
        reviews = ["커피가 맛있고 조용해요", "디저트도 괜찮아요", "가성비 좋아요"]
        tags = extract_tags(reviews)
        assert len(tags) >= 2

    def test_empty_reviews(self):
        tags = extract_tags([])
        assert tags == []

    def test_no_matching_keywords(self):
        reviews = ["그냥 그래요"]
        tags = extract_tags(reviews)
        assert tags == []

    def test_extract_cozy_tag(self):
        reviews = ["아늑하고 분위기 좋아요"]
        tags = extract_tags(reviews)
        assert "아늑한" in tags

    def test_extract_coffee_tag(self):
        reviews = ["커피 맛집이에요", "원두가 정말 좋아요"]
        tags = extract_tags(reviews)
        assert "커피맛집" in tags

    def test_extract_value_tag(self):
        reviews = ["가성비가 최고예요", "가격 대비 만족"]
        tags = extract_tags(reviews)
        assert "가성비좋은" in tags
