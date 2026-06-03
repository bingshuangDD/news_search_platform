"""
Redis 分布式互斥锁 —— 防止缓存击穿

使用方式:
    token = await acquire_lock(redis_client, "news:categories")
    if token:
        try:
            # 查库 & 写缓存
        finally:
            await release_lock(redis_client, "news:categories", token)
"""

import asyncio
import uuid

# ── 默认参数 ──
DEFAULT_LOCK_TIMEOUT = 10        # 锁最大持有时间（秒）
DEFAULT_RETRY_INTERVAL = 0.1     # 抢锁失败后重试间隔（秒）
DEFAULT_MAX_RETRIES = 10         # 最大重试次数

# ── 锁 key 前缀 ──
LOCK_PREFIX = "mutex:"


def _lock_key(cache_key: str) -> str:
    """生成互斥锁专用的 Redis key"""
    return f"{LOCK_PREFIX}{cache_key}"


async def acquire_lock(redis_client, key: str, timeout: int = DEFAULT_LOCK_TIMEOUT) -> str | None:
    """
    获取分布式互斥锁（SET key value NX EX timeout）

    参数:
        redis_client:  redis.asyncio.Redis 实例
        key:           业务缓存 key（内部自动加 mutex: 前缀）
        timeout:       锁过期秒数，防止持锁者崩溃导致死锁

    返回:
        成功 → 锁 token（UUID 字符串），用于后续 release_lock
        失败 → None
    """
    lock_key = _lock_key(key)
    token = uuid.uuid4().hex
    try:
        acquired = await redis_client.set(lock_key, token, nx=True, ex=timeout)
        return token if acquired else None
    except Exception as e:
        print(f"[RedisMutex] 获取锁失败 key={key}: {e}")
        return None


async def release_lock(redis_client, key: str, token: str) -> bool:
    """
    安全释放互斥锁（Lua 脚本保证原子性）

    只有 token 匹配时才删除，防止误删其他请求刚获取的锁。

    返回:
        True  → 成功释放
        False → 锁不存在或 token 不匹配（已过期 / 被他人持有）
    """
    lock_key = _lock_key(key)
    lua_script = """
    if redis.call("GET", KEYS[1]) == ARGV[1] then
        return redis.call("DEL", KEYS[1])
    else
        return 0
    end
    """
    try:
        result = await redis_client.eval(lua_script, 1, lock_key, token)
        return result == 1
    except Exception as e:
        print(f"[RedisMutex] 释放锁失败 key={key}: {e}")
        return False


async def get_cache_with_mutex(
    redis_client,
    cache_read,       # async (key) -> data | None   读取缓存
    cache_write,      # async (key, data, expire)     写入缓存
    cache_key: str,
    fetch_func,       # async () -> data              查数据库
    expire: int = 3600,
    lock_timeout: int = DEFAULT_LOCK_TIMEOUT,
    retry_interval: float = DEFAULT_RETRY_INTERVAL,
    max_retries: int = DEFAULT_MAX_RETRIES,
):
    """
    带互斥锁的缓存读取 —— 一站式防止缓存击穿。

    流程:
      1. 查缓存 → 命中直接返回
      2. 未命中 → 尝试获取互斥锁
         ├─ 拿到锁: 双重检查 → 查 DB → 写缓存 → 释放锁 → 返回
         └─ 没拿到: 自旋等待 → 重试读缓存 → 超时降级查库
    """
    # ① 查缓存
    data = await cache_read(cache_key)
    if data is not None:
        return data

    # ② 尝试获取互斥锁
    token = await acquire_lock(redis_client, cache_key, timeout=lock_timeout)

    if token:
        # ③ 拿到锁 —— 负责查库 & 回写缓存
        try:
            # 双重检查：上一个持锁者可能已写入缓存
            data = await cache_read(cache_key)
            if data is not None:
                return data

            # 查数据库
            data = await fetch_func()

            # 写缓存
            if data:
                await cache_write(cache_key, data, expire)

            return data
        finally:
            await release_lock(redis_client, cache_key, token)
    else:
        # ④ 没拿到锁 —— 自旋等待缓存就绪
        for _ in range(max_retries):
            await asyncio.sleep(retry_interval)
            data = await cache_read(cache_key)
            if data is not None:
                return data

        # ⑤ 重试耗尽，降级直接查库
        print(f"[RedisMutex] 等待缓存超时，降级查库: {cache_key}")
        return await fetch_func()
