from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field
from .base import NewsItemBase

class HistoryCheckResponse(BaseModel):
    is_history:bool = Field(...,alias="isHistory")
    
class HistoryAddResponse(BaseModel):
  news_id:int = Field(...,alias="newsId")

class HistoryNewsItemRespones(NewsItemBase):
    history_id:int = Field(...,alias="historyId")
    view_time:datetime = Field(...,alias="viewTime")
    
    model_config =ConfigDict(
        populate_by_name=True,  # 通过字段名填充数据（alias字段名兼容）
        from_attributes=True    # 通过orm_attributes字段填充数据(允许从orm对象中取值)
    )

class HistoryListResponse(BaseModel):
    hasmore:bool = Field(...,alias="hasMore")
    list:list[HistoryNewsItemRespones]
    total: int 
    hasmore:bool = Field(...,alias="hasMore")
    model_config =ConfigDict(
        populate_by_name=True,  # 通过字段名填充数据（alias字段名兼容）
        from_attributes=True    # 通过orm_attributes字段填充数据(允许从orm对象中取值)
    )