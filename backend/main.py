import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.db.database import init_db
from app.routers import chat, dashboard, market, news, portfolio, recommendations, watchlist

logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(asctime)s %(levelname)-8s %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
for noisy_logger in ("httpx", "httpcore", "yfinance", "sqlalchemy", "openrouter"):
    logging.getLogger(noisy_logger).setLevel(logging.WARNING)

log = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info("Starting %s", settings.app_name)
    await init_db()
    log.info("Database initialized")
    yield
    log.info("Shutting down %s", settings.app_name)


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(portfolio.router, prefix="/api")
app.include_router(market.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
app.include_router(news.router, prefix="/api")
app.include_router(recommendations.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")
app.include_router(watchlist.router, prefix="/api")


@app.get("/api/health")
async def health():
    return {"status": "ok", "app": settings.app_name}


@app.get("/api/models")
async def available_models():
    return {
        "default": settings.default_model,
        "models": [
            {"id": "openrouter/free", "name": "Auto (Free)"},
            {"id": "google/gemma-4-26b-a4b-it:free", "name": "Gemma 4 26B"},
            {"id": "google/gemma-3-12b-it:free", "name": "Gemma 3 12B"},
            {"id": "nvidia/nemotron-3-super-120b-a12b:free", "name": "Nemotron 120B"},
            {"id": "deepseek/deepseek-chat-v3-0324:free", "name": "DeepSeek V3"},
            {"id": "meta-llama/llama-4-maverick:free", "name": "Llama 4 Maverick"},
        ],
    }
