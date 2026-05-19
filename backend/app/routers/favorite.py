from fastapi import APIRouter, Depends, HTTPException,Query
from..config.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.users import User
from ..utils.response import success_response
from ..utils.auth import get_current_user
from ..crud.favorite import check_favorite,add_news_favorite, crud_get_favorite_list, crud_remove_favorite, remove_news_favorite
from ..schemas.favorite import FavoriteAddResponse, FavoriteCheckResponse,FavoriteListResponse,FavoriteNewsItemRespones

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

@router.delete("/remove")
async def remove_favorite(news_id:int=Query(...,alias="newsId"),user:User=Depends(get_current_user),
                         db: AsyncSession = Depends(get_db)):
  result=await remove_news_favorite(user.id,news_id,db)
  if not result:
    raise HTTPException(status_code=400,detail="取消收藏失败")
  return success_response(message="取消收藏成功",data=result)


@router.get("/list")
async def get_favorite_list(
        page:int = Query(1,ge=1),
        page_size:int =Query(10,ge=1,alias="pageSize",le=100),

        user:User=Depends(get_current_user),
        db: AsyncSession = Depends(get_db)):
  rows,total = await crud_get_favorite_list(user.id,page,page_size,db)
  favorite_list=[FavoriteNewsItemRespones(
    **news.__dict__,
    favoriteTime=favorite_time,
    favoriteId=favorite_id
    )for news,favorite_time,favorite_id in rows]
  hasmore= total > page_size*page
  data= FavoriteListResponse(list = favorite_list ,total =total,hasMore=hasmore)
  return success_response(message="获取收藏列表成功",data=data)


@router.delete ("/clear")
async def clear_favorite(user:User=Depends(get_current_user),
                         db: AsyncSession = Depends(get_db)):
    count=await crud_remove_favorite(user.id,db)
    return success_response(message=f"清空收藏成功,清空了{count}条记录")