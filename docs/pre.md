**Python + 웹 + TDD + Claude Code** 조합이면 진행 순서를 잘 잡는 게 중요합니다.
Claude Code(Claude Notebook)를 쓸 때 **가장 효율적인 워크플로우**를 단계별로 정리해 드릴게요.

---

# 🚀 Claude Notebook에서 시작 순서 (추천 워크플로우)

## 1️⃣ 프로젝트 폴더부터 만들기

먼저 Claude에게 **프로젝트 구조 생성**을 시킵니다.

Claude Notebook에 이렇게 입력하세요 👇

```text
Python FastAPI 기반 문정동 카페 추천 웹 서비스를 만들려고 한다.

요구사항
- TDD 기반 개발
- pytest 사용
- FastAPI 웹 API
- 카페 추천 로직 구현
- 리뷰 기반 카페 특징 분석

프로젝트 폴더 구조를 제안해줘.
```

보통 이런 구조가 나옵니다

```text
cafe-recommendation/

app/
  main.py
  router.py
  service/
      recommendation_service.py
      review_analyzer.py
  model/
      cafe.py
      review.py

tests/
  test_recommendation.py
  test_review_analyzer.py

data/
  cafes.json

plan.md
prd.md
```

👉 이걸 Claude Code로 생성

---

# 2️⃣ plan.md 먼저 작성

Claude에게 이렇게 요청

```text
문정동 카페 추천 시스템 개발을 위한 plan.md 작성해줘.

조건
- Python
- FastAPI
- pytest 기반 TDD
- 리뷰 기반 카페 특징 분석
- TOP3 카페 추천
```

plan.md 내용 예시

```markdown
# Cafe Recommendation System Plan

## Goal
문정동 카페를 사용자 목적에 맞게 추천하는 웹 서비스

## Features
1. 카페 데이터 관리
2. 리뷰 분석
3. 사용자 조건 필터링
4. 추천 점수 계산
5. TOP3 추천

## Tech Stack
- Python
- FastAPI
- pytest
- Claude Code

## Development Strategy
TDD 방식으로 개발

1. 테스트 작성
2. 최소 구현
3. 리팩토링
```

---

# 3️⃣ prd.md 작성

Claude에게 요청

```text
문정동 카페 추천 웹서비스 PRD를 작성해줘.

포함
- User Story
- Functional Requirements
- Non Functional Requirements
```

예

```markdown
# PRD

## Problem
문정동에는 카페가 많지만 목적에 맞는 카페 찾기 어려움

## Target User
- 직장인
- 개발자
- 스터디 사용자

## User Stories

US-01
사용자는 조용한 카페를 찾고 싶다

US-02
사용자는 노트북 작업 가능한 카페를 찾고 싶다

US-03
사용자는 디저트 맛집을 찾고 싶다

## Functional Requirements

FR-01 카페 목록 제공  
FR-02 사용자 조건 입력  
FR-03 추천 점수 계산  
FR-04 TOP3 카페 추천

## Non Functional

응답시간 < 1초
```

---

# 4️⃣ TDD 테스트 먼저 만들기

Claude Notebook에 이렇게 입력

```text
pytest 기반으로 카페 추천 로직 테스트 코드를 먼저 작성해줘.

조건
- quiet 카페 필터
- power_socket 필터
- distance 필터
- 추천 점수 계산
```

예

```python
def test_filter_quiet_cafes():
    cafes = [
        {"name": "Cafe A", "noise": 2},
        {"name": "Cafe B", "noise": 5},
    ]

    result = filter_quiet_cafes(cafes)

    assert len(result) == 1
    assert result[0]["name"] == "Cafe A"
```

👉 **QA 직무 포인트 = 테스트 먼저 작성**

---

# 5️⃣ FastAPI 웹 API 만들기

Claude에게 요청

```text
FastAPI 기반 카페 추천 API 만들어줘.

endpoint
/recommend

query
- mood
- power_socket
```

예

```python
@app.get("/recommend")
def recommend(mood: str, power_socket: bool):
    return recommendation_service.recommend(mood, power_socket)
```

---

# 6️⃣ Claude Code에서 추천 Prompt

개발하면서 자주 쓰는 프롬프트

### 테스트 생성

```text
이 코드에 대해 pytest 테스트 코드를 작성해줘
```

---

### TDD 구현

```text
이 테스트를 통과하는 최소 구현 코드를 작성해줘
```

---

### 리팩토링

```text
테스트는 유지하면서 코드를 리팩토링해줘
```

---

# 🧠 QA 직무 어필 포인트 (스터디에서 중요)

발표할 때 이렇게 말하면 좋습니다

```text
QA 관점에서 추천 알고리즘 품질을 보장하기 위해
TDD 기반 테스트를 먼저 작성했습니다.

추천 결과가 사용자 의도와 맞는지 검증하는 테스트를
자동화했습니다.
```

이거 **엄청 좋아합니다.**

---

# ⭐ Claude Notebook에서 처음 입력하면 좋은 프롬프트

이거 그대로 쓰세요 👇

```text
Python FastAPI 기반 문정동 카페 추천 웹 서비스를 만들려고 한다.

요구사항
- pytest 기반 TDD 개발
- 리뷰 기반 카페 특징 분석
- 사용자 조건 기반 추천
- TOP3 카페 추천

먼저 아래 문서를 작성해줘.

1. plan.md
2. prd.md
3. 프로젝트 폴더 구조
```

---

# 🔥 추가 팁 (스터디에서 차별화)

**AI 기능 하나 넣으면 완전 좋아짐**

예

```
리뷰 → AI 분석

"조용하다"
"공부하기 좋다"
"콘센트 많다"

→ feature 생성
```

---

💡 원하면 제가 **스터디에서 진짜 잘 먹히는 설계**도 만들어 줄게요.

예

* **Claude Code 최적 프로젝트 구조**
* **TDD 테스트 10개**
* **문정동 실제 카페 데이터**
* **FastAPI 웹 UI**

까지 **한 번에 설계**해 드릴게요.
(이거 하면 스터디에서 거의 **1등 프로젝트 느낌** 납니다 😎)
