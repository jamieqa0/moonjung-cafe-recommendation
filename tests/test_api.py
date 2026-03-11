class TestCafesAPI:
    def test_get_all_cafes(self, client):
        response = client.get("/api/cafes")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

    def test_get_cafe_by_id(self, client):
        response = client.get("/api/cafes/1")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1

    def test_get_cafe_not_found(self, client):
        response = client.get("/api/cafes/9999")
        assert response.status_code == 404


class TestRecommendAPI:
    def test_recommend_no_filter(self, client):
        response = client.post("/api/recommend", json={})
        assert response.status_code == 200
        data = response.json()
        assert "cafes" in data
        assert "total" in data

    def test_recommend_with_mood(self, client):
        response = client.post("/api/recommend", json={"mood": "조용한"})
        assert response.status_code == 200
        data = response.json()
        assert len(data["cafes"]) > 0

    def test_recommend_with_purpose(self, client):
        response = client.post("/api/recommend", json={"purpose": "작업"})
        assert response.status_code == 200

    def test_recommend_with_all_filters(self, client):
        response = client.post(
            "/api/recommend",
            json={"mood": "조용한", "purpose": "작업", "price_range": "중가"},
        )
        assert response.status_code == 200


class TestHTMLPages:
    def test_index_page(self, client):
        response = client.get("/")
        assert response.status_code == 200
        assert "문정동" in response.text
