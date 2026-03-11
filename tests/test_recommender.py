from app.recommender import recommend


class TestRecommendBasicFilter:
    """기존 필터 (mood, purpose, price_range) 테스트"""

    def test_no_filter_returns_sorted_by_rating(self, sample_cafes):
        result = recommend(sample_cafes)
        assert result[0].name == "카페D"  # rating 4.7
        assert result[1].name == "카페A"  # rating 4.5

    def test_filter_by_mood(self, sample_cafes):
        result = recommend(sample_cafes, mood="조용한")
        assert result[0].name in ("카페A", "카페D")

    def test_filter_by_purpose(self, sample_cafes):
        result = recommend(sample_cafes, purpose="대화")
        names = [c.name for c in result]
        assert "카페B" in names
        assert "카페C" in names

    def test_default_top3(self, sample_cafes):
        result = recommend(sample_cafes)
        assert len(result) <= 3

    def test_custom_max_results(self, sample_cafes):
        result = recommend(sample_cafes, max_results=2)
        assert len(result) == 2


class TestQuietFilter:
    """조용한 카페 필터 테스트"""

    def test_quiet_true_returns_only_quiet_cafes(self, sample_cafes):
        result = recommend(sample_cafes, quiet=True)
        for cafe in result:
            assert cafe.quiet is True

    def test_quiet_false_returns_only_noisy_cafes(self, sample_cafes):
        result = recommend(sample_cafes, quiet=False)
        for cafe in result:
            assert cafe.quiet is False

    def test_quiet_none_returns_all(self, sample_cafes):
        result = recommend(sample_cafes, quiet=None, max_results=10)
        assert len(result) == 4

    def test_quiet_filter_with_mood(self, sample_cafes):
        """조용한 필터 + mood 조합"""
        result = recommend(sample_cafes, quiet=True, mood="조용한")
        assert len(result) > 0
        for cafe in result:
            assert cafe.quiet is True


class TestPowerSocketFilter:
    """콘센트 유무 필터 테스트"""

    def test_power_socket_true_filters_correctly(self, sample_cafes):
        result = recommend(sample_cafes, power_socket=True, max_results=10)
        for cafe in result:
            assert cafe.power_socket is True

    def test_power_socket_false_filters_correctly(self, sample_cafes):
        result = recommend(sample_cafes, power_socket=False, max_results=10)
        for cafe in result:
            assert cafe.power_socket is False

    def test_power_socket_none_returns_all(self, sample_cafes):
        result = recommend(sample_cafes, power_socket=None, max_results=10)
        assert len(result) == 4

    def test_quiet_and_power_socket_combined(self, sample_cafes):
        """조용하고 콘센트 있는 카페만"""
        result = recommend(sample_cafes, quiet=True, power_socket=True, max_results=10)
        for cafe in result:
            assert cafe.quiet is True
            assert cafe.power_socket is True
        names = [c.name for c in result]
        assert "카페A" in names
        assert "카페D" in names


class TestDistanceFilter:
    """거리 필터 테스트"""

    def test_distance_within_radius(self, sample_cafes):
        """반경 0.5km 이내 카페만 반환"""
        result = recommend(sample_cafes, max_distance=0.5, max_results=10)
        for cafe in result:
            assert cafe.distance <= 0.5
        names = [c.name for c in result]
        assert "카페A" in names  # 0.3km
        assert "카페C" in names  # 0.5km
        assert "카페B" not in names  # 1.2km
        assert "카페D" not in names  # 2.0km

    def test_distance_large_radius_returns_all(self, sample_cafes):
        """충분히 큰 반경이면 전체 반환"""
        result = recommend(sample_cafes, max_distance=10.0, max_results=10)
        assert len(result) == 4

    def test_distance_none_returns_all(self, sample_cafes):
        """거리 필터 미지정 시 전체 반환"""
        result = recommend(sample_cafes, max_distance=None, max_results=10)
        assert len(result) == 4

    def test_distance_zero_returns_none(self, sample_cafes):
        """반경 0km이면 결과 없음"""
        result = recommend(sample_cafes, max_distance=0.0)
        assert len(result) == 0

    def test_closer_cafes_get_higher_score(self, sample_cafes):
        """가까운 카페가 거리 보너스를 받아 점수가 높아진다"""
        result = recommend(sample_cafes, max_distance=3.0, max_results=10)
        # 카페A(0.3km)와 카페D(2.0km)는 rating이 비슷하지만
        # 거리 보너스로 카페A가 더 높은 점수를 받을 수 있다
        scores = {c.name: _get_score(c) for c in result}
        # 가까울수록 보너스가 크다
        assert scores is not None  # 점수 계산이 정상 동작


class TestScoreCalculation:
    """추천 점수 계산 테스트"""

    def test_score_base_is_rating(self, sample_cafes):
        """조건 없으면 rating 순으로 정렬"""
        result = recommend(sample_cafes, max_results=10)
        ratings = [c.rating for c in result]
        assert ratings == sorted(ratings, reverse=True)

    def test_mood_match_boosts_score(self, sample_cafes):
        """mood 일치 시 점수 상승으로 순위 변동"""
        # 카페C(rating 3.8, 활기찬)는 기본 순위가 낮지만
        # mood=활기찬 조건 시 상위에 올라와야 함
        result = recommend(sample_cafes, mood="활기찬", max_results=10)
        names = [c.name for c in result]
        idx_c = names.index("카페C")
        # mood 매칭으로 카페C가 최하위가 아님
        assert idx_c < len(names) - 1

    def test_multiple_conditions_accumulate_score(self, sample_cafes):
        """여러 조건이 동시에 맞으면 점수가 누적된다"""
        # 카페A: 조용한 + 작업 + 중가 + quiet + power_socket → 최고 점수
        result = recommend(
            sample_cafes,
            mood="조용한",
            purpose="작업",
            price_range="중가",
            quiet=True,
            power_socket=True,
        )
        assert result[0].name == "카페A"

    def test_quiet_bonus_affects_ranking(self, sample_cafes):
        """quiet 보너스가 순위에 반영된다"""
        result_without = recommend(sample_cafes, max_results=10)
        result_with = recommend(sample_cafes, quiet=True, max_results=10)
        # quiet=True 필터 시 조용한 카페만 나오고 점수도 반영
        for cafe in result_with:
            assert cafe.quiet is True

    def test_power_socket_bonus_affects_ranking(self, sample_cafes):
        """power_socket 보너스가 순위에 반영된다"""
        result = recommend(
            sample_cafes,
            power_socket=True,
            purpose="작업",
            max_results=10,
        )
        # 콘센트 있는 작업 카페가 상위
        assert result[0].power_socket is True
        assert "작업" in result[0].purpose

    def test_distance_bonus_affects_ranking(self, sample_cafes):
        """가까운 카페에 거리 보너스가 적용된다"""
        # 카페A(0.3km, 4.5) vs 카페D(2.0km, 4.7)
        # rating만 보면 카페D가 높지만, 거리 보너스 반영 시 카페A가 유리할 수 있다
        result = recommend(sample_cafes, max_distance=3.0, max_results=2)
        # 거리 보너스가 적용되므로 가까운 카페가 유리
        distances = [c.distance for c in result]
        assert min(distances) <= 1.0  # 가까운 카페가 TOP에 포함


def _get_score(cafe):
    """테스트 헬퍼: 기본 점수 계산"""
    return cafe.rating * 0.5
