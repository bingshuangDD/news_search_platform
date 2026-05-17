from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy import alias
from sqlalchemy.ext.asyncio import AsyncSession
from ..config.database import get_db
from ..crud import users

async def get_current_user(authorization:str=Header(...,alias="Authorization")   ,db: AsyncSession = Depends(get_db)):
  '''
  token = authorization.split(" ")[1]
  这是根据文档中的请求头,从请求头中获取token,并返回当前用户信息的写法
  '''
  token=authorization.replace("Bearer ","")
  user=await users.get_user_by_token(db,token)
  if not user:
    raise HTTPException(status_code=401,detail="无效的令牌")
  return user