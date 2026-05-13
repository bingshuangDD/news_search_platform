from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import select
from ..models import news


async def get_category(db: AsyncSession, skip: int = 0, limit: int = 100):
  stmt = select(news.Category).offset(skip).limit(limit)
  result = await db.execute(stmt)
  news_list = result.scalars().all()
  return news_list