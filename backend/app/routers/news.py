from fastapi import APIRouter,Depends
from datetime import datetime
from ..crud import news
from ..config.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession

"""
新闻模块
"""
router = APIRouter(prefix="/api/news", tags=["news"])  # 同模块前缀相同

@router.get("/categories")
async def get_category(skip: int = 0, limit: int = 100,db: AsyncSession = Depends(get_db)):
    categories=await news.get_category(db,skip, limit)
    return {
        "code": 200,
        "message": "获取分类成功",
        "data": [
            categories
        ]
}

@router.get("/{id}")
async def get_news(id: int):
    return {"msg": "获取新闻成功"}