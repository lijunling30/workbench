"""漫镜工场（ManJu Studio）后端入口。

技术栈：Python FastAPI + SQLAlchemy + SQLite（MVP）。
架构：L2 应用服务层；AI 调用统一经 L4 网关（services/ai_gateway）。
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .database import init_db
from .routers import ai, assets, auth, characters, content, costs, projects


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="AI 漫剧工业化生产平台 API（PRD v1.3）",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # MVP 开发期放开，生产按域名收紧
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

for r in (auth, projects, ai, content, characters, assets, costs):
    app.include_router(r.router, prefix=settings.api_prefix)


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "app": settings.app_name,
        "ai_mode": settings.ai_mode,
        "gate_high_cost_threshold": settings.gate_high_cost_threshold,
    }
