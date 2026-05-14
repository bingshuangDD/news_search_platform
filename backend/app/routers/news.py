from fastapi import APIRouter,Depends,Query
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
        "data": categories
}


@router.get("/list")
async def get_news_list(
                category_id:int =Query(...,alias="categoryId"),
                page:int =1,
                page_size:int =Query(10,alias="pageSize",le=100),
                db: AsyncSession = Depends(get_db)
):  
    offset = (page-1)*page_size
    news_list=await news.get_news_list(db,category_id,offset,page_size)
    total=await news.get_news_count(db,category_id)
    hasMore = total > offset + len(news_list)
    return{
        "code": 200,
        "message": "获取新闻列表成功",
        "data":{
            "list":news_list,
            "total":total,
            "hasMore":hasMore
        }
}
    

@router.get("/detail")
async def get_news_detail(news_id:int=Query(...,alias="id"),db: AsyncSession = Depends(get_db)):
    # news_detail=await news.get_news_detail(db,id)功能待开发
    return{
        "code": 200,
        "message": "获取新闻详情成功",
        "data": {
            "text":"text"
        }
}