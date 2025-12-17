from fastapi import FastAPI, Depends
import uvicorn

import redis
import time

from lib.decorators import measure_time
from infra.redis_client import get_redis
from keys_vs_scan import QueryRouter

app = FastAPI()

app.include_router(QueryRouter)

@app.get("/ping")
@measure_time
def redis_ping(r :redis.Redis = Depends(get_redis)):
    r.ping()
    return {"status": "ok", "timestamp": time.time()}

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
