from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, select
from contextlib import asynccontextmanager
from datetime import datetime

from .config.database import (
    async_engine,
    Base,
    AsyncSessionLocal,
    create_database,
    create_tables,
    close_db,
    get_db,
)
from .routers import news


# ---------- Book 模型（演示用，后续替换为 news 模型）----------
class Book(Base):
    __tablename__ = "books"
    id: Mapped[int] = mapped_column(primary_key=True, comment="编号")
    title: Mapped[str] = mapped_column(String(50), comment="书名")
    author: Mapped[str] = mapped_column(String(50), comment="作者")
    price: Mapped[float] = mapped_column(comment="价格")


# ---------- 应用生命周期 ----------
@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_database()
    await create_tables()
    yield
    await close_db()


app = FastAPI(title="新闻平台项目", version="1.0.0", lifespan=lifespan)

app.include_router(news.router)


# ---------- 基础路由 ----------
@app.get("/")
async def root():
    return {"message": "Hello from FastAPI!", "status": "running"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


# ---------- Book 路由（演示用）----------
@app.get("/book/books")
async def get_books(db: AsyncSession = Depends(get_db)):
    query = select(Book)
    result = await db.execute(query)
    return result.scalars().all()


@app.get("/book/books/{id}")
async def get_book(id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Book).where(Book.id == id))
    book = result.scalar_one_or_none()
    return book


@app.get("/book/search", description="小于该价钱的书籍")
async def search_books(price: float, db: AsyncSession = Depends(get_db)):
    query = select(Book).where(Book.price <= price)
    result = await db.execute(query)
    return result.scalars().all()


@app.get("/book/search_author", description="作者包含指定字符的图书")
async def get_search_author(author: str, db: AsyncSession = Depends(get_db)):
    query = select(Book).where(Book.author.contains(author))
    result = await db.execute(query)
    return result.scalars().all()


class BookCreate(BaseModel):
    id: int
    title: str
    author: str
    price: float


@app.post("/book/add")
async def add_book(book: BookCreate, db: AsyncSession = Depends(get_db)):
    db_book = Book(**book.model_dump())
    db.add(db_book)
    await db.commit()
    return book


class BookUpdate(BaseModel):
    title: str
    author: str
    price: float


@app.put("/book/update/{id}")
async def update_book(id: int, book: BookUpdate, db: AsyncSession = Depends(get_db)):
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
    db_book = await db.get(Book, id)
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    await db.delete(db_book)
    await db.commit()
    return {"message": "Book deleted"}
