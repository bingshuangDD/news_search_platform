from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import create_async_engine,async_sessionmaker,AsyncSession
from sqlalchemy.orm import DeclarativeBase,Mapped,mapped_column
from sqlalchemy import Column, Integer, String, DateTime, select,text
from contextlib import asynccontextmanager
from datetime import datetime
from .routers import news
# conda activate fastapi_env 激活环境

ADMIN_DATABASE_URL = "mysql+aiomysql://root:123456@localhost:3306/mysql"
async def create_database():
    """先创建 FastAPI_first 数据库（如果不存在）"""
    admin_engine = create_async_engine(ADMIN_DATABASE_URL)
    async with admin_engine.connect() as conn:
        await conn.execute(text(
            "CREATE DATABASE IF NOT EXISTS FastAPI_first CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
        ))
        await conn.commit()
    await admin_engine.dispose()
    print("✅ 数据库 FastAPI_first 已创建或已存在")
# 格式: mysql+aiomysql://用户名:密码@主机:端口/数据库名?charset=utf8
ASYNC_DATABASE_URL = "mysql+aiomysql://root:123456@localhost:3306/FastAPI_first?charset=utf8"

# 创建异步引擎
async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=True,           # 打印 SQL 语句（开发时开启，生产关闭）
    pool_size=10,        # 连接池大小
    max_overflow=20      # 超出池大小后允许的额外连接
)

# 2.定义模型类
class Base(DeclarativeBase):
    create_time: Mapped[datetime]=mapped_column(DateTime,default=datetime.now,comment="创建时间")
    update_time: Mapped[datetime]=mapped_column(DateTime,default=datetime.now,onupdate=datetime.now,comment="更新时间")
   
class Book(Base):
    __tablename__ = "books"
    id: Mapped[int] = mapped_column(primary_key=True, comment="编号")
    title: Mapped[str] = mapped_column(String(50), comment="书名")
    author: Mapped[str] = mapped_column(String(50), comment="作者")
    price: Mapped[float] = mapped_column(comment="价格")
    
async def create_tables():
    # 获取异步引擎
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ 数据表已创建或已存在")

async def close_db():
    await async_engine.dispose()
    print("数据库连接已关闭")
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动
    await create_database()
    await create_tables()
    yield  # 应用运行期间
    # 关闭
    await close_db()
       
app = FastAPI(title="新闻平台项目", version="1.0.0", lifespan=lifespan)

app.include_router(news.router)


@app.get("/")
async def root():
    return {"message": "Hello from FastAPI!", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

'''路由函数需要数据库连接才能操作数据，但：
❌ 直接在路由里创建连接 → 代码混乱，无法复用
✅ 用依赖注入 → 自动获取连接，用完自动关闭'''

AsyncSessionLocal=async_sessionmaker(
    bind=async_engine,  # 绑定引擎
    class_=AsyncSession, # 指定会话类
    expire_on_commit=False # 不自动提交
)

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session #返回会话
            await session.commit() # 提交
        except:
            await session.rollback() #回滚
            raise #抛出异常
        finally:
            await session.close() #关闭会话

@app.get("/book/books")
async def get_books(db: AsyncSession = Depends(get_db)):
    """获取所有图书"""
    query = select(Book) 
    result = await db.execute(query)
    books = result.scalars().all()
    # 获取单条数据
    '''book=awwait db.get(Book,id)'''
    return books

@app.get("/book/books/{id}")
async def get_book(id: int, db: AsyncSession = Depends(get_db)):
    """获取指定编号的图书"""
    result = await db.execute(select(Book).where(Book.id == id))
    book=result.scalar_one_or_none()
    return book
 
@app.get("/book/search",description="小于该价钱的书籍")
async def search_books(price: float, db: AsyncSession = Depends(get_db)):
    """搜索图书"""
    query = select(Book).where(Book.price<=price)
    result = await db.execute(query)
    books = result.scalars().all()
    return books

@app.get("/book/search_author",description="作者包含指定字符的图书")
async def get_search_author(author: str, db: AsyncSession = Depends(get_db)):
    """搜索作者"""
    query = select(Book).where(Book.author.contains(author))
    result = await db.execute(query)
    books = result.scalars().all()
    return books

class BookCreate(BaseModel):
    id: int
    title: str
    author: str
    price: float
#新增id,书名,作者,价格
@app.post("/book/add")
async def add_book(book:BookCreate, db: AsyncSession = Depends(get_db)):
    """新增图书"""
    book_data = book.model_dump()
    orm_book = Book(**book_data)
    db.add(orm_book)
    await db.commit()
    return book

class BookUpdate(BaseModel):
    title: str
    author: str
    price: float
    
    
@app.put("/book/update/{id}")
async def update_book(id: int, book: BookUpdate, db: AsyncSession = Depends(get_db)):
    """更新图书"""
    db_book = await db.get(Book, id)
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    db_book.title = book.title
    db_book.author = book.author
    db_book.price = book.price
    await db.commit()
    return db_book
    

@app.delete("/book/delete/{id}")
async def delete_book(id: int, db: AsyncSession = Depends(get_db)):
    """删除图书"""
    db_book = await db.get(Book, id)
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    await db.delete(db_book)
    await db.commit()
    return {"message": "Book deleted"}