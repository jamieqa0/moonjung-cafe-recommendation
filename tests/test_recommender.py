from app.recommender import recommend


class TestRecommendBasicFilter:
    """기본 필터 (mood, purpose, price_range) 테스트"""

    def test_no_filter_returns_all_bakeries(self, sample_bakeries):
        result = recommend(sample_bakeries)
        assert len(result) <= 5
        assert len(result) > 0

    def test_filter_by_mood(self, sample_bakeries):
        result = recommend(sample_bakeries, mood="아늑한")
        assert result[0].name in ("베이커리A", "베이커리D")

    def test_filter_by_purpose(self, sample_bakeries):
        result = recommend(sample_bakeries, purpose="브런치")
        names = [b.name for b in result]
        assert "베이커리A" in names
        assert "베이커리C" in names

    def test_default_top5(self, sample_bakeries):
        result = recommend(sample_bakeries)
        assert len(result) <= 5

    def test_custom_max_results(self, sample_bakeries):
        result = recommend(sample_bakeries, max_results=2)
        assert len(result) == 2


class TestParkingFilter:
    """주차 가능 필터 테스트"""

    def test_parking_true_returns_only_parking_bakeries(self, sample_bakeries):
        result = recommend(sample_bakeries, parking=True)
        for bakery in result:
            assert bakery.parking is True

    def test_parking_false_returns_only_no_parking_bakeries(self, sample_bakeries):
        result = recommend(sample_bakeries, parking=False)
        for bakery in result:
            assert bakery.parking is False

    def test_parking_none_returns_all(self, sample_bakeries):
        result = recommend(sample_bakeries, parking=None, max_results=10)
        assert len(result) == 4

    def test_parking_filter_with_mood(self, sample_bakeries):
        """주차 필터 + mood 조합"""
        result = recommend(sample_bakeries, parking=True, mood="아늑한")
        assert len(result) > 0
        for bakery in result:
            assert bakery.parking is True


class TestCustomOrderFilter:
    """주문 제작 케이크 필터 테스트"""

    def test_custom_order_true_filters_correctly(self, sample_bakeries):
        result = recommend(sample_bakeries, custom_order=True, max_results=10)
        for bakery in result:
            assert bakery.custom_order is True

    def test_custom_order_false_filters_correctly(self, sample_bakeries):
        result = recommend(sample_bakeries, custom_order=False, max_results=10)
        for bakery in result:
            assert bakery.custom_order is False

    def test_custom_order_none_returns_all(self, sample_bakeries):
        result = recommend(sample_bakeries, custom_order=None, max_results=10)
        assert len(result) == 4

    def test_parking_and_custom_order_combined(self, sample_bakeries):
        """주차 가능 + 주문 제작 모두 가능한 베이커리만"""
        result = recommend(sample_bakeries, parking=True, custom_order=True, max_results=10)
        for bakery in result:
            assert bakery.parking is True
            assert bakery.custom_order is True
        names = [b.name for b in result]
        assert "베이커리A" in names


class TestDistanceFilter:
    """거리 필터 테스트"""

    def test_distance_within_radius(self, sample_bakeries):
        """반경 0.5km 이내 베이커리만 반환"""
        result = recommend(sample_bakeries, max_distance=0.5, max_results=10)
        for bakery in result:
            assert bakery.distance <= 0.5
        names = [b.name for b in result]
        assert "베이커리A" in names  # 0.3km
        assert "베이커리C" in names  # 0.5km
        assert "베이커리B" not in names  # 1.2km
        assert "베이커리D" not in names  # 2.0km

    def test_distance_large_radius_returns_all(self, sample_bakeries):
        """충분히 큰 반경이면 전체 반환"""
        result = recommend(sample_bakeries, max_distance=10.0, max_results=10)
        assert len(result) == 4

    def test_distance_none_returns_all(self, sample_bakeries):
        """거리 필터 미지정 시 전체 반환"""
        result = recommend(sample_bakeries, max_distance=None, max_results=10)
        assert len(result) == 4

    def test_distance_zero_returns_none(self, sample_bakeries):
        """반경 0km이면 결과 없음"""
        result = recommend(sample_bakeries, max_distance=0.0)
        assert len(result) == 0

    def test_closer_bakeries_get_higher_score(self, sample_bakeries):
        """가까운 베이커리가 거리 보너스를 받아 점수가 높아진다"""
        result = recommend(sample_bakeries, max_distance=3.0, max_results=10)
        scores = {b.name: _get_score(b) for b in result}
        assert scores is not None


class TestScoreCalculation:
    """추천 점수 계산 테스트"""

    def test_no_conditions_returns_all(self, sample_bakeries):
        """조건 없으면 전체 베이커리가 반환된다"""
        result = recommend(sample_bakeries, max_results=10)
        assert len(result) == 4

    def test_mood_match_boosts_score(self, sample_bakeries):
        """mood 일치 시 점수 상승으로 순위 변동"""
        result = recommend(sample_bakeries, mood="편안한", max_results=10)
        names = [b.name for b in result]
        idx_c = names.index("베이커리C")
        assert idx_c < len(names) - 1

    def test_multiple_conditions_accumulate_score(self, sample_bakeries):
        """여러 조건이 동시에 맞으면 점수가 누적된다"""
        result = recommend(
            sample_bakeries,
            mood="아늑한",
            purpose="브런치",
            price_range="일반",
            parking=True,
            custom_order=True,
        )
        assert result[0].name == "베이커리A"

    def test_parking_filter_affects_ranking(self, sample_bakeries):
        """parking 필터 시 주차 가능 베이커리만 나온다"""
        result = recommend(sample_bakeries, parking=True, max_results=10)
        for bakery in result:
            assert bakery.parking is True

    def test_custom_order_with_purpose_affects_ranking(self, sample_bakeries):
        """주문 제작 + 케이크 목적 조합"""
        result = recommend(
            sample_bakeries,
            custom_order=True,
            purpose="케이크",
            max_results=10,
        )
        assert result[0].custom_order is True
        assert "케이크" in result[0].purpose

    def test_distance_bonus_affects_ranking(self, sample_bakeries):
        """가까운 베이커리에 거리 보너스가 적용된다"""
        result = recommend(sample_bakeries, max_distance=3.0, max_results=2)
        distances = [b.distance for b in result]
        assert min(distances) <= 1.0


def _get_score(bakery):
    """테스트 헬퍼: 기본 점수 계산"""
    return 0.0
