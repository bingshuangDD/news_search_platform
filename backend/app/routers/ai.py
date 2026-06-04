import os
import json
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from dotenv import load_dotenv
import httpx

from ..services.rag import ask_news_question

load_dotenv()

KIMI_API_KEY = os.getenv("KIMI_API_KEY")
KIMI_BASE_URL = os.getenv("KIMI_BASE_URL", "https://api.moonshot.cn")
KIMI_MODEL = os.getenv("KIMI_MODEL", "kimi-k2.6")

router = APIRouter(prefix="/api/ai", tags=["ai"])


class ChatRequest(BaseModel):
    messages: list[dict]
    model: str | None = None
    stream: bool = True


class AskRequest(BaseModel):
    question: str          # 用户问题
    top_k: int = 3         # 检索数量，默认 3


async def stream_kimi(messages: list[dict], model: str):
    """流式转发请求到 Kimi API，逐块 yield SSE 数据"""
    async with httpx.AsyncClient(timeout=httpx.Timeout(120.0, connect=10.0)) as client:
        async with client.stream(
            "POST",
            f"{KIMI_BASE_URL}/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {KIMI_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": model,
                "messages": messages,
                "stream": True,
            },
        ) as response:
            async for chunk in response.aiter_bytes():
                yield chunk


@router.post("/chat")
async def chat(req: ChatRequest):
    model = req.model or KIMI_MODEL
    return StreamingResponse(
        stream_kimi(req.messages, model),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )


@router.post("/ask")
async def ask_news(req: AskRequest):
    """RAG 新闻问答（SSE 流式返回）"""
    return StreamingResponse(
        ask_news_question(req.question, req.top_k),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )
