"""
全量新闻导出 —— 供 RAG 索引构建使用
"""

from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.news import News, Category


async def get_all_news_for_index(db: AsyncSession) -> List[dict]:
    """
    查询全量新闻（含分类名称），用于构建 RAG 检索索引。

    Returns:
        [
            {
                "id": 1,
                "title": "...",
                "content": "...",
                "category": "科技",
                "publish_time": "2024-01-15T10:30:00",
            },
            ...
        ]
    """
    stmt = (
        select(
            News.id,
            News.title,
            News.content,
            Category.name.label("category_name"),
            News.publish_time,
        )
        .join(Category, News.category_id == Category.id)
        .where(News.content.isnot(None))
    )

    result = await db.execute(stmt)
    rows = result.all()

    news_list = []
    for row in rows:
        # 应用层过滤：跳过内容过短的新闻
        if not row.content or len(row.content) < 50:
            continue

        news_list.append({
            "id": row.id,
            "title": row.title,
            "content": row.content,
            "category": row.category_name,
            "publish_time": row.publish_time.isoformat() if row.publish_time else "",
        })

    return news_list
