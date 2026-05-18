from fastapi import APIRouter, Depends,Query
from..config.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.users import User
from ..utils.response import success_response
from ..utils.auth import get_current_user
from ..crud.favorite import check_favorite,add_news_favorite
from ..schemas.favorite import FavoriteAddResponse, FavoriteCheckResponse

router = APIRouter(prefix="/api/favorite", tags=["favorite"])


# 检查流程：进入请求->验证token是否正确->查用户是否收藏该新闻->返回结果
@router.get("/check")
async def check_favorited(news_id:int=Query(...,alias="newsId"),user:User=Depends(get_current_user),
                         db: AsyncSession = Depends(get_db)):
  
  favored= await check_favorite(user.id,news_id,db)
  return success_response(message="success",data= FavoriteCheckResponse(isFavorite=favored))



# 添加流程：进入请求->验证token是否正确->携带请求体参数newsid ->添加收藏->返回结果
@router.post("/add")
async def add_favorite(data:FavoriteAddResponse,user:User=Depends(get_current_user),
                         db: AsyncSession = Depends(get_db)):
  result=await add_news_favorite(user.id,data.news_id,db)
  return success_response(message="success",data=result)