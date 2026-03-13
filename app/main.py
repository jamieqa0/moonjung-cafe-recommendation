import os
import random
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.data import BAKERIES
from app.recommender import recommend
from app.routers import cafes, recommend as recommend_router
from app.sensory import map_sensory_to_conditions

BASE_DIR = Path(__file__).resolve().parent.parent

app = FastAPI(title="MoonBBang Station")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")

app.include_router(cafes.router)
app.include_router(recommend_router.router)

KAKAO_JS_KEY = os.environ.get("KAKAO_JS_KEY", "")

INVITATION_MESSAGES = [
    "문정동은 항상 여기서 기다릴게요. 또 놀러 오세요.",
    "다음에도 놀러 와. 문정동은 항상 여기 있어.",
    "다음엔 다른 빵도 먹어봐요. 우주 어디서든 다시 환영합니다.",
    "빵은 매일 새로 구워져요. 내일도, 모레도, 언제든 오세요.",
    "오늘의 빵은 오늘뿐이에요. 하지만 내일은 또 새로운 빵이 기다려요.",
]


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/recommend", response_class=HTMLResponse)
def recommend_page(
    request: Request,
    mood: str = Form(""),
    purpose: str = Form(""),
    price_range: str = Form(""),
    parking: str = Form(""),
    custom_order: str = Form(""),
    max_distance: str = Form(""),
):
    results = recommend(
        BAKERIES,
        mood=mood or None,
        purpose=purpose or None,
        price_range=price_range or None,
        parking=True if parking == "on" else None,
        custom_order=True if custom_order == "on" else None,
        max_distance=float(max_distance) if max_distance else None,
    )
    invitation = random.choice(INVITATION_MESSAGES)
    kakao_js_key = os.environ.get("KAKAO_JS_KEY", "")
    return templates.TemplateResponse(
        "results.html",
        {
            "request": request,
            "bakeries": results,
            "invitation": invitation,
            "kakao_js_key": kakao_js_key,
        },
    )


@app.get("/sensory", response_class=HTMLResponse)
def sensory_page(request: Request):
    return templates.TemplateResponse("sensory.html", {"request": request})


@app.post("/sensory", response_class=HTMLResponse)
def sensory_recommend(
    request: Request,
    texture: str = Form("바삭"),
    taste: str = Form("달콤"),
    atmosphere: str = Form("혼자"),
):
    conditions = map_sensory_to_conditions(texture, taste, atmosphere)
    results = recommend(
        BAKERIES,
        mood=conditions["mood"],
        purpose=conditions["purpose"],
    )
    invitation = random.choice(INVITATION_MESSAGES)
    kakao_js_key = os.environ.get("KAKAO_JS_KEY", "")
    return templates.TemplateResponse(
        "results.html",
        {
            "request": request,
            "bakeries": results,
            "invitation": invitation,
            "kakao_js_key": kakao_js_key,
        },
    )


@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return templates.TemplateResponse(
        "404.html", {"request": request}, status_code=404
    )
