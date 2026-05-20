from typing import Any, Dict, List, Optional

from ..config.cache import get_cache,get_json_cache,set_cache

#redis 缓存-->key:value
# 自己设计key名

CATEGORIES_KEY = "news:categories"
NEWS_LIST_PREFIX = "news_list:"
#获取新闻缓存
async def get_cached_categories():
  return await get_json_cache(CATEGORIES_KEY)


#写入新闻缓存
#分类、配置 7200； 列表： 600 ； 详细： 1800 ； 验证码： 120-----数据越稳定，缓存越持久
async def set_cached_categories(data:List[Dict[str , Any]],expire:int = 7200):
  return  await set_cache(CATEGORIES_KEY,data,expire)
  
  
  
#列表写入
# key = news_list,分页：页码：每页数+数据+过期时间
async def set_cached_news_list(category_id:Optional[int],page:int,size:int,news_list:List[Dict[str,Any]],expire:int = 1800):
  category_part = category_id  if category_id is not None else "all"
  key = f"{NEWS_LIST_PREFIX}{category_part}:{page}:{size}"
  return await set_cache(key,news_list,expire)


async def get_cached_news_list(category_id:Optional[int],page:int,size:int):
    category_part = category_id or "all" 
    key = f"{NEWS_LIST_PREFIX}{category_part}:{page}:{size}"
    return await get_json_cache(key)