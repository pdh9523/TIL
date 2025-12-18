import time
import random
import string
from typing import List

import redis
from fastapi import APIRouter, Body, Depends, HTTPException

from infra.redis_client import get_redis
from utils.decorators import measure_time


QueueRouter = APIRouter(prefix="/queue")

ListRouter = APIRouter(prefix="/list")
ZSetRouter = APIRouter(prefix="/zset")

LIST_KEY = "test:list"
ZSET_KEY = "test:zset"

def random_user_id():
    return "user_" + "".join(random.choices(string.ascii_lowercase + string.digits, k=8))

@ListRouter.post("/enqueue")
@measure_time
def list_enqueue(
    ids: List[str] = Body(..., embed=False, description='JSON 배열로 보낼 것. 예: ["u1","u2"]'),
    r: redis.Redis = Depends(get_redis),
):
    if not ids:
        raise HTTPException(status_code=400, detail="ids list is empty")

    pipe = r.pipeline()
    for user_id in ids:
        pipe.rpush(LIST_KEY, user_id)
    pipe.execute()

    return {
        "status": "created", 
        "type": "list", 
        "enqueued": len(ids)
    }

@ListRouter.get("/position")
@measure_time
def list_position(user_id: str, r: redis.Redis = Depends(get_redis)):
    total = r.llen(LIST_KEY)
    pos = r.lpos(LIST_KEY, user_id) +1
    return {
        "status": "ok",
        "type": "list",
        "total": total,
        "position": pos,
    }

@ListRouter.get("/top100")
@measure_time
def list_top100(r: redis.Redis = Depends(get_redis)):
    total = r.llen(LIST_KEY)
    users = r.lrange(LIST_KEY, 0, 100-1)
    return {
        "status": "ok",
        "total": total,
        "count": len(users),
    }

@ListRouter.get("/bottom100")
@measure_time
def list_bottom100(r: redis.Redis = Depends(get_redis)):
    total = r.llen(LIST_KEY)
    start = max(0, total-100)
    users = r.lrange(LIST_KEY, start, total-1)
    return {
        "status": "ok",
        "total": total,
        "count": len(users),
    }

'''
=== ZSET ===
'''

@ZSetRouter.get("/position")
@measure_time
def zset_position(user_id: str, r: redis.Redis = Depends(get_redis)):
    total = r.zcard(ZSET_KEY)
    pos = r.zrank(ZSET_KEY, user_id) + 1
    return {
        "status": "ok",
        "type": "zset",
        "total": total,
        "position": pos
    }

@ZSetRouter.post("/enqueue")
@measure_time
def zset_enqueue(
    ids: List[str] = Body(..., embed=False, description='JSON 배열로 보낼 것. 예: ["u1","u2"]'),
    r: redis.Redis = Depends(get_redis),
):
    if not ids:
        raise HTTPException(status_code=400, detail="ids list is empty")

    pipe = r.pipeline()
    for user_id in ids:
        pipe.zadd(ZSET_KEY, {user_id: time.time()})
    pipe.execute()

    return {
        "status": "created", 
        "type": "list", 
        "enqueued": len(ids)
    }

@ZSetRouter.get("/top100")
def zset_top100(r: redis.Redis = Depends(get_redis)):
    total = r.zcard(ZSET_KEY)
    users = r.zrange(ZSET_KEY, 0, 100-1)
    return {
        "status": "ok",
        "total": total,
        "count": len(users),
    }

@ZSetRouter.get("/bottom100")
def zset_bottom100(r: redis.Redis = Depends(get_redis)):
    total = r.zcard(ZSET_KEY)
    users = r.zrevrange(ZSET_KEY, 0, 100-1)
    return {
        "status": "ok",
        "total": total,
        "count": len(users),
    }


QueueRouter.include_router(ListRouter)
QueueRouter.include_router(ZSetRouter)
