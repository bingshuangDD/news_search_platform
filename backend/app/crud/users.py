from datetime import datetime, timedelta
import uuid

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import select
from ..utils.security import get_hash_password
from ..schemas.users import UserRequest
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