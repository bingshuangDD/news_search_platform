import os

from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine


def build_database_url():
    """构建数据库连接，兼容 Railway URL 和 Docker 独立变量。"""
    raw_url = os.getenv("DATABASE_URL")
    if raw_url:
        # Railway 注入的是 mysql:// 格式，aiomysql 需要 mysql+aiomysql://
        if raw_url.startswith("mysql://"):
            raw_url = raw_url.replace("mysql://", "mysql+aiomysql://", 1)

        # 追加 charset 参数
        return raw_url + (
            "?charset=utf8mb4" if "?" not in raw_url else "&charset=utf8mb4"
        )

    return URL.create(
        drivername="mysql+aiomysql",
        username=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", "123456"),
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "3306")),
        database=os.getenv("DB_NAME", "news_app"),
        query={"charset": "utf8mb4"},
    )


ASYNC_DATABASE_URL = build_database_url()

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
