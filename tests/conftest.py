import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models import Bakery


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def sample_bakeries() -> list[Bakery]:
    return [
        Bakery(
            id=1,
            name="베이커리A",
            address="문정동 1",
            mood=["아늑한", "모던한"],
            purpose=["브런치"],
            signature_menu="소금빵",
            price_range="일반",

            description="조용한 브런치 베이커리",
            reviews=["소금빵이 맛있어요", "브런치 메뉴가 훌륭해요"],
            parking=True,
            custom_order=True,
            distance=0.3,
        ),
        Bakery(
            id=2,
            name="베이커리B",
            address="문정동 2",
            mood=["감성적인"],
            purpose=["선물", "케이크"],
            signature_menu="딸기 생크림 케이크",
            price_range="프리미엄",

            description="주문 제작 케이크 전문점",
            reviews=["케이크가 예뻐요", "선물 포장이 좋아요"],
            parking=False,
            custom_order=True,
            distance=1.2,
        ),
        Bakery(
            id=3,
            name="베이커리C",
            address="문정동 3",
            mood=["편안한"],
            purpose=["빵구경", "브런치"],
            signature_menu="버터크루아상",
            price_range="일반",

            description="가성비 동네 빵집",
            reviews=["가성비 최고", "크루아상이 맛있어요"],
            parking=False,
            custom_order=False,
            distance=0.5,
        ),
        Bakery(
            id=4,
            name="베이커리D",
            address="문정동 4",
            mood=["모던한"],
            purpose=["빵구경"],
            signature_menu="통밀 캄파뉴",
            price_range="프리미엄",

            description="정통 아티잔 베이커리",
            reviews=["빵 퀄리티가 최고예요"],
            parking=True,
            custom_order=False,
            distance=2.0,
        ),
    ]
