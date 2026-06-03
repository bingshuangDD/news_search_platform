from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import func, select, update

from ..schemas.base import NewsItemBase
from ..models import news
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from ..cache.news_cache import (
    get_cached_categories, get_cached_news_list,
    set_cached_categories, set_cached_news_list,
    CATEGORIES_KEY, NEWS_LIST_PREFIX,
)
from ..config.cache import get_cache_with_mutex

async def get_category(db: AsyncSession, skip: int = 0, limit: int = 100):
    """获取分类列表（带互斥锁，防止缓存击穿）"""
    cache_categories = await get_cached_categories()
    if cache_categories:
        return cache_categories

    # 缓存未命中 → 通过互斥锁查库，只有第一个请求真正打到 DB
    async def fetch_from_db():
        stmt = select(news.Category).offset(skip).limit(limit)
        result = await db.execute(stmt)
        rows = result.scalars().all()
        return jsonable_encoder(rows) if rows else []

    return await get_cache_with_mutex(
        cache_key=CATEGORIES_KEY,
        fetch_func=fetch_from_db,
        expire=7200,
    )

async def get_news_list(db: AsyncSession, category_id:int,skip: int = 0, limit: int = 100):
  """获取新闻列表（带互斥锁，防止缓存击穿）"""
  #尝试缓存读取
  #跳过的数量skip
  page = skip // limit + 1
  cache_list = await get_cached_news_list(category_id,page,limit)
  if cache_list:  #缓存命中
    return [news.News(**item)for item in cache_list]

  # 构造缓存 key
  category_part = category_id if category_id is not None else "all"
  cache_key = f"{NEWS_LIST_PREFIX}{category_part}:{page}:{limit}"

  # 缓存未命中 → 通过互斥锁查库，只有第一个请求真正打到 DB
  async def fetch_from_db():
      stmt = select(news.News).where(news.News.category_id==category_id).offset(skip).limit(limit)
      result = await db.execute(stmt)
      rows = result.scalars().all()

      if rows:
          return [NewsItemBase.model_validate(item).model_dump(mode="json",by_alias=False) for item in rows]
      return []

  news_data = await get_cache_with_mutex(
      cache_key=cache_key,
      fetch_func=fetch_from_db,
      expire=1800,
  )

  # 统一返回 ORM 对象
  if news_data:
      return [news.News(**item) for item in news_data]
  return []

  
    

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
