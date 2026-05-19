from fastapi import APIRouter, Depends, HTTPException,Query

from ..crud.history import add_news_history, crud_check_history, crud_clear_history, crud_get_history_list, remove_news_history
from..config.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.users import User
from ..utils.response import success_response
from ..utils.auth import get_current_user
from ..schemas.history import HistoryCheckResponse,HistoryAddResponse,HistoryListResponse,HistoryNewsItemRespones

router = APIRouter(prefix="/api/history",tags=["history"])

@router.get("/check")
async def check_history(news_id:int=Query(...,alias="newsId"),user:User=Depends(get_current_user),
                         db: AsyncSession = Depends(get_db)):
    """
    查看新闻是否已浏览
    """
    result = await crud_check_history(user.id,news_id,db)
    return success_response(message="success",data=result)
  
  # 以上代码无用
  
@router.post("/add")
async def add_history(news_id:int=Query(...,alias="newsId"),user:User=Depends(get_current_user),
                         db: AsyncSession = Depends(get_db)):
    result=await add_news_history(user.id,news_id,db)
    return success_response(message="添加历史记录成功",data=HistoryCheckResponse(isHistory=result))

@router.get("/delete/{history_id}")
async def remove_history(news_id:int=Query(...,alias="newsId"),user:User=Depends(get_current_user),
                         db: AsyncSession = Depends(get_db)):
    result=await remove_news_history(user.id,news_id,db)
    if not result:
        raise HTTPException(status_code=400,detail="删除历史记录失败")
    return success_response(message="删除历史记录成功",data=result)
  

#拉表思路
#验证-->查数据创建列表字典-->构建与请求相符的json数据
@router.get("/list")
async def get_history_list(
        page:int = Query(1,ge=1),
        page_size:int =Query(10,ge=1,alias="pageSize",le=100),
        user:User=Depends(get_current_user),
        db: AsyncSession = Depends(get_db)):
  rows,total = await crud_get_history_list(user.id,page,page_size,db)
  history_list = [HistoryNewsItemRespones(
    **news.__dict__,
    viewTime=view_time,
    historyId=history_id
)for news,view_time,history_id in rows]
  hasmore = total > page_size*page
  data = HistoryListResponse(list=history_list,total=total,hasMore=hasmore)
  return success_response(message="获取浏览列表成功",data=data)


@router.delete("/clear")
async def clear_history(user:User=Depends(get_current_user),
                         db: AsyncSession = Depends(get_db)):
    await crud_clear_history(user.id,db)
    
    return success_response(message="清空成功")