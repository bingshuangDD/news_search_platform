from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import func, select, update

from ..schemas.base import NewsItemBase
from ..models import news
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from ..cache.news_cache import get_cached_categories, get_cached_news_list, set_cached_categories, set_cached_news_list

async def get_category(db: AsyncSession, skip: int = 0, limit: int = 100):
  cache_categories = await get_cached_categories()
  if cache_categories: return cache_categories
  stmt = select(news.Category).offset(skip).limit(limit)
  result = await db.execute(stmt)
  news_list = result.scalars().all()  #ORM
  if not cache_categories:
    news_list = jsonable_encoder(news_list)
    await set_cached_categories(news_list)
  return news_list

async def get_news_list(db: AsyncSession, category_id:int,skip: int = 0, limit: int = 100):
  #尝试缓存读取
  #跳过的数量skip
  #await get_cache_news_list(cache_key)
  page = skip // limit + 1
  cache_list = await get_cached_news_list(category_id,page,limit)
  if cache_list:  #缓存命中
    return [news.News(**item)for item in cache_list]
  
  
  stmt = select(news.News).where(news.News.category_id==category_id).offset(skip).limit(limit)
  result = await db.execute(stmt)
  news_list = result.scalars().all()
  
  
  #写入缓存
  #先ORM 转 字典
  #并且保持python风格的键，让by_alias=False
  if news_list:  #数据库有数据
     news_data = [NewsItemBase.model_validate(item).model_dump(mode="json",by_alias=False) for item in news_list]
     await set_cached_news_list(category_id,page,limit,news_data)
     
     
  return news_list

  
    

async def get_news_count(db: AsyncSession, category_id:int):
  stmt = select(func.count(news.News.id)).where(news.News.category_id==category_id)
  result = await db.execute(stmt)
  news_count = result.scalar_one() #只能有1个结果，否则报错
  return news_count

async def get_news_detail(db: AsyncSession, news_id:int):
  stmt = select(news.News).where(news.News.id==news_id)
  result = await db.execute(stmt)
  news_detail = result.scalar_one_or_none()
  return news_detail



async def increase_news_views(db: AsyncSession, news_id: int) -> bool:
    stmt = (
        update(news.News)
        .where(news.News.id == news_id)
        .values(views=news.News.views + 1)
    )
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount > 0 # pyright: ignore[reportAttributeAccessIssue]

async def get_related_news(db: AsyncSession, news_id: int,categoryid:int, limit: int = 5):
    stmt = (
        select(news.News)
        .where(news.News.id != news_id,news.News.category_id==categoryid)
        .order_by(news.News.views.desc(),news.News.publish_time.desc())
        .limit(limit)
    )
    result = await db.execute(stmt)
    related_news = result.scalars().all()
    
    return [{
        "id": news_detail.id,
            "title": news_detail.title,
            "content": news_detail.content,
            "image": news_detail.image,
            "author": news_detail.author,
            "publishTime": news_detail.publish_time,
            "categoryId": news_detail.category_id,
            "views": news_detail.views,
    }for news_detail in related_news] 
