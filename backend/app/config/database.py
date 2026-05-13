from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import DateTime, text
from datetime import datetime

# 用于创建数据库的管理员连接
ADMIN_DATABASE_URL = "mysql+aiomysql://root:123456@localhost:3306/mysql"

# 项目数据库连接
ASYNC_DATABASE_URL = "mysql+aiomysql://root:123456@localhost:3306/FastAPI_first?charset=utf8"
ASYNC_DATABASE_URL = "mysql+aiomysql://root:123456@localhost:3306/news_app?charset=utf8"

async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=True,
    pool_size=10, # 连接池大小
    max_overflow=20, # 连接池溢出时最大连接数
)


class Base(DeclarativeBase):
    create_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, comment="创建时间")
    update_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")


AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def create_database():
    admin_engine = create_async_engine(ADMIN_DATABASE_URL)
    async with admin_engine.connect() as conn:
        await conn.execute(text(
            "CREATE DATABASE IF NOT EXISTS FastAPI_first CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
        ))
        await conn.commit()
    await admin_engine.dispose()


async def create_tables():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


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
