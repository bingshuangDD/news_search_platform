from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
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