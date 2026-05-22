# 新闻头条 - 全栈新闻资讯平台

**线上地址：[https://news-search-platform.vercel.app/](https://news-search-platform.vercel.app/)**

---

## 项目概述

新闻头条是一个全栈新闻资讯平台，提供新闻分类浏览、文章详情阅读、用户收藏/历史记录、个人中心管理以及 AI 智能聊天等功能。项目采用前后端分离架构，后端基于 FastAPI 提供 RESTful API 服务，前端基于 Vue 3 + Vant 构建移动端 SPA 应用。

---

## 技术栈

| 层级 | 技术 | 版本 |
|---|---|---|
| **后端框架** | FastAPI | >=0.100.0 |
| **ASGI 服务器** | Uvicorn | >=0.23.0 |
| **ORM** | SQLAlchemy (async) | >=2.0.0 |
| **数据库** | MySQL 8 | — |
| **数据库驱动** | aiomysql | >=0.2.0 |
| **缓存** | Redis | >=5.0.0 |
| **密码加密** | bcrypt | >=4.0.0 |
| **AI 集成** | Kimi API (Moonshot) + httpx | >=0.27.0 |
| **前端框架** | Vue 3 (Composition API) | — |
| **构建工具** | Vite 5 | — |
| **移动端 UI** | Vant 4 | — |
| **状态管理** | Pinia | — |
| **国际化** | vue-i18n | — |

---

## 项目结构

```
Fastapi+Vue-新闻头条项目/
├── backend/                        # 后端项目
│   ├── app/
│   │   ├── main.py                 # FastAPI 应用入口
│   │   ├── config/                 # 配置模块
│   │   │   ├── database.py         # 数据库连接（异步引擎、连接池、会话依赖）
│   │   │   └── cache.py            # Redis 缓存客户端配置
│   │   ├── models/                 # ORM 模型层 (SQLAlchemy)
│   │   │   ├── base.py             # 声明基类 + 时间戳混入
│   │   │   ├── users.py            # 用户模型 + 用户令牌模型
│   │   │   ├── news.py             # 新闻分类模型 + 新闻模型
│   │   │   ├── favorite.py         # 收藏模型
│   │   │   └── history.py          # 浏览历史模型
│   │   ├── schemas/                # Pydantic 数据校验/序列化
│   │   │   ├── base.py             # 新闻基础 Schema
│   │   │   ├── users.py            # 用户请求/响应 Schema
│   │   │   ├── favorite.py         # 收藏请求/响应 Schema
│   │   │   └── history.py          # 历史请求/响应 Schema
│   │   ├── crud/                   # 数据访问层（业务逻辑）
│   │   │   ├── users.py            # 用户注册/登录/Token 管理/信息更新
│   │   │   ├── news.py             # 新闻分类/列表/详情/浏览量/相关推荐
│   │   │   ├── news_cache.py       # 带 Redis 缓存的新闻查询
│   │   │   ├── favorite.py         # 收藏增删查改
│   │   │   └── history.py          # 历史记录增删查改
│   │   ├── routers/                # API 路由层
│   │   │   ├── news.py             # /api/news/* 新闻接口
│   │   │   ├── users.py            # /api/user/* 用户接口
│   │   │   ├── favorite.py         # /api/favorite/* 收藏接口
│   │   │   ├── history.py          # /api/history/* 历史接口
│   │   │   └── ai.py               # /api/ai/* AI 聊天接口（SSE 流式转发）
│   │   ├── cache/                  # 缓存键管理
│   │   │   └── news_cache.py       # 新闻缓存键设计 + 读写封装
│   │   └── utils/                  # 工具模块
│   │       ├── auth.py             # Token 认证依赖（get_current_user）
│   │       ├── security.py         # bcrypt 密码哈希/验证
│   │       ├── response.py         # 统一 JSON 响应格式
│   │       ├── exception.py        # 各类异常处理函数
│   │       └── exception_handler.py # 异常处理器注册
│   ├── db/
│   │   └── init.sql                # 数据库建表 + 初始数据（50+条新闻）
│   ├── .env                        # 环境变量（Kimi API Key）
│   ├── railway.json                # Railway 部署配置
│   └── requirements.txt            # Python 依赖
│
└── frontend/                       # 前端项目（Vue 3 + Vant）
    ├── src/
    │   ├── views/                  # 页面组件（10个页面）
    │   ├── components/             # 公共组件
    │   ├── store/                  # Pinia 状态管理
    │   ├── router/                 # Vue Router 路由配置
    │   ├── i18n/                   # 国际化（中/英）
    │   └── config/api.js           # API 请求配置
    ├── vercel.json                 # Vercel 部署配置
    └── vite.config.js              # Vite 构建配置
```

---

## 后端架构详解

### 1. 应用入口 ([main.py](backend/app/main.py))

FastAPI 应用在 `backend/app/main.py` 中创建，主要完成以下初始化：

- 创建 `FastAPI` 实例，标题为"新闻平台项目"
- 注册 **CORS 中间件**（开发阶段允许所有源）
- 注册 **5 个路由模块**：新闻、用户、收藏、历史、AI 聊天
- 注册 **全局异常处理器**（HTTP 异常、数据库完整性异常、SQLAlchemy 异常、通用异常）
- 提供 `/` 根路径和 `/health` 健康检查端点

```python
app = FastAPI(title="新闻平台项目", version="1.0.0")
register_exception(app)
app.add_middleware(CORSMiddleware, allow_origins=["*"], ...)
app.include_router(news.router)
app.include_router(users.router)
app.include_router(favorite.router)
app.include_router(history.router)
app.include_router(ai.router)
```

### 2. 数据库设计

项目使用 **MySQL 8 + SQLAlchemy 2.x 异步引擎**，共 7 张表：

#### 表结构总览

| 表名 | 说明 | 关键字段 |
|---|---|---|
| `user` | 用户信息 | id, username(UNIQUE), password(bcrypt), nickname, avatar, gender(ENUM), bio, phone(UNIQUE) |
| `user_token` | 用户认证令牌 | id, user_id(FK), token(UUID, UNIQUE), expires_at |
| `news_category` | 新闻分类 | id, name(UNIQUE), sort_order |
| `news` | 新闻文章 | id, title, description, content(TEXT), image, author, category_id(FK), views, publish_time |
| `related_news` | 相关新闻关联 | id, news_id(FK), related_news_id(FK), UNIQUE(news_id, related_news_id) |
| `favorite` | 用户收藏 | id, user_id(FK), news_id(FK), UNIQUE(user_id, news_id) |
| `history` | 浏览历史 | id, user_id(FK), news_id(FK), view_time |
| `ai_chat` | AI 聊天记录 | id, user_id(FK), message(TEXT), response(TEXT) |

#### 数据库配置 ([config/database.py](backend/app/config/database.py))

- **异步引擎**：使用 `create_async_engine` 创建 SQLAlchemy 异步引擎，驱动为 `aiomysql`
- **连接池**：`pool_size=10`, `max_overflow=20`
- **Railway 兼容**：自动将 Railway 注入的 `mysql://` 格式转换为 `mysql+aiomysql://`
- **会话管理**：通过 `get_db()` 依赖注入异步会话，自动处理 commit/rollback/close

```python
async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=True,
    pool_size=10,
    max_overflow=20,
)

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
```

#### 索引设计

- `news` 表：`category_id` 索引 + `publish_time` 降序索引（优化分类列表查询）
- `favorite` 表：`user_id`、`news_id` 分别索引 + `(user_id, news_id)` 联合唯一索引
- `history` 表：`user_id`、`news_id`、`view_time` 分别索引
- `user_token` 表：`token` 唯一索引 + `user_id` 索引

### 3. 认证系统

#### 密码加密 ([utils/security.py](backend/app/utils/security.py))

使用 **bcrypt** 直接进行密码哈希，不依赖 passlib 的 CryptContext：

```python
import bcrypt

def get_hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())
```

#### Token 认证 ([utils/auth.py](backend/app/utils/auth.py))

采用 **Bearer Token** 方案，Token 为 UUID 格式，存储于 `user_token` 表：

- **生成**：登录/注册时生成 UUID Token，有效期 7 天
- **存储**：每个用户对应一条 Token 记录，再次登录时更新（upsert 模式）
- **验证**：从请求头 `Authorization: Bearer <token>` 提取 Token，查库验证有效性
- **过期处理**：Token 过期返回 401

```python
async def get_current_user(authorization: str = Header(..., alias="Authorization"),
                           db: AsyncSession = Depends(get_db)):
    token = authorization.replace("Bearer ", "")
    user = await users.get_user_by_token(db, token)
    if not user:
        raise HTTPException(status_code=401, detail="无效的令牌")
    return user
```

#### 用户 CRUD ([crud/users.py](backend/app/crud/users.py))

| 操作 | 函数 | 说明 |
|---|---|---|
| 查询用户 | `get_user_by_username()` | 按用户名查询 |
| 创建用户 | `create_user()` | 密码 bcrypt 加密后入库 |
| 创建 Token | `create_token()` | UUID + 7天过期，upsert |
| 认证用户 | `authenticate_user()` | 用户名 + 密码校验 |
| Token 查用户 | `get_user_by_token()` | 根据 Token 查用户（含过期检查） |
| 更新用户 | `update_user()` | 部分更新（exclude_unset + exclude_none） |
| 修改密码 | `change_password()` | 先验证旧密码，再更新新密码 |

### 4. API 接口设计

所有接口返回统一的 JSON 格式：

```json
{
  "code": 200,
  "message": "操作成功",
  "data": { ... }
}
```

#### 新闻模块 (`/api/news`)

| 方法 | 路径 | 说明 | 认证 |
|---|---|---|---|
| GET | `/api/news/categories` | 获取全部分类列表（Redis 缓存） | 否 |
| GET | `/api/news/list?categoryId=&page=&pageSize=` | 分类新闻分页列表（Redis 缓存） | 否 |
| GET | `/api/news/detail?id=` | 新闻详情（含浏览量+1 + 相关推荐） | 否 |

#### 用户模块 (`/api/user`)

| 方法 | 路径 | 说明 | 认证 |
|---|---|---|---|
| POST | `/api/user/register` | 用户注册（返回 Token + 用户信息） | 否 |
| POST | `/api/user/login` | 用户登录（返回 Token + 用户信息） | 否 |
| GET | `/api/user/info` | 获取当前用户信息 | 是 |
| PUT | `/api/user/update` | 更新用户资料（昵称/头像/简介/性别/手机号） | 是 |
| PUT | `/api/user/password` | 修改密码（需提供旧密码） | 是 |

#### 收藏模块 (`/api/favorite`)

| 方法 | 路径 | 说明 | 认证 |
|---|---|---|---|
| GET | `/api/favorite/check?newsId=` | 检查是否已收藏某新闻 | 是 |
| POST | `/api/favorite/add` | 添加收藏 | 是 |
| DELETE | `/api/favorite/remove?newsId=` | 取消收藏 | 是 |
| GET | `/api/favorite/list?page=&pageSize=` | 分页获取收藏列表 | 是 |
| DELETE | `/api/favorite/clear` | 清空全部收藏 | 是 |

#### 历史记录模块 (`/api/history`)

| 方法 | 路径 | 说明 | 认证 |
|---|---|---|---|
| GET | `/api/history/check?newsId=` | 检查是否已浏览某新闻 | 是 |
| POST | `/api/history/add` | 添加/更新浏览记录（已存在则更新时间） | 是 |
| DELETE | `/api/history/delete/{history_id}` | 删除单条历史记录 | 是 |
| GET | `/api/history/list` | 分页获取历史记录列表 | 是 |
| DELETE | `/api/history/clear` | 清空全部历史记录 | 是 |

#### AI 聊天模块 (`/api/ai`)

| 方法 | 路径 | 说明 | 认证 |
|---|---|---|---|
| POST | `/api/ai/chat` | AI 聊天（SSE 流式转发到 Kimi API） | 否 |

### 5. Redis 缓存层

缓存层分层设计，针对不同数据特征设置不同过期策略：

#### 缓存架构

```
请求 → 路由层 → news_cache (CRUD + 缓存逻辑) → Redis / MySQL
```

#### 缓存键设计 ([cache/news_cache.py](backend/app/cache/news_cache.py))

| 缓存对象 | Key 格式 | 过期时间 | 策略依据 |
|---|---|---|---|
| 分类列表 | `news:categories` | 7200s (2小时) | 分类数据极少变动 |
| 新闻列表 | `news_list:{category_id}:{page}:{size}` | 1800s (30分钟) | 新闻列表更新频率中等 |

#### 缓存读写流程 ([crud/news_cache.py](backend/app/crud/news_cache.py))

```
1. 请求到达 → 尝试从 Redis 读取缓存
2. 缓存命中 → 反序列化为 ORM 对象直接返回（跳过数据库）
3. 缓存未命中 → 查询 MySQL → 序列化为 JSON → 写入 Redis → 返回数据
```

```python
async def get_category(db: AsyncSession, skip: int = 0, limit: int = 100):
    cache_categories = await get_cached_categories()
    if cache_categories:
        return cache_categories
    # 缓存未命中，查数据库
    result = await db.execute(select(Category).offset(skip).limit(limit))
    news_list = result.scalars().all()
    if news_list:
        await set_cached_categories(jsonable_encoder(news_list))
    return news_list
```

#### Redis 配置 ([config/cache.py](backend/app/config/cache.py))

- 优先读取 `REDIS_URL`（Railway 自动注入）
- 回退到手动配置 `REDIS_HOST` / `REDIS_PORT` / `REDIS_PASSWORD`
- 提供 `get_cache()`、`get_json_cache()`、`set_cache()` 三个通用工具函数

### 6. AI 聊天集成 ([routers/ai.py](backend/app/routers/ai.py))

AI 聊天模块作为 **服务端代理** 转发请求到 Kimi API（Moonshot），保证 API Key 不暴露到前端：

- **模型**：默认 `kimi-k2.6`，可通过环境变量 `KIMI_MODEL` 配置
- **传输方式**：**SSE (Server-Sent Events)** 流式传输
- **实现**：使用 `httpx.AsyncClient` 的 `stream()` 方法逐块转发响应字节

```python
async def stream_kimi(messages: list[dict], model: str):
    async with httpx.AsyncClient(timeout=httpx.Timeout(120.0, connect=10.0)) as client:
        async with client.stream("POST", f"{KIMI_BASE_URL}/v1/chat/completions",
            headers={"Authorization": f"Bearer {KIMI_API_KEY}", ...},
            json={"model": model, "messages": messages, "stream": True},
        ) as response:
            async for chunk in response.aiter_bytes():
                yield chunk
```

### 7. 统一异常处理 ([utils/exception_handler.py](backend/app/utils/exception_handler.py))

全局注册的异常处理器按优先级从具体到通用排列：

| 异常类型 | 处理方式 | 示例场景 |
|---|---|---|
| `HTTPException` | 返回自定义 code + message | 404 新闻不存在、401 认证失败 |
| `IntegrityError` | 解析重复键/外键冲突消息 | 用户名重复、关联数据不存在 |
| `SQLAlchemyError` | 返回通用数据库错误 | 连接超时、查询异常 |
| `Exception` | 兜底处理，区分 DEBUG 模式 | 未知运行时错误 |

### 8. 统一响应格式 ([utils/response.py](backend/app/utils/response.py))

```python
def success_response(message: str = "success", data=None):
    content = {"code": 200, "message": message, "data": data}
    return JSONResponse(content=jsonable_encoder(content))
```

所有成功响应通过 `jsonable_encoder` 将 ORM 对象/Pydantic 模型统一转换为 JSON 兼容格式。

---

## 数据库初始化

项目提供了完整的建表和种子数据脚本 [backend/db/init.sql](backend/db/init.sql)：

- **8 个新闻分类**：头条、社会、国内、国际、娱乐、体育、科技、财经
- **50+ 条预置新闻**：涵盖时政、科技、经济、社会、教育、文化等领域
- **关联推荐数据**：通过 `related_news` 表建立新闻间关联关系

---

## 部署架构

```
┌──────────────┐     ┌─────────────────────┐     ┌───────────┐
│  Vercel      │────▶│  Railway            │────▶│  MySQL 8  │
│  (Vue 3 SPA) │     │  (FastAPI + Uvicorn)│     │  (Railway)│
│              │     │                     │     │           │
│  前端静态托管 │     │  后端 API 服务       │────▶│  Redis    │
│  SPA Rewrites│     │  Nixpacks 构建       │     │  (Railway)│
└──────────────┘     └─────────────────────┘     └───────────┘
```

### 后端部署 ([railway.json](backend/railway.json))

- **平台**：Railway (PaaS)
- **构建器**：Nixpacks（自动识别 Python 项目）
- **启动命令**：`uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- **重启策略**：`ON_FAILURE`（仅在异常退出时重启）
- **环境变量**：`DATABASE_URL`、`REDIS_URL` 由 Railway 自动注入

### 前端部署

- **平台**：Vercel
- **构建命令**：`npx vite build`
- **输出目录**：`dist`
- **SPA 路由**：所有路径重写至 `index.html`

---

## 本地开发

### 后端

```bash
# 1. 进入后端目录
cd backend

# 2. 创建虚拟环境并激活
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 3. 安装依赖
pip install -r requirements.txt

# 4. 初始化数据库（执行 init.sql）
mysql -u root -p < db/init.sql

# 5. 启动 Redis（确保本地 Redis 运行中）

# 6. 配置环境变量（.env）
# KIMI_API_KEY=sk-xxx
# KIMI_BASE_URL=https://api.moonshot.cn
# KIMI_MODEL=kimi-k2.6

# 7. 启动服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 前端

```bash
# 1. 进入前端目录
cd frontend

# 2. 安装依赖
npm install

# 3. 启动开发服务器
npm run dev
# 默认运行在 http://localhost:3000
```

---

## 环境变量

### 后端

| 变量 | 说明 | 默认值 |
|---|---|---|
| `DATABASE_URL` | MySQL 连接字符串 | `mysql+aiomysql://root:123456@localhost:3306/news_app` |
| `REDIS_URL` | Redis 连接字符串（Railway 注入） | — |
| `REDIS_HOST` | Redis 主机（REDIS_URL 不存在时使用） | `localhost` |
| `REDIS_PORT` | Redis 端口 | `6379` |
| `REDIS_PASSWORD` | Redis 密码 | — |
| `KIMI_API_KEY` | Kimi API 密钥 | — |
| `KIMI_BASE_URL` | Kimi API 地址 | `https://api.moonshot.cn` |
| `KIMI_MODEL` | Kimi 模型名称 | `kimi-k2.6` |

### 前端

| 变量 | 说明 |
|---|---|
| `VITE_API_BASE_URL` | 后端 API 地址（生产环境） |

---

## 前端简述

前端基于 **Vue 3 Composition API + Vant 4 移动端组件库** 构建，主要特性：

- **10 个页面**：首页、新闻详情、分类管理、AI 聊天、收藏、历史、个人中心、编辑资料、登录、注册
- **底部导航栏**：首页、AI 聊天、我的（三 Tab 布局）
- **状态管理**：Pinia + 持久化插件，管理用户登录态、主题切换、语言切换
- **国际化**：支持中文/英文切换（vue-i18n）
- **多主题**：浅色/深色/蓝色/绿色四种主题配色

---

## License

MIT
