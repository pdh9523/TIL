import redis
from datetime import datetime
from typing import List, Tuple

from fastapi import APIRouter, Body, Depends

from src.infra.redis_client import get_redis
from src.utils.decorators import measure_time

TimeScaleRouter = APIRouter(prefix="/time-scale")

HSetRouter = APIRouter(prefix="/hset")
StringRouter = APIRouter(prefix="/string")

TIMESCALE_KEY = "test:timescale"

@HSetRouter.post("")
@measure_time
def hset_add(
    data: List[Tuple[str, datetime]] = Body(
        ..., embed=False, description='JSON 배열 예시: [["user1","2024-01-01T05:00:00"]]'
    ),
    r: redis.Redis = Depends(get_redis),
):
    pipe = r.pipeline()
    for user_id, ts in data:
        day_key = f"{TIMESCALE_KEY}:{user_id}:hset:{ts.strftime('%Y%m%d')}"
        hour_field = ts.strftime("%H")
        pipe.hincrby(day_key, hour_field, 1)
    pipe.execute()
    return {"status": "ok", "processed": len(data)}

@HSetRouter.get("")
@measure_time
def hset_find(
    user_id: str, 
    r: redis.Redis = Depends(get_redis)
    ):
    pattern = f"{TIMESCALE_KEY}:{user_id}:hset:*"
    cursor = 0
    keys = []

    while True:
        cursor, batch = r.scan(cursor=cursor, match=pattern, count=1000)
        keys.extend(batch)
        if cursor == 0:
            break
    
    keys.sort()

    pipe = r.pipeline()
    for key in keys:
        pipe.hgetall(key)
    results = pipe.execute() if keys else []

    data = {
        key: {hour: int(count) for hour, count in hours.items()}
        for key, hours in zip(keys, results)
    }

    return {
        "status": "ok",
        "user_id": user_id,
        # "keys": len(keys),
        # "data": data,
    }

@StringRouter.post("")
@measure_time
def string_add(
    data: List[Tuple[str, datetime]] = Body(
        ..., embed=False, description='JSON 배열 예시: [["user1","2024-01-01T05:00:00"]]'
    ),
    r: redis.Redis = Depends(get_redis),
):
    pipe = r.pipeline()
    for user_id, ts in data:
        day_key = f"{TIMESCALE_KEY}:{user_id}:string:{ts.strftime('%Y%m%d%H')}"
        pipe.incrby(day_key, 1)
    pipe.execute()
    return {"status": "ok", "processed": len(data)}

@StringRouter.get("")
@measure_time
def string_find(
    user_id: str,
    r: redis.Redis = Depends(get_redis)
):
    pattern = f"{TIMESCALE_KEY}:{user_id}:string:*"
    keys = sorted(list(r.scan_iter(match=pattern, count=10000)))

    values = r.mget(keys) if keys else []

    data = {}
    for key, count in zip(keys, values):
        if count is None:
            continue
        ts_token = key.rsplit(":", 1)[-1]
        day_token, hour = ts_token[:-2], ts_token[-2:]
        day_key = f"{TIMESCALE_KEY}:{user_id}:string:{day_token}"
        data.setdefault(day_key, {})[hour] = int(count)

    return {
        "status": "ok",
        "user_id": user_id,
        # "keys": len(keys),
        # "data": data,
    }

TimeScaleRouter.include_router(HSetRouter)
TimeScaleRouter.include_router(StringRouter)
