from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import DateTime, text
from datetime import datetime


import os

_raw_url = os.getenv(
    "DATABASE_URL",
    "mysql+aiomysql://root:123456@localhost:3306/news_app",
)

# Railway 注入的是 mysql:// 格式，aiomysql 需要 mysql+aiomysql://
if _raw_url.startswith("mysql://"):
    _raw_url = _raw_url.replace("mysql://", "mysql+aiomysql://", 1)

# 追加 charset 参数
ASYNC_DATABASE_URL = _raw_url + ("?" + "charset=utf8mb4" if "?" not in _raw_url else "&charset=utf8mb4")

# 用于创建数据库的管理员连接
# 项目数据库连接


async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=True,
    pool_size=10, # 连接池大小
    max_overflow=20, # 连接池溢出时最大连接数
)



AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)
async def close_db():
    await async_engine.dispose()


async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
