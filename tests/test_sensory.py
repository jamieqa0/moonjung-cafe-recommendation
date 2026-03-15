from app.sensory import map_sensory_to_conditions


class TestSensoryMapping:
    def test_crispy_sweet_alone(self):
        result = map_sensory_to_conditions("바삭", "달콤", "혼자")
        assert result["mood"] == "아늑한"
        assert result["purpose"] is None

    def test_crispy_savory_alone(self):
        # 바삭+고소 = 식사빵 (바게트·캄파뉴 등 담백한 빵)
        result = map_sensory_to_conditions("바삭", "고소", "혼자")
        assert result["mood"] == "아늑한"
        assert result["purpose"] == "식사빵"

    def test_soft_sweet_together(self):
        result = map_sensory_to_conditions("부드러움", "달콤", "여럿")
        assert result["mood"] == "편안한"
        assert result["purpose"] == "케이크"

    def test_soft_savory_together(self):
        # 부드러움+고소 = 브런치 (샌드위치·소프트 식사빵)
        result = map_sensory_to_conditions("부드러움", "고소", "여럿")
        assert result["mood"] == "편안한"
        assert result["purpose"] == "브런치"

    def test_soft_sweet_alone(self):
        result = map_sensory_to_conditions("부드러움", "달콤", "혼자")
        assert result["mood"] == "아늑한"
        assert result["purpose"] == "케이크"

    def test_crispy_savory_together(self):
        result = map_sensory_to_conditions("바삭", "고소", "여럿")
        assert result["mood"] == "편안한"
        assert result["purpose"] == "식사빵"

    def test_returns_all_keys(self):
        result = map_sensory_to_conditions("바삭", "달콤", "혼자")
        assert "mood" in result
        assert "purpose" in result

    # ── None 폴백 — 미매칭 시 필터 미적용 ───────────────────────
    def test_unknown_atmosphere_returns_none_mood(self):
        result = map_sensory_to_conditions("바삭", "달콤", "알수없음")
        assert result["mood"] is None

    def test_unknown_texture_taste_returns_none_purpose(self):
        result = map_sensory_to_conditions("미끌미끌", "쓴맛", "혼자")
        assert result["purpose"] is None

    def test_none_mood_does_not_filter(self):
        """mood가 None이면 recommend()에서 무시되는지 확인 (sensory 경로 통합)"""
        from app.recommender import recommend
        from app.data import BAKERIES
        result = map_sensory_to_conditions("바삭", "달콤", "알수없음")
        # mood=None 이어도 recommend가 정상 동작해야 함
        bakeries = recommend(BAKERIES, mood=result["mood"], purpose=result["purpose"])
        assert len(bakeries) > 0
