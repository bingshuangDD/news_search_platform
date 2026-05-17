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
from .routers import news,users
from .utils.exception_handler import register_exception

app = FastAPI(title="新闻平台项目", version="1.0.0")

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

# ---------- 基础路由 ----------
@app.get("/")
async def root():
    return {"message": "Hello from FastAPI!", "status": "running"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}

