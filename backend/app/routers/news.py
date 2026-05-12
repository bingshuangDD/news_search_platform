from fastapi import APIRouter

router = APIRouter(prefix="/api/news", tags=["news"])  # 同模块前缀相同

@router.get("/categories")
async def get_category(id: int):
    return {"msg": "获取分类成功"}
