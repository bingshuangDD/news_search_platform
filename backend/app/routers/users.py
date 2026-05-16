from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import null
from ..config.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from ..schemas.users import UserAuthResponse, UserRequest ,UserInfoBase,UserInfoResponse
from ..models.users import User, UserToken
from ..crud import users
from ..utils.response import success_response
router = APIRouter(prefix="/api/user", tags=["users"])


@router.post("/register")
async def register(user_data:UserRequest,db: AsyncSession = Depends(get_db)):
  #注册逻辑：1.验证用户名是否已存在 2.创建用户 3.生成token 4.返回用户信息
  existing_user=await users.get_user_by_username(db,user_data.username)
  if existing_user:
    raise HTTPException(status_code=400, detail="用户已存在")
  user=await users.create_user(db,user_data)
  token=await users.create_token(db,user.id)
#   return {
#       "code": 200,
#       "message": "登录成功",
#       "data": {
#         "token": token,
#         "userInfo": {
#         "id": user.id,
#         "username": user.username,
#         "nickname": user.nickname,
#         "avatar": user.avatar,
#         "bio": user.bio
#     }
#   }
# }
  response_data = UserAuthResponse(token=token, userInfo=UserInfoResponse.model_validate(user))
  return success_response(message="注册成功",data=response_data)
  