from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, select
from contextlib import asynccontextmanager
from datetime import datetime
from .config.database import (
    async_engine,
    AsyncSessionLocal,
    close_db,
    get_db,
)
from .routers import news


app = FastAPI(title="新闻平台项目", version="1.0.0")

app.include_router(news.router)


# ---------- 基础路由 ----------
@app.get("/")
async def root():
    return {"message": "Hello from FastAPI!", "status": "running"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}

