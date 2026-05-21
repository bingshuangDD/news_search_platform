import json
import os
from typing import Any

import redis.asyncio as redis

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)



redis_client = redis.Redis(
  host=REDIS_HOST,  #主机地址
  port=REDIS_PORT, #端口号
  db=0, #redis数据库编号
  decode_responses=True #字节数据解码为字符串
  )

#设置/读取缓存的方法

async def get_cache(key:str):
  """获取缓存"""
  try:
    return await redis_client.get(key)
  except Exception as e:
    print(f"获取失败:{e}")
    return None


async def get_json_cache(key:str):
  """获取缓存"""
  try:
    data = await get_cache(key)
    if data:
      return json.loads(data)
    return None
  except Exception as e:
    print(f"获取json缓存失败:{e}")
    return None
  
async def set_cache(key:str,value: Any ,expire:int=3600):
  """设置缓存""" 
  try:
    if isinstance(value,dict):
      value = json.dumps(value, ensure_ascii=False) #保存中文
    elif isinstance(value,list):
      value = json.dumps(value , ensure_ascii=False)
    await redis_client.setex(key,expire,value)
    return True
  except Exception as e:
    print(f"设置缓存失败:{e}")
    return None