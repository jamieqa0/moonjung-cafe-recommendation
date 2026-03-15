"""공공데이터 로더 및 데이터 무결성 테스트."""

import os
import tempfile

from app.data import BAKERIES, _haversine, _infer_attributes, _load_public_bakeries, _parse_coordinate, _tm_to_wgs84


class TestDataIntegrity:
    def test_all_bakeries_have_coordinates(self):
        for b in BAKERIES:
            if b.id <= 10:  # 시드 데이터만 (리치 데이터)
                assert b.lat != 0.0, f"{b.name}에 위도가 없습니다"
                assert b.lon != 0.0, f"{b.name}에 경도가 없습니다"

    def test_all_bakeries_have_reviews(self):
        for b in BAKERIES:
            if b.id <= 10:  # 시드 데이터만 (리치 데이터)
                assert len(b.reviews) >= 5, f"{b.name}의 리뷰가 5개 미만입니다"

    def test_all_bakeries_have_tags(self):
        for b in BAKERIES:
            if b.id <= 10:  # 시드 데이터만 (리치 데이터)
                assert len(b.tags) > 0, f"{b.name}에 태그가 없습니다"

    def test_bakery_ids_unique(self):
        ids = [b.id for b in BAKERIES]
        assert len(ids) == len(set(ids))

    def test_minimum_bakery_count(self):
        assert len(BAKERIES) >= 10


class TestInferAttributes:
    """_infer_attributes 추론 로직 단위 테스트"""

    def test_hans_is_not_large_bakery(self):
        """한스는 소규모 프랜차이즈 — 대형빵집 mood 없어야 함"""
        result = _infer_attributes("한스 문정점", "제과,베이커리 > 한스")
        assert "대형빵집" not in result["mood"]

    def test_paris_baguette_is_large_bakery(self):
        """파리바게뜨는 대형빵집 mood 포함"""
        result = _infer_attributes("파리바게뜨 문정중앙점", "제과,베이커리 > 파리바게뜨")
        assert "대형빵집" in result["mood"]

    def test_franchise_without_name_clue_uses_default_menu(self):
        """이름에 메뉴 힌트 없는 프랜차이즈는 특정 메뉴를 추측하지 않는다"""
        result = _infer_attributes("파리바게뜨 문정중앙점", "제과,베이커리")
        assert "베이글" not in result["signature_menu"]
        assert "크루아상" not in result["signature_menu"]
        assert "케이크" not in result["signature_menu"]

    def test_hans_uses_default_menu(self):
        """한스는 이름에 메뉴 힌트 없으므로 특정 메뉴를 추측하지 않는다"""
        result = _infer_attributes("한스 문정점", "제과,베이커리 > 한스")
        assert "베이글" not in result["signature_menu"]
        assert "크루아상" not in result["signature_menu"]
        assert "케이크" not in result["signature_menu"]

    def test_name_with_literal_food_infers_menu(self):
        """이름에 메뉴가 직접 포함되면 해당 메뉴로 추론"""
        assert "베이글" in _infer_attributes("베이글집", "")["signature_menu"]
        assert "와플" in _infer_attributes("와플대학 문정캠퍼스", "")["signature_menu"]
        assert "포카치아" in _infer_attributes("포카치아", "")["signature_menu"]

    def test_oegaeyin_bangadan_is_rice_bread(self):
        """외계인방앗간은 쌀빵집 — 떡·한과 아님"""
        result = _infer_attributes("외계인방앗간 문정점", "제과,베이커리")
        assert "쌀빵" in result["signature_menu"]
        assert "떡·한과" not in result["signature_menu"]

    def test_artize_is_premium(self):
        """아티제는 프리미엄 가격대"""
        result = _infer_attributes("아티제 송파아이파크점", "제과,베이커리 > 아티제")
        assert result["price_range"] == "프리미엄"

    def test_sorimsa_is_macaron(self):
        """소림사는 마카롱 브랜드"""
        result = _infer_attributes("소림사 문정점", "제과,베이커리")
        assert "마카롱" in result["signature_menu"]

    def test_cake_shop_inferred(self):
        """이름에 '케이크' 포함 시 케이크 전문점으로 추론"""
        result = _infer_attributes("달콤케이크", "제과,베이커리")
        assert "케이크" in result["purpose"]

    def test_bagel_shop_inferred(self):
        """이름에 '베이글' 포함 시 베이글 전문점으로 추론"""
        result = _infer_attributes("베이글집", "제과,베이커리")
        assert "베이글" in result["signature_menu"]


class TestHaversine:
    def test_same_point_is_zero(self):
        assert _haversine(127.0, 37.0, 127.0, 37.0) == 0.0

    def test_moonjeong_distance(self):
        """문정역에서 약 1km 떨어진 지점 확인."""
        dist = _haversine(127.1264, 37.4857, 127.1264, 37.4947)
        assert 0.9 < dist < 1.1  # 대략 1km


class TestParseCoordinate:
    def test_valid_float(self):
        assert _parse_coordinate("127.1264", 0.0) == 127.1264

    def test_zero_returns_fallback(self):
        assert _parse_coordinate("0", 99.9) == 99.9

    def test_empty_returns_fallback(self):
        assert _parse_coordinate("", 99.9) == 99.9

    def test_none_returns_fallback(self):
        assert _parse_coordinate(None, 99.9) == 99.9


class TestTmToWgs84:
    def test_moonjeong_reference_point(self):
        """기준점 TM(210900, 442400)은 문정역 부근이어야 한다."""
        lon, lat = _tm_to_wgs84(210900, 442400)
        assert abs(lon - 127.1225) < 0.001
        assert abs(lat - 37.4858) < 0.001

    def test_nearby_point(self):
        """문정역 인근 TM 좌표 변환 결과가 합리적이어야 한다."""
        lon, lat = _tm_to_wgs84(210964, 442351)
        assert 127.12 < lon < 127.14
        assert 37.48 < lat < 37.50


class TestPublicDataLoader:
    def test_no_csv_returns_empty(self):
        """CSV 파일이 없으면 빈 리스트를 반환한다."""
        old = os.environ.get("PUBLIC_DATA_SOURCE_PATH")
        os.environ["PUBLIC_DATA_SOURCE_PATH"] = "nonexistent.csv"
        try:
            result = _load_public_bakeries()
            assert result == []
        finally:
            if old is not None:
                os.environ["PUBLIC_DATA_SOURCE_PATH"] = old
            else:
                os.environ.pop("PUBLIC_DATA_SOURCE_PATH", None)

    def test_load_valid_csv(self):
        """올바른 CSV를 읽어서 베이커리 딕셔너리를 반환한다."""
        csv_content = (
            "사업장명,소재지전체주소,상세영업상태명,도로명전체주소,좌표정보(x),좌표정보(y)\n"
            "테스트빵집,서울특별시 송파구 문정동 123,영업,서울특별시 송파구 송파대로 155,210964,442351\n"
            "폐업빵집,서울특별시 송파구 문정동 456,폐업,,,"
        )
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", encoding="utf-8", delete=False
        ) as f:
            f.write(csv_content)
            tmp_path = f.name

        old = os.environ.get("PUBLIC_DATA_SOURCE_PATH")
        os.environ["PUBLIC_DATA_SOURCE_PATH"] = tmp_path
        try:
            result = _load_public_bakeries()
            assert len(result) == 1
            assert result[0]["name"] == "테스트빵집"
            assert result[0]["address"] == "서울특별시 송파구 송파대로 155"  # 도로명 우선
            assert 37.48 < result[0]["lat"] < 37.50  # TM→WGS84 변환됨
            assert 127.12 < result[0]["lon"] < 127.14
            assert result[0]["distance"] > 0  # 거리 계산됨
        finally:
            os.unlink(tmp_path)
            if old is not None:
                os.environ["PUBLIC_DATA_SOURCE_PATH"] = old
            else:
                os.environ.pop("PUBLIC_DATA_SOURCE_PATH", None)

    def test_filters_non_munjeong(self):
        """문정동이 아닌 주소는 필터링된다."""
        csv_content = (
            "사업장명,소재지전체주소,상세영업상태명\n"
            "강남빵집,서울특별시 강남구 역삼동 123,영업\n"
        )
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", encoding="utf-8", delete=False
        ) as f:
            f.write(csv_content)
            tmp_path = f.name

        old = os.environ.get("PUBLIC_DATA_SOURCE_PATH")
        os.environ["PUBLIC_DATA_SOURCE_PATH"] = tmp_path
        try:
            result = _load_public_bakeries()
            assert result == []
        finally:
            os.unlink(tmp_path)
            if old is not None:
                os.environ["PUBLIC_DATA_SOURCE_PATH"] = old
            else:
                os.environ.pop("PUBLIC_DATA_SOURCE_PATH", None)
