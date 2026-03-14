import pytest
from pydantic import ValidationError

from app.models import Bakery, RecommendRequest


class TestBakery:
    def test_create_bakery(self):
        bakery = Bakery(
            id=1,
            name="테스트베이커리",
            address="문정동 100",
            mood=["아늑한"],
            purpose=["브런치"],
            signature_menu="소금빵",
            price_range="일반",

            description="테스트용 베이커리",
        )
        assert bakery.name == "테스트베이커리"
        assert bakery.reviews == []
        assert bakery.tags == []

    def test_bakery_with_reviews(self):
        bakery = Bakery(
            id=1,
            name="테스트베이커리",
            address="문정동 100",
            mood=["아늑한"],
            purpose=["브런치"],
            signature_menu="소금빵",
            price_range="일반",

            description="테스트용",
            reviews=["맛있어요", "또 올게요"],
        )
        assert len(bakery.reviews) == 2

    def test_bakery_missing_required_field(self):
        with pytest.raises(ValidationError):
            Bakery(id=1, name="테스트베이커리")


class TestRecommendRequest:
    def test_empty_request(self):
        req = RecommendRequest()
        assert req.mood is None
        assert req.purpose is None
        assert req.price_range is None

    def test_partial_request(self):
        req = RecommendRequest(mood="아늑한")
        assert req.mood == "아늑한"
        assert req.purpose is None
