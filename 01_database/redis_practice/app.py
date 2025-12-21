import time

import redis
import uvicorn

from fastapi import FastAPI, Depends
from redis.cluster import RedisCluster

from utils.decorators import measure_time
from infra.redis_client import get_redis
from infra.redis_cluster import get_redis_cluster
from keys_vs_scan import QueryRouter
from list_vs_zset import QueueRouter
from string_vs_hset import TimeScaleRouter

app = FastAPI()

app.include_router(QueryRouter)
app.include_router(QueueRouter)
app.include_router(TimeScaleRouter)

@app.get("/redis/ping")
@measure_time
def redis_ping(r :redis.Redis = Depends(get_redis)):
    r.ping()
    return {"status": "ok", "timestamp": time.time()}

@app.get("/cluster/ping")
@measure_time
def redis_cluster_ping(rc : RedisCluster = Depends(get_redis_cluster)):
    rc.ping()
    return {"status": "ok", "timestamp": time.time()}

@app.get("/count")
@measure_time
def get_count(pattern: str, r: redis.Redis = Depends(get_redis)):
    res = sum(1 for _ in r.scan_iter(match=pattern, count=1000))
    return {
        "status": "ok",
        "count": res,
    }

@app.delete("/clear")
@measure_time
def redis_clear(pattern: str = "test:*", r: redis.Redis = Depends(get_redis)):
    deleted = 0
    batch_size = 1000
    pipe = r.pipeline()

    for key in r.scan_iter(match=pattern, count=batch_size):
        pipe.unlink(key)
        deleted += 1
        if deleted % batch_size == 0:
            pipe.execute()

    if deleted % batch_size:
        pipe.execute()

    return {"status": "no content", "deleted": deleted, "pattern": pattern}

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
