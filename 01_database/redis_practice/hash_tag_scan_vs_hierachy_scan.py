import time

from typing import List

from fastapi import APIRouter, Depends
from redis.cluster import RedisCluster

from utils.decorators import measure_time
from infra.redis_cluster import get_redis_cluster

SearchRouter = APIRouter(prefix="/search")

HashTagRouter = APIRouter(prefix="/hash-tag")
HierachyRouter = APIRouter(prefix="/hierachy")

@HashTagRouter.get("")
def get_data_with_tag(
    user_id: str,
    rc: RedisCluster = Depends(get_redis_cluster)
    ):
    pattern = f"test:user:{{{user_id}}}:*"
    # 해시태그로 슬롯을 고정한 키가 모여 있는 노드를 지정해 단일 노드만 스캔한다.
    target_node = rc.get_node_from_key(f"test:user:{{{user_id}}}:0")
    counts = sum(
        1
        for _ in rc.scan_iter(
            match=pattern,
            count=1000,
            target_nodes=target_node,
        )
    )
    return {
        "status": "ok",
        "type": "hash-tag",
        "count": counts
    }

@HashTagRouter.post("/add")
@measure_time
def bulk_add_data_with_tag(
    user_ids: List[int],
    rc: RedisCluster = Depends(get_redis_cluster),
    ):
    pipe = rc.pipeline()
    for user_id in user_ids:
        for _ in range(100000):
            pipe.incrby(f"test:user:{{{user_id}}}:{time.time()}")
    pipe.execute()

    return {
        "status": "created", 
        "type": "hash-tag",
        "length": len(user_ids) * 100000
    }

@HierachyRouter.get("")
@measure_time
def get_data_with_hierachy(
    user_id: str,
    rc: RedisCluster = Depends(get_redis_cluster)
    ):
    counts = sum(1 for _ in rc.scan_iter(match=f"test:user:{user_id}:*", count=1000))
    return {
        "status": "ok",
        "type": "hierachy",
        "count": counts
    }

@HierachyRouter.post("/add")
@measure_time
def bulk_add_data_with_hierachy(
    user_ids: List[int],
    rc: RedisCluster = Depends(get_redis_cluster),
    ):
    pipe = rc.pipeline()
    for user_id in user_ids:
        for _ in range(100000):
            pipe.incrby(f"test:user:{user_id}:{time.time()}")
    pipe.execute()

    return {
        "status": "created", 
        "type": "hierachy",
        "length": len(user_ids) * 100000
    }

SearchRouter.include_router(HierachyRouter)
SearchRouter.include_router(HashTagRouter)
