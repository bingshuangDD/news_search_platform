from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy import delete, func, select

from ..models.news import News
from ..config.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.users import User
from ..models.history import History


async def crud_check_history(user_id:int,news_id:int,db: AsyncSession = Depends(get_db)):
  query = select(History.id).where(History.user_id==user_id,History.news_id==news_id).limit(1)
  result = await db.execute(query)
  return result.scalar() is not None

async def add_news_history( user_id:int,news_id:int,db: AsyncSession = Depends(get_db)):
  query = select(History).where(History.user_id==user_id, History.news_id==news_id).limit(1)
  result = await db.execute(query)
  existing = result.scalar()
  if existing:
    existing.view_time = datetime.now()
    await db.commit()
    await db.refresh(existing)
  else:
    data = History(user_id=user_id, news_id=news_id)
    db.add(data)
    await db.commit()
    await db.refresh(data)
  return True

async def remove_news_history( user_id:int,news_id:int,db: AsyncSession = Depends(get_db)):
  stmt = delete(History).where(History.user_id==user_id,History.news_id==news_id)
  result = await db.execute(stmt)
  await db.commit()
  return result.rowcount > 0 # pyright: ignore[reportAttributeAccessIssue]

#方案：获取请求token->验证登录->统计总量->联表查询浏览新闻->返回结果
async def crud_get_history_list(
  user_id:int ,
  page:int =1,
  page_size:int =10,
  db: AsyncSession = Depends(get_db)
):
  count_query = select(func.count(History.id)).where(History.user_id==user_id)
  count_result = await db.execute(count_query)
  total = count_result.scalar_one()
  
#获取列表，按view_time排序，分页
  off_set = (page-1)*page_size
  list_query = (select(News,History.view_time.label("view_time"),History.id.label("history_id")).join(History,History.news_id==News.id)
  .where(History.user_id==user_id).order_by(History.view_time.desc()).offset(off_set).limit(page_size))
  result = await db.execute(list_query)
  rows = result.all()
  return rows,total

async def crud_clear_history(user_id:int,db: AsyncSession = Depends(get_db)):
  stmt = delete(History).where(History.user_id==user_id)
  await db.execute(stmt)
  result = await db.commit()
  return result