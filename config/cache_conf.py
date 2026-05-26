import json
import os
from typing import Any

import redis.asyncio as redis

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DB = int(os.getenv("REDIS_DB", "0"))

#创建 Redis的连接对象
redis_client = redis.Redis(
    host=REDIS_HOST,   #Redis服务器的主机地址，默认为localhost
    port=REDIS_PORT,   #Redis服务器的端口号，默认为6379
    db=REDIS_DB,       #Redis数据库的索引，默认为0
    decode_responses= True  #自动解码响应结果为字符串True
)

#设置和读取 （字符串 和 列表或字典）“[{}]”
#读取：字符串
async def get_cache(key: str):
    #return await redis_client.get(key)

    try:
        return await redis_client.get(key)
    except Exception as e:
        print(f"获取缓存失败：{e}")
        return None

#读取：列表或字典
async def get_json_cache(key: str):
    try:
        data = await redis_client.get(key)
        if data:
            return json.loads(data)  #序列化
        return None
    except Exception as e:
        print(f"获取JSON缓存失败：{e}")
        return None

#设置缓存setex(key,expire,value)
async def set_cache(key: str, value: Any, expire: int):
    try:
        if isinstance(value, (dict,list)):
            #转字符串再存
            value = json.dumps(value,ensure_ascii=False) #中文正常保存
        await redis_client.setex(key,expire,value)
        return True
    except Exception as e:
        print(f"设置缓存失败：{e}")
        return False
