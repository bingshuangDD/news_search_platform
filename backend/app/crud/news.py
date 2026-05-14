from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import func, select
from ..models import news


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