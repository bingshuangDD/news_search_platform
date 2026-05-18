from pydantic import BaseModel, Field

class FavoriteCheckResponse(BaseModel):
    is_favorite:bool = Field(...,alias="isFavorite")
    
class FavoriteAddResponse(BaseModel):
    news_id:int = Field(...,alias="newsId")