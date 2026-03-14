class TestBakeriesAPI:
    def test_get_all_bakeries(self, client):
        response = client.get("/api/bakeries")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

    def test_get_bakery_by_id(self, client):
        response = client.get("/api/bakeries/1")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1

    def test_get_bakery_not_found(self, client):
        response = client.get("/api/bakeries/9999")
        assert response.status_code == 404


class TestRecommendAPI:
    def test_recommend_no_filter(self, client):
        response = client.post("/api/recommend", json={})
        assert response.status_code == 200
        data = response.json()
        assert "bakeries" in data
        assert "total" in data

    def test_recommend_with_mood(self, client):
        response = client.post("/api/recommend", json={"mood": "아늑한"})
        assert response.status_code == 200
        data = response.json()
        assert len(data["bakeries"]) > 0

    def test_recommend_with_purpose(self, client):
        response = client.post("/api/recommend", json={"purpose": "브런치"})
        assert response.status_code == 200

    def test_recommend_with_all_filters(self, client):
        response = client.post(
            "/api/recommend",
            json={"mood": "아늑한", "purpose": "브런치", "price_range": "일반"},
        )
        assert response.status_code == 200

    def test_recommend_with_parking(self, client):
        response = client.post(
            "/api/recommend", json={"parking": True}
        )
        assert response.status_code == 200
        data = response.json()
        for bakery in data["bakeries"]:
            assert bakery["parking"] is True

    def test_recommend_with_custom_order(self, client):
        response = client.post(
            "/api/recommend", json={"custom_order": True}
        )
        assert response.status_code == 200
        data = response.json()
        for bakery in data["bakeries"]:
            assert bakery["custom_order"] is True

    def test_recommend_with_max_distance(self, client):
        response = client.post(
            "/api/recommend", json={"max_distance": 0.5}
        )
        assert response.status_code == 200
        data = response.json()
        for bakery in data["bakeries"]:
            assert bakery["distance"] <= 0.5

    def test_recommend_with_all_new_filters(self, client):
        response = client.post(
            "/api/recommend",
            json={
                "mood": "아늑한",
                "parking": True,
                "custom_order": True,
                "max_distance": 2.0,
            },
        )
        assert response.status_code == 200


class TestHTMLPages:
    def test_index_page(self, client):
        response = client.get("/")
        assert response.status_code == 200
        assert "문정동" in response.text

    def test_index_has_welcome_message(self, client):
        response = client.get("/")
        assert "우주에서 온 빵친구" in response.text

    def test_index_has_help_section(self, client):
        response = client.get("/")
        assert "지구 빵 튜토리얼" in response.text

    def test_index_has_universe_button(self, client):
        response = client.get("/")
        assert "내 취향 저격 빵집 찾기" in response.text

    def test_results_has_warm_header(self, client):
        response = client.post(
            "/recommend", data={"mood": "", "purpose": "", "price_range": ""}
        )
        assert response.status_code == 200
        assert "당신을 위해 고른" in response.text

    def test_results_has_invitation_message(self, client):
        response = client.post(
            "/recommend", data={"mood": "", "purpose": "", "price_range": ""}
        )
        assert response.status_code == 200
        assert "invitation-message" in response.text

    def test_results_has_flavor_profile(self, client):
        response = client.get("/bakery/1")
        assert response.status_code == 200
        assert "flavor-profile" in response.text

    def test_results_back_link_text(self, client):
        response = client.post(
            "/recommend", data={"mood": "", "purpose": "", "price_range": ""}
        )
        assert "다른 빵집도 궁금하다면" in response.text

    def test_index_has_parking_checkbox(self, client):
        response = client.get("/")
        assert 'name="parking"' in response.text

    def test_index_has_custom_order_checkbox(self, client):
        response = client.get("/")
        assert 'name="custom_order"' in response.text

    def test_index_has_distance_select(self, client):
        response = client.get("/")
        assert 'name="max_distance"' in response.text

    def test_recommend_form_with_parking(self, client):
        response = client.post(
            "/recommend",
            data={"mood": "", "purpose": "", "price_range": "", "parking": "on"},
        )
        assert response.status_code == 200
        # 주차 가능한 베이커리만 결과에 포함
        assert "당신을 위해 고른" in response.text

    def test_recommend_form_with_distance(self, client):
        response = client.post(
            "/recommend",
            data={
                "mood": "",
                "purpose": "",
                "price_range": "",
                "max_distance": "0.5",
            },
        )
        assert response.status_code == 200

    def test_results_shows_parking_info(self, client):
        response = client.post(
            "/recommend", data={"mood": "", "purpose": "", "price_range": ""}
        )
        assert "주차" in response.text

    def test_results_shows_distance_info(self, client):
        response = client.post(
            "/recommend", data={"mood": "", "purpose": "", "price_range": ""}
        )
        assert "문정역" in response.text

    def test_sensory_page(self, client):
        response = client.get("/sensory")
        assert response.status_code == 200
        assert "감각으로 찾기" in response.text

    def test_sensory_has_three_questions(self, client):
        response = client.get("/sensory")
        assert "바삭" in response.text
        assert "달콤" in response.text
        assert "혼자" in response.text

    def test_sensory_form_submit(self, client):
        response = client.post(
            "/sensory",
            data={"texture": "바삭", "taste": "달콤", "atmosphere": "혼자"},
        )
        assert response.status_code == 200
        assert "당신을 위해 고른" in response.text

    def test_results_has_map(self, client):
        response = client.post(
            "/recommend", data={"mood": "", "purpose": "", "price_range": ""}
        )
        assert response.status_code == 200
        assert "bakery-map" in response.text

    def test_bakery_api_has_coordinates(self, client):
        response = client.get("/api/bakeries/1")
        data = response.json()
        assert "lat" in data
        assert "lon" in data
        assert data["lat"] != 0.0
        assert data["lon"] != 0.0

    def test_404_page(self, client):
        response = client.get("/nonexistent-page")
        assert response.status_code == 404
        assert "이 빵집은 아직 이 우주에 없어요" in response.text

    def test_bakery_detail_page(self, client):
        response = client.get("/bakery/1")
        assert response.status_code == 200
        assert "더 브레드 레지던스" in response.text
        assert "소금빵" in response.text

    def test_bakery_detail_has_reviews(self, client):
        response = client.get("/bakery/1")
        assert response.status_code == 200
        assert "방문자 리뷰" in response.text

    def test_bakery_detail_not_found(self, client):
        response = client.get("/bakery/9999")
        assert response.status_code == 404
