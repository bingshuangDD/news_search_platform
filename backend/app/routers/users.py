from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import null
from ..config.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from ..schemas.users import UserAuthResponse, UserRequest ,UserInfoBase,UserInfoResponse,UserUpdateRequest,UserChangePasswordRequest
from ..models.users import User, UserToken
from ..crud import users
from ..utils.response import success_response
from ..utils.auth import get_current_user
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
  
  
@router.post("/login")
async def login(user_data:UserRequest,db: AsyncSession = Depends(get_db)):
  #登录逻辑：1.验证用户名是否已存在 2.验证 3.生成token 4.返回用户信息
  user=await users.authenticate_user(user_data.username,db,user_data.password)
  if not user:
    raise HTTPException(status_code=401, detail="用户名或密码错误")
  token=await users.create_token(db,user.id)
  response_data = UserAuthResponse(token=token, userInfo=UserInfoResponse.model_validate(user))
  return success_response(message="登录成功",data=response_data)


@router.get("/info")
async def get_user_info(user: User = Depends(get_current_user)):
  #获取用户信息
  #响应前端token流程：进入请求认证token->验证token是否有效->查用户信息->返回用户信息
  return success_response(message="获取用户信息成功",data=UserInfoResponse.model_validate(user))


@router.put("/update")
async def update_user_info(user_data:UserUpdateRequest,user: User = Depends(get_current_user),db: AsyncSession = Depends(get_db)):
  #更新用户信息
  #1.验证用户名是否已存在 2.更新用户信息 3.返回用户信息
  updated_user=await users.update_user(db,user.username,user_data)
  return success_response(message="更新用户信息成功",data=UserInfoResponse.model_validate(updated_user))
  
@router.put("/password")
async def update_password(password_data:UserChangePasswordRequest,user: User = Depends(get_current_user),db: AsyncSession = Depends(get_db)):
   changed_password=await users.change_password(db,user,old_password=password_data.old_password,new_password=password_data.new_password)
   if not changed_password:
     raise HTTPException(status_code=500, detail="密码修改失败")
   return success_response(message="密码修改成功")
   