from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field,ConfigDict

class NewsItemBase(BaseModel):
    id:int 
    title:str 
    description:Optional[str]=None 
    image: Optional[str]=None
    author:Optional[str]=None
    category_id:int = Field(alias="categoryId")
    views:int 
    publish_time:Optional[datetime] = Field(None,alias="publishTime")
    
    model_config =ConfigDict(
        from_attributes=True,    # 通过orm_attributes字段填充数据(允许从orm对象中取值)
        populate_by_name=True
    )
    
    
