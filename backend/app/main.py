from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, select
from contextlib import asynccontextmanager
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware
from .config.database import (
    async_engine,
    AsyncSessionLocal,
    close_db,
    get_db,
)
from .schemas import users
from .routers import news,users,favorite,history,ai
from .utils.exception_handler import register_exception
from .services.rag import build_news_index


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期：启动时构建 RAG 索引，关闭时清理资源"""
    # 启动：加载新闻构建检索索引
    async with AsyncSessionLocal() as session:
        try:
            chunk_count = await build_news_index(session)
            print(f"[RAG] 索引构建完成，共 {chunk_count} 个 chunk")
        except Exception as e:
            print(f"[RAG] 索引构建失败（服务仍可启动）: {e}")
    yield
    # 关闭：无需额外清理（数据库连接由 close_db 处理）


app = FastAPI(
    title="新闻平台项目",
    version="1.0.0",
    lifespan=lifespan,
)

register_exception(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],    #允许的源，开发中，后面实战不能这样写，
    allow_credentials=True, # 允许携带 Cookie
    allow_methods=["*"],    # 允许的请求方法
    allow_headers=["*"],    # 允许的请求头
)
app.include_router(news.router)
app.include_router(users.router)
app.include_router(favorite.router)
app.include_router(history.router)
app.include_router(ai.router)
# ---------- 基础路由 ----------
@app.get("/")
async def root():
    return {"message": "Hello from FastAPI!", "status": "running"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}

