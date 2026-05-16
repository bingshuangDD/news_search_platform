from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class UserRequest(BaseModel):
    username: str
    password: str

#user数据类型->（可选类+必填类）    
class UserInfoBase(BaseModel):   #可选类
    nickname: Optional[str]=Field(None,max_length=50,description="昵称")
    avatar: Optional[str]=Field(None,max_length=255,description="头像URL")
    gender: Optional[str]=Field(None,max_length=10,description="性别")
    bio: Optional[str]=Field(None,max_length=500,description="个人简介")

    

class UserInfoResponse(UserInfoBase):
    id: int
    username: str
    model_config =ConfigDict(
        from_attributes=True    # 通过orm_attributes字段填充数据(允许从orm对象中取值)
    )
    
#data数据类型
class UserAuthResponse(BaseModel):
    token: str
    user_info: UserInfoResponse = Field(...,alias="userInfo")
    #模型类配置
    model_config =ConfigDict(
        populate_by_name=True,  # 通过字段名填充数据（alias字段名兼容）
        from_attributes=True    # 通过orm_attributes字段填充数据(允许从orm对象中取值)
    )