# 新闻头条全栈项目 — 面试 Q&A

> 基于 [新闻头条 - 全栈新闻资讯平台](https://news-search-platform.vercel.app/) 真实项目提炼，覆盖高频面试考点。

---

## 目录

1. [项目架构与设计](#1-项目架构与设计)
2. [FastAPI 后端核心](#2-fastapi-后端核心)
3. [数据库设计与 ORM](#3-数据库设计与-orm)
4. [认证与安全](#4-认证与安全)
5. [Redis 缓存策略](#5-redis-缓存策略)
6. [AI 集成与 SSE 流式传输](#6-ai-集成与-sse-流式传输)
7. [Vue 3 前端架构](#7-vue-3-前端架构)
8. [部署与 DevOps](#8-部署与-devops)
9. [性能优化](#9-性能优化)
10. [错误处理与异常设计](#10-错误处理与异常设计)
11. [综合情景题](#11-综合情景题)

---

## 1. 项目架构与设计

### Q1: 请介绍这个项目的整体架构？

**答：** 这是一个前后端分离的全栈新闻资讯平台，架构分为三层：

```
前端 (Vue 3 SPA)  ──HTTP/REST──▶  后端 (FastAPI)  ──▶  MySQL 8 (主存储)
   Vercel 托管                       Railway 托管         Railway 托管
                                                      ──▶  Redis (缓存层)
                                                           Railway 托管
                                                      ──▶  Kimi API (AI)
```

- **前端**：Vue 3 + Vite 5 + Vant 4，移动端 SPA，部署在 Vercel
- **后端**：FastAPI + Uvicorn，RESTful API，部署在 Railway
- **数据层**：MySQL 8（异步驱动 aiomysql）+ Redis 缓存
- **AI 服务**：服务端代理转发至 Kimi API（Moonshot），SSE 流式响应

**项目亮点**：
- 全异步架构（FastAPI + SQLAlchemy async + aiomysql）
- Redis 缓存分层设计（不同数据不同过期策略）
- 服务端代理模式保护 API Key 安全
- 统一异常处理与响应格式

---

### Q2: 为什么选择 FastAPI 而不是 Flask 或 Django？

**答：**

| 维度 | FastAPI | Flask | Django |
|------|---------|-------|--------|
| **异步支持** | 原生 async/await | 需插件（Quart） | 3.1+ 才逐步支持 |
| **性能** | 接近 Node.js/Go | 一般 | 一般 |
| **自动文档** | Swagger + ReDoc 自动生成 | 需 flask-swagger | DRF 自带 |
| **数据校验** | Pydantic 原生集成 | 需 marshmallow | DRF Serializer |
| **类型安全** | Python type hints 驱动 | 无 | 无 |
| **学习曲线** | 低 | 低 | 高 |

选择 FastAPI 的核心原因：
1. **异步性能**：项目中全部使用 `async/await`，包括数据库操作和 HTTP 请求
2. **自动 API 文档**：`/docs` 和 `/redoc` 自动生成，无需额外配置
3. **Pydantic 校验**：请求/响应自动校验，类型安全
4. **轻量灵活**：不像 Django 自带 ORM/模板等，可以自由选型 SQLAlchemy

---

### Q3: 前后端分离的利弊是什么？你是如何解决跨域问题的？

**答：**

**优势：**
- 前后端独立开发、独立部署
- 前端静态资源 CDN 加速，后端 API 独立扩容
- 同一后端可服务 Web/App/小程序多端

**劣势：**
- 跨域问题需要处理
- SEO 不友好（SPA 需 SSR 方案）
- 增加了网络请求的复杂性

**本项目跨域解决方案：**

```python
# backend/app/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],     # 开发阶段允许所有源
    allow_credentials=True,  # 允许携带 Cookie
    allow_methods=["*"],     # 允许所有 HTTP 方法
    allow_headers=["*"],     # 允许所有请求头
)
```

**生产环境建议**：将 `allow_origins` 限制为具体域名列表，如 `["https://news-search-platform.vercel.app"]`。

---

## 2. FastAPI 后端核心

### Q4: FastAPI 的依赖注入（Depends）是如何工作的？项目中如何使用？

**答：** FastAPI 的 `Depends` 是一个强大的依赖注入系统，它可以：

1. **自动解析参数**：被依赖函数可以有自己的参数，框架自动解析
2. **复用依赖**：多个路由共享同一依赖逻辑
3. **缓存结果**：同一请求内多次使用同一依赖，只执行一次

**项目中的典型用法 — 数据库会话注入：**

```python
# config/database.py
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session          # 注入给路由
            await session.commit() # 成功后自动提交
        except Exception:
            await session.rollback() # 异常自动回滚
            raise
        finally:
            await session.close()    # 最终关闭
```

**认证依赖注入：**

```python
# utils/auth.py
async def get_current_user(
    authorization: str = Header(..., alias="Authorization"),
    db: AsyncSession = Depends(get_db)  # 链式依赖
):
    token = authorization.replace("Bearer ", "")
    user = await users.get_user_by_token(db, token)
    if not user:
        raise HTTPException(status_code=401, detail="无效的令牌")
    return user
```

**关键点**：
- `yield` 使 `get_db` 成为上下文管理器，`yield` 前的代码在请求前执行，后的代码在请求后执行
- `get_current_user` 本身依赖 `get_db`，形成**依赖链**
- 路由中只需写 `current_user = Depends(get_current_user)` 即可获得认证用户

---

### Q5: 项目中路由是如何组织的？路由前缀和标签的作用？

**答：**

```python
# 各路由模块通过 APIRouter 组织
# routers/news.py
router = APIRouter(prefix="/api/news", tags=["新闻管理"])

# routers/users.py
router = APIRouter(prefix="/api/user", tags=["用户管理"])

# routers/ai.py
router = APIRouter(prefix="/api/ai", tags=["ai"])

# main.py 统一注册
app.include_router(news.router)
app.include_router(users.router)
app.include_router(favorite.router)
app.include_router(history.router)
app.include_router(ai.router)
```

**prefix 作用**：该模块下所有路由自动加上前缀，避免路径重复
**tags 作用**：在 Swagger 文档中按标签分组展示，便于查阅和测试

**最佳实践**：
- 按业务模块拆分路由文件
- 每个模块独立的 `prefix` 和 `tags`
- `main.py` 只做组装，保持简洁

---

### Q6: 项目中统一响应格式是如何设计的？

**答：**

```python
# utils/response.py
def success_response(message: str = "success", data=None):
    content = {"code": 200, "message": message, "data": data}
    return JSONResponse(content=jsonable_encoder(content))
```

所有接口返回统一格式：
```json
{
  "code": 200,
  "message": "操作成功",
  "data": { ... }
}
```

**设计优势：**
- 前端可以统一处理：先判断 `code`，再取 `data`
- `jsonable_encoder` 自动将 ORM 对象、datetime 等转换为 JSON 兼容格式
- 错误时也返回相同结构（只是 code 不同），前端无需区分处理逻辑

---

## 3. 数据库设计与 ORM

### Q7: 项目中如何实现 SQLAlchemy 异步操作？同步和异步有什么区别？

**答：**

**核心配置：**

```python
# 1. 异步引擎
async_engine = create_async_engine(
    ASYNC_DATABASE_URL,  # mysql+aiomysql://...
    echo=True,
    pool_size=10,        # 连接池大小
    max_overflow=20,     # 溢出时最大连接数
)

# 2. 异步会话工厂
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)
```

**同步 vs 异步的差异：**

| 维度 | 同步 (psycopg2/pymysql) | 异步 (aiomysql/asyncpg) |
|------|--------------------------|-------------------------|
| 执行方式 | 阻塞当前线程 | 不阻塞，await 等待 |
| 并发能力 | 靠线程池 | 单线程高并发 |
| ORM 查询 | `session.execute()` | `await session.execute()` |
| 路由函数 | `def` | `async def` |

**项目中的异步查询示例：**

```python
# 异步查询新闻列表
async def get_news_list(db: AsyncSession, category_id: int, skip: int, limit: int):
    stmt = select(News).where(News.category_id == category_id).offset(skip).limit(limit)
    result = await db.execute(stmt)    # await 执行
    return result.scalars().all()      # 获取 ORM 对象列表
```

**Railway 兼容处理：**
```python
# Railway 注入 mysql:// 格式，aiomysql 需要 mysql+aiomysql://
if _raw_url.startswith("mysql://"):
    _raw_url = _raw_url.replace("mysql://", "mysql+aiomysql://", 1)
```

---

### Q8: 项目中设计了哪些表？表之间的关系是怎样的？

**答：** 共设计了 8 张表，核心关系如下：

```
user ──1:N──▶ user_token      (一个用户一个 Token，upsert 模式)
user ──1:N──▶ favorite        (一个用户多条收藏)
user ──1:N──▶ history         (一个用户多条浏览历史)
user ──1:N──▶ ai_chat         (一个用户多条聊天记录)
news_category ──1:N──▶ news   (一个分类多篇新闻)
news ──N:N──▶ news (related)  (通过 related_news 表自关联)
news ──1:N──▶ favorite        (一篇新闻被多人收藏)
news ──1:N──▶ history         (一篇新闻被多人浏览)
```

**关键索引设计：**

| 表 | 索引 |
|----|------|
| `news` | `category_id` 索引、`publish_time DESC` 索引 |
| `favorite` | `(user_id, news_id)` 联合唯一索引 |
| `user_token` | `token` 唯一索引 |
| `history` | `user_id`、`news_id`、`view_time` 分别索引 |

**面试延伸**：为什么要建联合唯一索引 `(user_id, news_id)`？因为同一用户不能重复收藏同一新闻，联合唯一索引既保证数据完整性，又加速了"检查是否已收藏"的查询。

---

### Q9: get_db() 为什么用 yield 而不是 return？

**答：**

```python
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session          # ① 返回会话给路由使用
            await session.commit() # ② 路由执行完后自动提交
        except Exception:
            await session.rollback() # ③ 异常时回滚
            raise
        finally:
            await session.close()    # ④ 无论成功失败都关闭
```

**yield 的关键作用：**
- `yield` 把函数变成**生成器**，FastAPI 将其作为**上下文管理器**处理
- `yield` 之前的代码 = 请求处理前执行（创建会话）
- `yield` 之后的代码 = 请求处理完后执行（提交/回滚/关闭）
- 如果使用 `return`，就无法在请求完成后执行清理逻辑

这是 Python 中实现**依赖生命周期管理**的经典模式。

---

## 4. 认证与安全

### Q10: 项目的认证方案是怎样的？为什么用 Token 而不是 JWT 或 Session？

**答：**

**本项目方案：UUID Token + 数据库存储**

```
注册/登录 → 生成 UUID Token → 存入 user_token 表（7天过期）
后续请求 → Header 携带 Authorization: Bearer <token>
服务端   → 查 user_token 表验证有效性 → 获取用户信息
```

**核心代码：**

```python
# 生成 Token
async def create_token(db: AsyncSession, user_id: int):
    token = str(uuid.uuid4())
    expires_at = datetime.utcnow() + timedelta(days=7)
    # upsert 模式：存在则更新，不存在则插入
    ...

# 验证 Token
async def get_user_by_token(db: AsyncSession, token: str):
    result = await db.execute(
        select(UserToken).where(
            UserToken.token == token,
            UserToken.expires_at > datetime.utcnow()  # 过期检查
        )
    )
    token_record = result.scalar_one_or_none()
    return token_record.user if token_record else None
```

**几种方案的对比：**

| 方案 | 优点 | 缺点 | 适用场景 |
|------|------|------|----------|
| **Session + Cookie** | 成熟、可即时失效 | 需共享存储、跨域麻烦 | 传统 SSR 应用 |
| **JWT** | 无状态、跨服务 | 无法即时失效、payload 不可信 | 微服务/分布式 |
| **UUID Token（本项目）** | 简单、可即时失效 | 每次查库 | 中小型项目 |

**为什么选 UUID Token：**
1. 简单直观，新手友好
2. 可以通过删除数据库记录即时失效（JWT 做不到）
3. 项目规模不大，不需要 JWT 的无状态优势

---

### Q11: 密码是如何安全存储的？bcrypt 和 MD5/SHA256 有什么区别？

**答：**

```python
# security.py
import bcrypt

def get_hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())
```

**bcrypt vs MD5/SHA256：**

| 维度 | bcrypt | MD5/SHA256 |
|------|--------|------------|
| **设计目的** | 专门用于密码哈希 | 通用哈希/签名 |
| **盐值** | 内置自动加盐 | 需手动加盐 |
| **计算速度** | **故意慢**（可调节 cost factor） | 快 |
| **抗暴力破解** | 强（慢 = 攻击成本高） | 弱（GPU 可快速计算） |
| **彩虹表攻击** | 免疫（每个密码独立 salt） | 不加盐时易受攻击 |

**关键理解**：密码哈希不是要"快"，而是要"慢"。bcrypt 默认 `gensalt()` 会生成一个随机的 salt 并嵌入到结果中，验证时 `checkpw` 会自动提取 salt 重新计算。

**项目中 passlib 被注释掉的原因**：直接使用 `bcrypt` 库更轻量，避免额外的依赖。但 passlib 的 `CryptContext` 在需要支持多算法或算法升级时更方便。

---

### Q12: 如何进行接口的权限控制？

**答：** 通过 FastAPI 的依赖注入实现声明式权限控制：

```python
# 公开接口 — 不依赖 get_current_user
@router.get("/api/news/categories")
async def get_categories(db: AsyncSession = Depends(get_db)):
    ...

# 认证接口 — 依赖 get_current_user
@router.get("/api/user/info")
async def get_user_info(
    current_user = Depends(get_current_user)  # 未登录自动返回 401
):
    ...
```

**具体实现：**
- `get_current_user` 从 Header 提取 Token → 查库验证 → 返回 user 或抛出 401
- 需要认证的路由添加 `Depends(get_current_user)`，FastAPI 自动处理
- 不需要认证的路由不添加该依赖即可

---

## 5. Redis 缓存策略

### Q13: 项目中的 Redis 缓存是如何设计的？

**答：** 采用**分层缓存策略**，针对不同数据特征配置不同过期时间：

| 缓存对象 | Key 格式 | 过期时间 | 设计理由 |
|----------|----------|----------|----------|
| 分类列表 | `news:categories` | 7200s (2h) | 分类几乎不变，长缓存 |
| 新闻列表 | `news_list:{category_id}:{page}:{size}` | 1800s (30min) | 新闻更新频率中等 |

**缓存读写流程（Cache-Aside 模式）：**

```
请求 → 查 Redis 缓存
        ├─ 命中 → 反序列化 → 返回（跳过 MySQL）
        └─ 未命中 → 查 MySQL → 序列化 → 写入 Redis → 返回
```

**代码实现：**

```python
# crud/news_cache.py
async def get_news_list(db, category_id, skip, limit):
    page = skip // limit + 1
    cached = await get_cached_news_list(category_id, page, limit)
    if cached:
        # 缓存命中：字典 → ORM 对象
        return [News(**item) for item in cached]

    # 缓存未命中：查数据库
    result = await db.execute(
        select(News).where(News.category_id == category_id).offset(skip).limit(limit)
    )
    news_list = result.scalars().all()

    if news_list:
        # 写入缓存
        data = [NewsItemBase.model_validate(item).model_dump(mode="json") for item in news_list]
        await set_cached_news_list(category_id, page, limit, data)

    return news_list
```

**关键设计细节：**
- 缓存 Key 包含分页参数 `{page}:{size}`，不同分页各自缓存
- 缓存存储的是 JSON 字典而非 ORM 对象（ORM 对象不可序列化）
- 命中缓存后用 `News(**item)` 重建 ORM 对象，保持接口一致性

---

### Q14: Redis 缓存穿透、击穿、雪崩是什么？项目中如何应对？

**答：**

| 问题 | 定义 | 本项目应对方式 |
|------|------|---------------|
| **缓存穿透** | 查询不存在的数据，缓存和 DB 都没命中 | 仅在有数据时才写缓存（`if news_list`），避免缓存空值 |
| **缓存击穿** | 热点 Key 过期瞬间大量请求打到 DB | 分类列表 TTL 2 小时，新闻列表 30 分钟，避免同时过期 |
| **缓存雪崩** | 大量 Key 同时过期/Redis 宕机 | 不同数据不同 TTL（2h vs 30min）；连接池配置 |

**延伸讨论 — 更完善的解决方案：**

```python
# 缓存穿透：缓存空值
if not news_list:
    await set_cache(key, "NULL", expire=60)  # 短期缓存空值
    return []

# 缓存击穿：互斥锁
async def get_with_lock(key):
    data = await get_cache(key)
    if data: return data
    if await acquire_lock(key + ":lock"):
        try:
            data = await query_db()
            await set_cache(key, data, expire=1800)
        finally:
            await release_lock(key + ":lock")
    else:
        await asyncio.sleep(0.1)
        return await get_with_lock(key)

# 缓存雪崩：TTL 加随机值
import random
expire = 1800 + random.randint(0, 300)  # 30min ± 5min
await set_cache(key, data, expire=expire)
```

---

### Q15: Redis 连接配置是如何设计的？

**答：**

```python
# config/cache.py — 兼容多种部署环境
# 优先使用 REDIS_URL（Railway 自动注入）
# 回退到 REDIS_HOST / REDIS_PORT / REDIS_PASSWORD 手动配置
```

**设计亮点：**
1. **环境自适应**：优先读 `REDIS_URL`（PaaS 平台一键注入），不存在时回退到手动配置
2. **封装通用函数**：`get_cache()`、`get_json_cache()`、`set_cache()` 三个核心函数，统一操作接口

---

## 6. AI 集成与 SSE 流式传输

### Q16: 为什么要通过后端代理转发 AI 请求，而不是前端直接调用 Kimi API？

**答：**

**核心原因：API Key 安全**

```
❌ 前端直接调用：
   浏览器 → Kimi API（API Key 暴露在 JS 代码/网络请求中）
   任何人都可以查看源码拿到 Key，造成盗用和费用损失

✅ 后端代理转发（本项目方案）：
   浏览器 → FastAPI → Kimi API（API Key 仅存在服务端环境变量）
   API Key 永不离开服务器
```

**其他优势：**
- 可以对请求做**内容审核**（敏感词过滤）
- 可以**记录聊天日志**（user_message + ai_response 存入数据库）
- 可以**限流控制**（防止单个用户滥用）
- 可以**切换模型**而不需要前端更新

---

### Q17: 什么是 SSE？项目中如何实现流式 AI 对话？

**答：**

**SSE（Server-Sent Events）** 是一种服务器向客户端推送数据的单向通信协议。

```
普通 HTTP：  客户端请求 → 服务器完整响应 → 结束
SSE 流式：   客户端请求 → 服务器逐块推送 → 持续连接直到结束
```

**本项目实现：**

```python
# routers/ai.py
async def stream_kimi(messages: list[dict], model: str):
    """流式转发到 Kimi API"""
    async with httpx.AsyncClient(timeout=httpx.Timeout(120.0, connect=10.0)) as client:
        async with client.stream(
            "POST",
            f"{KIMI_BASE_URL}/v1/chat/completions",
            headers={"Authorization": f"Bearer {KIMI_API_KEY}"},
            json={"model": model, "messages": messages, "stream": True},
        ) as response:
            async for chunk in response.aiter_bytes():
                yield chunk  # 逐块推送给前端

@router.post("/chat")
async def chat(req: ChatRequest):
    return StreamingResponse(
        stream_kimi(req.messages, req.model or KIMI_MODEL),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"},
    )
```

**关键点：**
1. `httpx.AsyncClient.stream()` 实现异步流式读取
2. `aiter_bytes()` 逐块迭代响应体
3. `StreamingResponse` 将生成器变为 SSE 响应
4. `media_type="text/event-stream"` 声明 SSE 格式
5. `Cache-Control: no-cache` 告知浏览器不要缓存流

**SSE vs WebSocket：**

| 维度 | SSE | WebSocket |
|------|-----|-----------|
| 通信方向 | 服务器→客户端（单向） | 双向 |
| 协议 | HTTP | 独立协议 ws:// |
| 实现复杂度 | 低 | 中 |
| 断线重连 | 浏览器内置 | 需手动实现 |
| 适用场景 | 实时推送、AI 流式 | 即时通讯、游戏 |

AI 对话只需要服务器单向推送结果，SSE 完全够用且更简单。

---

### Q18: httpx.AsyncClient 超时配置是如何设计的？为什么 connect 和整体超时分开设置？

**答：**

```python
httpx.Timeout(120.0, connect=10.0)
#              ↑ 整体超时    ↑ 连接超时
```

- **connect=10s**：建立 TCP 连接的超时（通常很快，不应该等太久）
- **整体=120s**：整个请求的超时（AI 生成可能很长，给足够时间）

**分开设置的原因：**
- 如果不能连接，10 秒内快速失败，不让用户傻等
- 如果连接成功但 AI 生成慢，给 120 秒缓冲
- 避免一个数字解决所有场景导致的不合理等待

---

## 7. Vue 3 前端架构

### Q19: Vue 3 Composition API 相比 Options API 有什么优势？项目中如何使用？

**答：**

| 维度 | Options API | Composition API |
|------|-------------|-----------------|
| 代码组织 | 按选项类型（data/methods/watch） | 按逻辑关注点 |
| 逻辑复用 | Mixins（命名冲突、来源不清） | Composables（清晰、类型安全） |
| TypeScript | 支持有限 | 完整支持 |
| Tree-shaking | 不支持 | 支持 |

**项目中 Pinia Store 使用 Composition API 风格：**

```javascript
// store/user.js — Options API 风格（Pinia 两种都支持）
export const useUserStore = defineStore('user', {
  state: () => ({
    userInfo: null,
    token: '',
    isLogin: false,
  }),
  getters: {
    getUserInfo: (state) => state.userInfo,
    getLoginStatus: (state) => state.isLogin,
  },
  actions: {
    async login(userData) { ... },
    async register(userData) { ... },
    logout() { ... },
  },
  persist: {
    enabled: true,
    strategies: [{ key: 'user-store', storage: localStorage }],
  },
})
```

---

### Q20: 项目中路由懒加载是如何实现的？有什么好处？

**答：**

```javascript
// router/index.js
const routes = [
  {
    path: '/home',
    name: 'Home',
    component: () => import('../views/Home.vue'),  // 懒加载
  },
  {
    path: '/news/detail/:id',
    name: 'NewsDetail',
    component: () => import('../views/NewsDetail.vue'), // 懒加载
  },
  // ...
]
```

**懒加载原理：**
- `() => import(...)` 返回 Promise，Vite 将其拆分为独立 chunk
- 只有访问该路由时才加载对应 JS 文件

**好处：**
1. **首屏加载更快**：初始只加载首页代码，其他页面按需加载
2. **代码分割**：每个页面独立文件，浏览器可并行下载
3. **缓存友好**：页面代码独立，修改一个页面不影响其他页面的缓存

---

### Q21: 项目中 Keep-Alive 是如何使用的？

**答：**

```javascript
// 路由配置中的 keepAlive meta
{ path: '/home',  meta: { keepAlive: true } },   // 首页缓存
{ path: '/my',    meta: { keepAlive: true } },   // 我的页面缓存
{ path: '/news/detail/:id', meta: { keepAlive: false } }, // 详情不缓存
```

**策略设计：**
- 首页、分类、AI 聊天、个人中心 → `keepAlive: true`（频繁切换，保留状态）
- 登录、注册、新闻详情、编辑资料 → `keepAlive: false`（每次进入需要最新数据）

---

### Q22: 项目中如何实现国际化（i18n）和主题切换？

**答：**

**国际化实现：**

```javascript
// i18n/index.js
export function setupI18n() {
  const savedLanguage = localStorage.getItem('language') || 'zh-CN';
  return createI18n({
    legacy: false,
    locale: savedLanguage,
    fallbackLocale: 'zh-CN',
    messages: { 'zh-CN': zhCN, 'en-US': enUS },
  });
}

// 动态切换
export function setI18nLanguage(i18n, locale) {
  i18n.global.locale.value = locale;  // Composition API 模式
  document.querySelector('html').setAttribute('lang', locale);
}
```

**主题切换：**
- 支持 4 种主题：浅色、深色、蓝色、绿色
- 通过 Pinia Store 管理当前主题状态，配合 CSS 变量实现

---

## 8. 部署与 DevOps

### Q23: 项目的部署架构是怎样的？为什么选择 Railway + Vercel？

**答：**

```
Vercel（前端）          Railway（后端）
    │                       │
    │ Vue 3 SPA             │ FastAPI + Uvicorn
    │ 静态文件托管           │ Nixpacks 自动构建
    │ SPA Rewrites          │ MySQL + Redis 插件
    │ 全球 CDN              │ ON_FAILURE 重启策略
    │                       │
    └─────── 免费额度 ───────┘
```

**选择理由：**

| 平台 | 用途 | 优势 |
|------|------|------|
| **Railway** | 后端 + 数据库 + 缓存 | 自动注入 DATABASE_URL/REDIS_URL、Nixpacks 零配置构建、内置 MySQL/Redis 插件 |
| **Vercel** | 前端静态托管 | 全球 CDN、自动 HTTPS、SPA Rewrites 原生支持、与 GitHub 无缝集成 |

**SPA Rewrites 配置（vercel.json）：**
```json
{
  "rewrites": [{ "source": "/(.*)", "destination": "/index.html" }]
}
```
所有非静态文件请求都返回 `index.html`，由 Vue Router 接管路由。

---

### Q24: 环境变量在不同环境（本地/生产）如何管理？API Key 如何保护？

**答：**

```python
# 优先级：环境变量 > 默认值
_raw_url = os.getenv("DATABASE_URL", "mysql+aiomysql://root:123456@localhost:3306/news_app")

# Railway 自动注入环境变量（无需手动配置）
# - DATABASE_URL：Railway MySQL 插件自动注入
# - REDIS_URL：Railway Redis 插件自动注入
# - PORT：Railway 自动分配端口

# 敏感信息通过 .env 文件管理（本地开发）
# .env 文件不提交到 Git（.gitignore 包含 .env）
```

**安全最佳实践：**
- `.env` 文件加入 `.gitignore`，永不提交
- 生产环境通过平台环境变量注入（Railway Dashboard / Vercel Settings）
- API Key 仅存后端，不在前端代码中出现
- 本地提供 `.env.example` 模板文件

---

### Q25: 数据库连接字符串为什么要做格式转换？

**答：**

```python
# Railway 注入的是 mysql:// 格式
# aiomysql 需要 mysql+aiomysql:// 格式
if _raw_url.startswith("mysql://"):
    _raw_url = _raw_url.replace("mysql://", "mysql+aiomysql://", 1)

# 追加 charset 参数
ASYNC_DATABASE_URL = _raw_url + (
    "?charset=utf8mb4" if "?" not in _raw_url else "&charset=utf8mb4"
)
```

**原因：**
1. Railway 使用通用的 `mysql://` scheme（标准 JDBC 格式）
2. SQLAlchemy 通过 scheme 识别驱动：`mysql+aiomysql://` 中的 `+aiomysql` 指定异步驱动
3. `utf8mb4` 支持完整 Unicode（包括 emoji），避免中文乱码
4. 对已有 query 参数的情况做兼容处理（`?` vs `&`）

---

## 9. 性能优化

### Q26: 项目中做了哪些性能优化？

**答：**

**后端优化：**

| 优化点 | 方案 | 效果 |
|--------|------|------|
| **异步架构** | FastAPI + async SQLAlchemy + aiomysql | 高并发下不阻塞线程 |
| **连接池** | `pool_size=10`, `max_overflow=20` | 复用连接，避免频繁建立 |
| **Redis 缓存** | 分类/新闻列表分层缓存 | 减少数据库查询 70%+ |
| **数据库索引** | `category_id`、`publish_time` 等 | 加速分类查询和排序 |
| **分页查询** | `OFFSET/LIMIT` | 避免一次性加载全部数据 |

**前端优化：**

| 优化点 | 方案 | 效果 |
|--------|------|------|
| **路由懒加载** | `() => import(...)` | 首屏 JS 体积减少 60%+ |
| **Keep-Alive** | 首页/分类页面缓存 | 切换不重新渲染 |
| **Vite 构建** | 原生 ESM + Rollup 打包 | 极快的冷启动和 HMR |
| **组件按需引入** | Vant 4 按需导入 | 减少组件库体积 |

---

### Q27: 数据库连接池的参数（pool_size=10, max_overflow=20）是如何确定的？

**答：**

```
pool_size=10   → 常驻 10 个连接
max_overflow=20 → 高峰期可额外创建 20 个（共 30 个）
```

**参数考量：**
1. Railway MySQL 插件的最大连接数限制（免费版通常 50-100）
2. 并发用户数估算（中小项目 10 个常驻连接够用）
3. `max_overflow` 留给突发流量缓冲
4. 异步驱动下单连接可服务多个并发请求（不像同步需要 1:1）

**面试延伸**：如何计算合理连接数？
```
理论值 = ((CPU 核心数 * 2) + 磁盘数)
实际值 = 预期并发 QPS ÷ 单查询平均时间（秒）
最后要在理论和实际之间取较小值，避免 MySQL 连接数爆满
```

---

## 10. 错误处理与异常设计

### Q28: 项目中异常处理是如何设计的？为什么按这种顺序注册？

**答：**

```python
# exception_handler.py
def register_exception(app):
    """子类在前，父类在后；具体在前，抽象在后"""
    app.add_exception_handler(HTTPException, http_exception_handler)     # ① 业务异常
    app.add_exception_handler(IntegrityError, integrity_error_handler)  # ② 数据完整性
    app.add_exception_handler(SQLAlchemyError, sqlalchemy_error_handler)# ③ 数据库异常
    app.add_exception_handler(Exception, general_exception_handler)     # ④ 兜底
```

**注册顺序的讲究：**
- FastAPI **按注册顺序**匹配异常处理器，找到第一个匹配的就停止
- `HTTPException` → `IntegrityError` → `SQLAlchemyError` → `Exception`（从具体到通用）
- 如果把 `Exception` 放在前面，后面的处理器永远不会被触发

**各类异常的处理：**
- `HTTPException`：返回自定义 code + message（如 404 "新闻不存在"）
- `IntegrityError`：解析重复键/外键冲突，返回友好提示（如"用户名已存在"）
- `SQLAlchemyError`：通用数据库错误（连接超时等）
- `Exception`：兜底，开发环境返回详细错误，生产环境返回通用错误

---

## 11. 综合情景题

### Q29: 如果用户量增长 100 倍，当前架构有哪些瓶颈？如何优化？

**答：**

**当前瓶颈分析：**

| 组件 | 瓶颈 | 优化方案 |
|------|------|----------|
| **MySQL** | 单机性能上限 | 读写分离（主从复制）、分库分表 |
| **Redis** | 单机内存限制 | Redis Cluster 集群分片 |
| **FastAPI** | 单进程限制 | 多 Worker 进程（`uvicorn --workers 4`）+ 负载均衡（Nginx/ALB） |
| **Token 验证** | 每次请求查 DB | 改为 JWT（无状态验证）+ Redis 黑名单 |
| **新闻列表** | Cache-Aside 模式在缓存失效时打到 DB | 加互斥锁防止击穿、预热缓存 |
| **AI 聊天** | Kimi API 依赖 | 增加备用模型、请求队列削峰 |

**演进路线：**

```
当前：单实例单体架构
  ↓
阶段1：多 Worker + 负载均衡（解决并发瓶颈）
  ↓
阶段2：MySQL 主从读写分离 + Redis Cluster（解决数据层瓶颈）
  ↓
阶段3：微服务拆分（用户服务、新闻服务、AI 服务独立部署）
  ↓
阶段4：引入消息队列（RabbitMQ/Kafka）处理异步任务
```

---

### Q30: 如果需要给项目增加一个"评论"功能，你会如何设计和实现？

**答：**

**1. 数据库设计：**
```sql
CREATE TABLE comment (
    id INT PRIMARY KEY AUTO_INCREMENT,
    news_id INT NOT NULL,          -- 关联新闻
    user_id INT NOT NULL,          -- 评论者
    parent_id INT DEFAULT NULL,    -- 父评论（支持回复，NULL 表示一级评论）
    content TEXT NOT NULL,         -- 评论内容
    created_at DATETIME DEFAULT NOW(),
    FOREIGN KEY (news_id) REFERENCES news(id),
    FOREIGN KEY (user_id) REFERENCES user(id),
    FOREIGN KEY (parent_id) REFERENCES comment(id),
    INDEX idx_news_id (news_id),
    INDEX idx_user_id (user_id),
    INDEX idx_parent_id (parent_id)
);
```

**2. 后端接口设计：**

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/comment/list?newsId=&page=&pageSize=` | 分页获取评论（含嵌套回复） |
| POST | `/api/comment/add` | 添加评论/回复 |
| DELETE | `/api/comment/delete/{id}` | 删除评论（本人或管理员） |

**3. 嵌套回复的处理：**
```
方案A：递归查询（简单但性能差，N+1 问题）
方案B：一次查全部再内存中组装（本项目规模推荐）
方案C：仅支持两层（一级评论 + 回复），最实用
```

**4. 前端组件：**
- `CommentList.vue`：评论列表（支持分页加载）
- `CommentItem.vue`：单条评论（含回复展示）
- `CommentInput.vue`：评论输入框

---

### Q31: 项目中的日志和监控是如何考虑的？如果线上出了问题如何排查？

**答：**

**当前项目：**
- SQLAlchemy `echo=True` 输出 SQL 日志（开发环境）
- 健康检查端点 `/health` 可供监控平台探测

**生产环境应补充：**

1. **结构化日志：**
```python
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s - %(message)s'
)
logger = logging.getLogger(__name__)
logger.info(f"User {user_id} viewed news {news_id}")
```

2. **监控指标：**
   - 接口响应时间（Middleware 记录每个请求耗时）
   - 数据库连接池使用率
   - Redis 命中率
   - 错误率（按异常类型分类）

3. **排查思路：**
   ```
   用户反馈问题
     → 查看 Railway/Vercel 日志
     → 确认是前端还是后端问题（浏览器 Network 面板）
     → 后端：检查 /health 端点 → 查看错误日志 → 检查数据库连接
     → 前端：检查 Console 错误 → 检查 API 响应状态码 → 检查环境变量
   ```

---

### Q32: 如果需要给这个项目的 AI 聊天增加"上下文记忆"功能，怎么做？

**答：**

**方案设计：**

1. **会话管理：**
```sql
CREATE TABLE ai_conversation (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    title VARCHAR(200),             -- 会话标题
    created_at DATETIME DEFAULT NOW(),
    updated_at DATETIME DEFAULT NOW(),
    FOREIGN KEY (user_id) REFERENCES user(id)
);

CREATE TABLE ai_message (
    id INT PRIMARY KEY AUTO_INCREMENT,
    conversation_id INT NOT NULL,
    role ENUM('user','assistant','system'),
    content TEXT NOT NULL,
    created_at DATETIME DEFAULT NOW(),
    FOREIGN KEY (conversation_id) REFERENCES ai_conversation(id)
);
```

2. **前端改造：**
   - 每次对话带上 `conversation_id`
   - 从数据库加载历史消息拼入 `messages` 数组
   - 限制携带最近 N 轮对话（Token 有限）

3. **后端改造：**
```python
@router.post("/chat")
async def chat(req: ChatRequest, conversation_id: int = None):
    # 加载历史消息
    history = await get_conversation_history(conversation_id)
    # 拼接消息
    full_messages = history + req.messages
    # 控制 Token 长度（保留最近 10 轮）
    full_messages = full_messages[-20:]
    return StreamingResponse(stream_kimi(full_messages, model), ...)
```

---

## 附录：面试高频考点速查表

| 知识点 | 对应章节 | 面试出现频率 |
|--------|----------|-------------|
| FastAPI vs Flask/Django | Q2 | ★★★★★ |
| async/await 异步编程 | Q4, Q7 | ★★★★★ |
| 依赖注入 (Depends) | Q4 | ★★★★ |
| RESTful API 设计 | Q5, Q6 | ★★★★★ |
| SQLAlchemy ORM | Q7, Q8 | ★★★★ |
| 密码安全存储 (bcrypt) | Q11 | ★★★★ |
| Token vs JWT vs Session | Q10 | ★★★★★ |
| Redis 缓存策略 | Q13, Q14 | ★★★★★ |
| 缓存穿透/击穿/雪崩 | Q14 | ★★★★★ |
| SSE vs WebSocket | Q17 | ★★★★ |
| 跨域 CORS | Q3 | ★★★★ |
| Vue 3 Composition API | Q19 | ★★★★ |
| 路由懒加载 | Q20 | ★★★ |
| 前后端分离架构 | Q1, Q3 | ★★★★★ |
| 环境变量与安全 | Q16, Q24 | ★★★★ |
| 数据库连接池 | Q27 | ★★★★ |
| 异常处理设计 | Q28 | ★★★★ |
| 系统设计/架构演进 | Q29 | ★★★★★ |
| 功能设计题 | Q30, Q32 | ★★★★ |

---

> 本文档基于真实项目代码编写，建议结合源码阅读，理解每个实现细节背后的设计思路。