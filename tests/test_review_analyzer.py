from app.review_analyzer import extract_tags, generate_fallback_tags


class TestExtractTags:
    def test_extract_cake_tag(self):
        reviews = ["케이크가 너무 예뻐요", "생크림이 부드러워요"]
        tags = extract_tags(reviews)
        assert "케이크맛집" in tags

    def test_extract_multiple_tags(self):
        reviews = ["빵이 맛있고", "케이크도 훌륭해요", "가성비 좋아요"]
        tags = extract_tags(reviews)
        assert len(tags) >= 2

    def test_empty_reviews(self):
        tags = extract_tags([])
        assert tags == []

    def test_no_matching_keywords(self):
        reviews = ["그냥 그래요"]
        tags = extract_tags(reviews)
        assert tags == []

    def test_extract_cozy_tag(self):
        reviews = ["아늑하고 따뜻한 분위기예요"]
        tags = extract_tags(reviews)
        assert "아늑한" in tags

    def test_extract_value_tag(self):
        reviews = ["가성비가 최고예요", "가격 대비 만족"]
        tags = extract_tags(reviews)
        assert "가성비좋은" in tags

    def test_extract_gift_tag(self):
        reviews = ["선물용으로 포장해줘요", "예쁜 박스에 담아줘요"]
        tags = extract_tags(reviews)
        assert "선물하기좋은" in tags

    def test_extract_salt_bread_tag(self):
        reviews = ["소금빵이 진짜 맛있어요", "얼그레이 소금빵 또 먹고싶다"]
        tags = extract_tags(reviews)
        assert "소금빵맛집" in tags

    def test_extract_cookie_tag(self):
        reviews = ["쿠키가 엄청 맛있어요", "타르트도 추천"]
        tags = extract_tags(reviews)
        assert "쿠키맛집" in tags

    def test_extract_canele_is_cookie_tag(self):
        reviews = ["까눌레 맛집임"]
        tags = extract_tags(reviews)
        assert "쿠키맛집" in tags

    def test_extract_bagel_tag(self):
        reviews = ["베이글 너무 맛있어요 쫄깃하고 고소해요"]
        tags = extract_tags(reviews)
        assert "베이글맛집" in tags

    def test_extract_kind_staff_tag(self):
        reviews = ["직원이 친절합니다", "친절하고 분위기 좋아요"]
        tags = extract_tags(reviews)
        assert "친절한" in tags

    def test_extract_baguette_is_meal_bread(self):
        reviews = ["바게트가 진짜 맛있어요", "명란바게트 추천"]
        tags = extract_tags(reviews)
        assert "식사빵" in tags

    def test_extract_openrun_is_waiting(self):
        reviews = ["오픈런 필수인 집", "조기마감되니 일찍 가세요"]
        tags = extract_tags(reviews)
        assert "줄서는집" in tags


class TestGenerateFallbackTags:
    def test_mood_mapping(self):
        tags = generate_fallback_tags(["아늑한"], [])
        assert "아늑한" in tags

    def test_purpose_mapping(self):
        tags = generate_fallback_tags([], ["브런치", "선물"])
        assert "브런치맛집" in tags
        assert "선물하기좋은" in tags

    def test_combined_mood_purpose(self):
        tags = generate_fallback_tags(["편안한", "대형빵집"], [])
        assert "동네 단골" in tags
        assert "대형빵집" in tags
        assert "빵맛집" not in tags

    def test_no_duplicates(self):
        tags = generate_fallback_tags(["편안한", "동네 단골"], [])
        assert tags.count("동네 단골") == 1

    def test_empty_inputs(self):
        tags = generate_fallback_tags([], [])
        assert tags == []

    def test_unmapped_values_ignored(self):
        tags = generate_fallback_tags(["알수없는분위기"], ["모임"])
        assert tags == []

    def test_modern_mood_no_tag(self):
        """모던한 mood 단독으로는 태그 없음 — 모든 빵집이 빵맛집이므로"""
        tags = generate_fallback_tags(["모던한"], [])
        assert "빵맛집" not in tags

    def test_emotional_mood_mapping(self):
        tags = generate_fallback_tags(["감성적인"], [])
        assert "선물하기좋은" in tags
