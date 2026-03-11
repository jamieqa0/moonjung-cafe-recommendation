from pathlib import Path

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.data import CAFES
from app.recommender import recommend
from app.routers import cafes, recommend as recommend_router

BASE_DIR = Path(__file__).resolve().parent.parent

app = FastAPI(title="문정동 카페 추천")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")

app.include_router(cafes.router)
app.include_router(recommend_router.router)


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/recommend", response_class=HTMLResponse)
def recommend_page(
    request: Request,
    mood: str = Form(""),
    purpose: str = Form(""),
    price_range: str = Form(""),
):
    results = recommend(
        CAFES,
        mood=mood or None,
        purpose=purpose or None,
        price_range=price_range or None,
    )
    return templates.TemplateResponse(
        "results.html", {"request": request, "cafes": results}
    )
