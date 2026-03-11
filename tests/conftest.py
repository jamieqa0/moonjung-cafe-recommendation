import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models import Cafe


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def sample_cafes() -> list[Cafe]:
    return [
        Cafe(
            id=1,
            name="카페A",
            address="문정동 1",
            mood=["조용한", "모던한"],
            purpose=["작업"],
            signature_menu="아메리카노",
            price_range="중가",
            rating=4.5,
            description="조용한 작업 카페",
            reviews=["커피가 맛있고 조용해요", "노트북 작업하기 좋아요"],
            quiet=True,
            power_socket=True,
            distance=0.3,
        ),
        Cafe(
            id=2,
            name="카페B",
            address="문정동 2",
            mood=["아늑한"],
            purpose=["대화", "데이트"],
            signature_menu="딸기라떼",
            price_range="고가",
            rating=4.2,
            description="분위기 좋은 데이트 카페",
            reviews=["분위기가 너무 좋아요", "디저트가 맛있어요"],
            quiet=False,
            power_socket=False,
            distance=1.2,
        ),
        Cafe(
            id=3,
            name="카페C",
            address="문정동 3",
            mood=["활기찬"],
            purpose=["대화", "디저트"],
            signature_menu="크로플",
            price_range="저가",
            rating=3.8,
            description="저렴한 디저트 카페",
            reviews=["가성비 최고", "크로플이 맛있어요"],
            quiet=False,
            power_socket=True,
            distance=0.5,
        ),
        Cafe(
            id=4,
            name="카페D",
            address="문정동 4",
            mood=["조용한"],
            purpose=["작업"],
            signature_menu="드립커피",
            price_range="고가",
            rating=4.7,
            description="프리미엄 조용한 작업 카페",
            reviews=["집중하기 최고예요"],
            quiet=True,
            power_socket=True,
            distance=2.0,
        ),
    ]
