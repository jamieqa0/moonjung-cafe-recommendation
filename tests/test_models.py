import pytest
from pydantic import ValidationError

from app.models import Cafe, RecommendRequest


class TestCafe:
    def test_create_cafe(self):
        cafe = Cafe(
            id=1,
            name="테스트카페",
            address="문정동 100",
            mood=["조용한"],
            purpose=["작업"],
            signature_menu="아메리카노",
            price_range="중가",
            rating=4.0,
            description="테스트용 카페",
        )
        assert cafe.name == "테스트카페"
        assert cafe.reviews == []
        assert cafe.tags == []

    def test_cafe_with_reviews(self):
        cafe = Cafe(
            id=1,
            name="테스트카페",
            address="문정동 100",
            mood=["조용한"],
            purpose=["작업"],
            signature_menu="아메리카노",
            price_range="중가",
            rating=4.0,
            description="테스트용",
            reviews=["좋아요", "맛있어요"],
        )
        assert len(cafe.reviews) == 2

    def test_cafe_missing_required_field(self):
        with pytest.raises(ValidationError):
            Cafe(id=1, name="테스트카페")


class TestRecommendRequest:
    def test_empty_request(self):
        req = RecommendRequest()
        assert req.mood is None
        assert req.purpose is None
        assert req.price_range is None

    def test_partial_request(self):
        req = RecommendRequest(mood="조용한")
        assert req.mood == "조용한"
        assert req.purpose is None
