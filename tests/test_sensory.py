from app.sensory import map_sensory_to_conditions


class TestSensoryMapping:
    def test_crispy_sweet_alone(self):
        result = map_sensory_to_conditions("바삭", "달콤", "혼자")
        assert result["mood"] == "아늑한"
        assert result["purpose"] == "빵구경"

    def test_crispy_savory_alone(self):
        result = map_sensory_to_conditions("바삭", "고소", "혼자")
        assert result["mood"] == "아늑한"
        assert result["purpose"] == "브런치"

    def test_soft_sweet_together(self):
        result = map_sensory_to_conditions("부드러움", "달콤", "여럿")
        assert result["mood"] == "편안한"
        assert result["purpose"] == "케이크"

    def test_soft_savory_together(self):
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
        assert result["purpose"] == "브런치"

    def test_returns_all_keys(self):
        result = map_sensory_to_conditions("바삭", "달콤", "혼자")
        assert "mood" in result
        assert "purpose" in result
