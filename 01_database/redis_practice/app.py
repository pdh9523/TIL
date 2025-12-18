from fastapi import FastAPI, Depends
import uvicorn

import redis
import time

from utils.decorators import measure_time
from infra.redis_client import get_redis
from keys_vs_scan import QueryRouter

app = FastAPI()

app.include_router(QueryRouter)

@app.get("/ping")
@measure_time
def redis_ping(r :redis.Redis = Depends(get_redis)):
    r.ping()
    return {"status": "ok", "timestamp": time.time()}

@app.delete("/clear")
@measure_time
def redis_clear(r: redis.Redis = Depends(get_redis), pattern: str = "test:*"):
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
