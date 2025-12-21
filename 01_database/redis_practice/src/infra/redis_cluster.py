from redis.cluster import RedisCluster, ClusterNode

_redis = RedisCluster(
    startup_nodes=[
        ClusterNode("redis1", 6379),
    ],
    decode_responses=True,
    socket_timeout=2,
    socket_connect_timeout=2,
)

def get_redis_cluster() -> RedisCluster:
    return _redis