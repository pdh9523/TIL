import time

import redis
import uvicorn

from fastapi import FastAPI, Depends
from redis.cluster import RedisCluster

from src.utils.decorators import measure_time
from src.infra.redis_client import get_redis
from src.infra.redis_cluster import get_redis_cluster
from src.keys_vs_scan import QueryRouter
from src.list_vs_zset import QueueRouter
from src.string_vs_hset import TimeScaleRouter
from src.hash_tag_scan_vs_hierachy_scan import SearchRouter

app = FastAPI()

app.include_router(QueryRouter)
app.include_router(QueueRouter)
app.include_router(TimeScaleRouter)
app.include_router(SearchRouter)

@app.get("/redis/ping")
@measure_time
def redis_ping(r: redis.Redis = Depends(get_redis)):
    r.ping()
    return {"status": "ok", "timestamp": time.time()}

@app.get("/stats")
@measure_time
def redis_stats(r: redis.Redis = Depends(get_redis)):
    info = r.info(section="commandstats")
    stat = info.get("cmdstat_scan") or {}
    if not isinstance(stat, dict):
        stat = {}
    return {
        "status": "ok",
        "scan_calls": stat.get("calls", 0),
        "usec_total": stat.get("usec", 0),
        "usec_per_call": stat.get("usec_per_call", 0),
    }

@app.post("/stats/reset")
@measure_time
def redis_stats_reset(r: redis.Redis = Depends(get_redis)):
    r.config_resetstat()
    return {"status": "ok", "message": "commandstats reset"}

@app.get("/cluster/ping")
@measure_time
def redis_cluster_ping(rc: RedisCluster = Depends(get_redis_cluster)):
    rc.ping()
    return {"status": "ok", "timestamp": time.time()}

@app.get("/cluster/stats")
@measure_time
def redis_cluster_stats(rc: RedisCluster = Depends(get_redis_cluster)):
    res = dict()
    for node in rc.get_primaries():
        # 각 노드별 INFO를 직접 조회해야 노드별 SCAN 집계가 분리된다.
        info = rc.info(section="commandstats", target_nodes=node)
        stat = info.get("cmdstat_scan") or {}
        if not isinstance(stat, dict):
            stat = {}
        res[f"{node.host}:{node.port}"] = {
            "scan_calls": stat.get("calls", 0),
            "usec_total": stat.get("usec", 0),
            "usec_per_call": stat.get("usec_per_call", 0),
        }
    res["status"] = "ok"
    return res

@app.post("/cluster/stats/reset")
@measure_time
def redis_cluster_stats_reset(rc: RedisCluster = Depends(get_redis_cluster)):
    # 프라이머리 노드들의 commandstats를 일괄 초기화한다.
    rc.config_resetstat(target_nodes=rc.PRIMARIES)
    return {"status": "ok", "message": "cluster commandstats reset"}

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

@app.delete("/cluster/clear")
@measure_time
def redis_cluster_clear(pattern: str = "test:*", rc: RedisCluster = Depends(get_redis_cluster)):
    deleted = 0
    batch_size = 1000
    pipe = rc.pipeline()

    for key in rc.scan_iter(match=pattern, count=batch_size):
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
