"""
RAG 新闻问答主流程

职责：
- 启动时从 MySQL 全量加载新闻 → 分块 → 构建 TF-IDF 索引
- 用户提问时检索相关 chunk → 拼接 Prompt → 调用 Kimi API 流式返回
"""

import os
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from .retriever import retriever, split_text
from ..crud.news_export import get_all_news_for_index

# ---------- 常量 ----------

KIMI_MODEL = os.getenv("KIMI_MODEL", "kimi-k2.6")

RAG_SYSTEM_PROMPT = """你是一个新闻知识助手。请基于以下新闻内容回答用户的问题。

要求：
1. 只使用下面提供的新闻内容来回答，不要编造信息
2. 如果新闻内容不足以回答用户的问题，请诚实告知"抱歉，暂无相关新闻可以回答这个问题"
3. 回答时请引用具体的新闻标题，格式为【新闻标题】
4. 回答简洁清晰，2-3 段为宜
5. 如果涉及多个新闻，请分点说明

相关新闻内容：
{context}

请基于以上新闻内容回答问题。"""

# ---------- 索引构建 ----------


async def build_news_index(db: AsyncSession) -> int:
    """
    从 MySQL 加载全量新闻 → 分块 → 构建 TF-IDF 索引。

    Returns:
        索引中的 chunk 总数
    """
    news_list = await get_all_news_for_index(db)

    for news in news_list:
        chunks = split_text(news["content"])
        for chunk_text in chunks:
            retriever.add_chunk(
                news_id=news["id"],
                title=news["title"],
                text=chunk_text,
                category=news["category"],
                publish_time=news["publish_time"],
            )

    retriever.build_index()
    return len(retriever.chunks)


# ---------- RAG 问答 ----------


async def ask_news_question(
    question: str,
    top_k: int = 3,
) -> AsyncGenerator[bytes, None]:
    """
    RAG 新闻问答（SSE 流式）。

    流程：检索 → 拼接上下文 → 构建 Prompt → 流式调用 Kimi API
    """
    # 1) 检索相关 chunk
    search_results = retriever.search(question, top_k)

    # 2) 拼接上下文
    context_parts = []
    for i, (chunk, score) in enumerate(search_results, 1):
        context_parts.append(
            f"[新闻{i}] 标题：{chunk['title']} | "
            f"分类：{chunk['category']} | "
            f"发布时间：{chunk['publish_time']}\n"
            f"内容：{chunk['text'][:500]}"
        )
    context = "\n\n".join(context_parts) if context_parts else "暂无相关新闻。"

    # 3) 构建 messages
    system_prompt = RAG_SYSTEM_PROMPT.format(context=context)
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": question},
    ]

    # 4) 流式调用 Kimi API
    from ..routers.ai import stream_kimi  # lazy import 避免循环依赖
    async for chunk in stream_kimi(messages, KIMI_MODEL):
        yield chunk


# ---------- 索引重建 ----------


async def rebuild_index(db: AsyncSession) -> int:
    """
    清空并重建索引（供管理接口使用，本次不挂路由）。
    """
    retriever.clear()
    return await build_news_index(db)
