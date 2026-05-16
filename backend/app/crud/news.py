from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import func, select, update
from ..models import news
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

async def get_category(db: AsyncSession, skip: int = 0, limit: int = 100):
  stmt = select(news.Category).offset(skip).limit(limit)
  result = await db.execute(stmt)
  news_list = result.scalars().all()
  return news_list

async def get_news_list(db: AsyncSession, category_id:int,skip: int = 0, limit: int = 100):
  stmt = select(news.News).where(news.News.category_id==category_id).offset(skip).limit(limit)
  result = await db.execute(stmt)
  news_list = result.scalars().all()
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
