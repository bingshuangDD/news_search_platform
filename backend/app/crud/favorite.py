from fastapi import APIRouter, Depends, Query
from sqlalchemy import delete, func, select

from ..models.news import News
from ..config.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.users import User
from ..models.favorite import Favorite


async def check_favorite( user_id:int,news_id:int,db: AsyncSession = Depends(get_db)):
  query=select(Favorite).where(Favorite.user_id==user_id,Favorite.news_id==news_id)
  result = await db.execute(query)
  #是否有收藏记录？
  return result.scalar_one_or_none() is not None

async def add_news_favorite( user_id:int,news_id:int,db: AsyncSession = Depends(get_db)):
   data=Favorite(user_id=user_id,news_id=news_id)
   db.add(data)
   await db.commit()
   await db.refresh(data)
   return await check_favorite(user_id,news_id,db)
 
 
async def remove_news_favorite( user_id:int,news_id:int,db: AsyncSession = Depends(get_db)):
  stmt= delete(Favorite).where(Favorite.user_id==user_id,Favorite.news_id==news_id)
  result = await db.execute(stmt)
  await db.commit()
  return result.rowcount > 0 # pyright: ignore[reportAttributeAccessIssue]


#获取收藏列表
#实现方案：获取请求token->验证登录->统计收藏总量->联表查询收藏新闻
async def crud_get_favorite_list(
  user_id:int ,
  page:int =1,
  page_size:int =10,
  db: AsyncSession = Depends(get_db)
):
  #总量+列表
  count_query=select(func.count()).where(Favorite.user_id==user_id)
  count_result= await db.execute(count_query)
  total = count_result.scalar_one()
  
  #获取列表（联表查询+收藏时间排序+分页）
  # Favorite.created_at.label("favorite_createtime")别名
  # 返回的对象[(新闻对象，收藏时间，收藏id)]
  off_set = (page-1)*page_size
  list_query=(select(News,Favorite.created_at.label("favorite_createtime"),Favorite.id.lable("favorite_id"))
              .join(Favorite,Favorite.news_id==News.id)
  .where(Favorite.user_id==user_id).order_by(Favorite.created_at.desc()).offset(off_set).limit(page_size))
  result = await db.execute(list_query)
  rows = result.all()
  return rows,total

#删除收藏
# 实现方案——>获取请求token->验证登录->删除收藏记录

async def crud_remove_favorite(user_id:int,db: AsyncSession = Depends(get_db)):
  delete_query=delete(Favorite).where(Favorite.user_id==user_id)
  await db.execute(delete_query)
  result = await db.commit()
  return result