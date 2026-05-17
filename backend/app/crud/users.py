from datetime import datetime, timedelta
import uuid

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import select, update
from ..utils.security import get_hash_password,verify_password
from ..schemas.users import UserRequest, UserUpdateRequest
from ..models.users import User, UserToken

async def get_user_by_username(db: AsyncSession, username: str):
    query = select(User).where(User.username == username)
    result = await db.execute(query)
    return result.scalar_one_or_none()
  
async def create_user(db: AsyncSession, user_data: UserRequest):
    hashed_password = get_hash_password(user_data.password)
    user=User(username=user_data.username, password=hashed_password)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

async def create_token(db: AsyncSession, user_id: int):
    #生成token->查有无token->有：更新；无->添加
    token=str(uuid.uuid4())
    expires_at=datetime.now()+timedelta(days=7)
    query = select(UserToken).where(UserToken.user_id == user_id)
    result = await db.execute(query)
    user_token = result.scalar_one_or_none()
    if user_token:
        user_token.token=token
        user_token.expires_at=expires_at
    else:
        user_token=UserToken(token=token,expires_at=expires_at,user_id=user_id)
        db.add(user_token)
        await db.commit()
        await db.refresh(user_token)
    return token

async def authenticate_user(username:str,db: AsyncSession,password:str):
    user=await get_user_by_username(db, username)
    if not user:
        return None
    if not verify_password(password, user.password):
        return None
    
    return user


#根据token获取用户信息，然后查询用户
async def get_user_by_token(db: AsyncSession, token: str):
    query = select(UserToken).where(UserToken.token == token)
    result = await db.execute(query)
    user_token = result.scalar_one_or_none()
    if not user_token:
        return None
    if user_token.expires_at < datetime.now():
        return None
    query = select(User).where(User.id == user_token.user_id)
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def update_user(db: AsyncSession, username: str, user_data: UserUpdateRequest):
    # 先解包userdata，拿到字典，再改数据
    query=update(User).where(User.username == username).values(**user_data.model_dump(
        exclude_unset=True,
        exclude_none=True
    ))    #只修改非none的属性
    result = await db.execute(query)
    await db.commit()
    if result.rowcount == 0: # pyright: ignore[reportAttributeAccessIssue]
        raise HTTPException(status_code=404, detail="用户不存在")
    
    updated_user = await get_user_by_username(db, username)     #重新更新用户
    return updated_user


# 先验证旧的，再更新新的
async def change_password(db: AsyncSession, user:User, old_password: str,new_password: str):
    if not verify_password(old_password, user.password):
        return False
    
    hashed_password = get_hash_password(new_password)
    user.password=hashed_password
    db.add(user)        #这句保证由sqlalchemy生成的id生效，session过期后，id会丢失
    await db.commit()
    await db.refresh(user)
    return True