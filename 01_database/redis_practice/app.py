from fastapi import FastAPI
import uvicorn

import redis
import time
from functools import wraps

def measure_time(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = f(*args, **kwargs)
        end = time.perf_counter() - start
        print(f"{wrapper.__name__} 소요시간: {end:.03f}초")
        return result
    return wrapper


app = FastAPI()

r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

@app.post("/add")
@measure_time
def bulk_add_data():
    pipe = r.pipeline()
    now = time.time()
    for i in range(1000000):
        key = f"test:{now}:{i}"
        pipe.set(key, 0)
    pipe.execute()
    return {"status": "created"}


@app.get("/keys")
@measure_time
def get_all_data_with_keys():
    data = r.keys("test:*")
    return {
        "status": "ok",
        "length": len(data),
    }

@app.get("/ping")
@measure_time
def redis_ping():
    r.ping()
    return {"status": "ok", "timestamp": time.time()}

@app.get("/scan")
@measure_time
def get_all_data_with_scan():
    cursor = 0
    data = []
    while True:
        cursor, batch = r.scan(cursor=cursor, match="test:*", count=10000)
        data.extend(batch)
        if cursor == 0: break
    return {
        "status": "ok",
        "length": len(data),
    }

    # SCAN은 커서 기반이라 한 호출이 COUNT 힌트만큼만 훑고 끝나 KEYS처럼 전체를 오래 블로킹하지 않는다.
    # COUNT 기본값은 10이고 크게 줘도 내부에서 여러 호출로 쪼개주지 않으며, 값이 커질수록 한 호출 지연은 늘고 왕복 횟수는 줄어든다.
    # 여러 클라이언트가 SCAN을 돌리면 호출 단위로 번갈아 처리되어 짧은 요청이 끼어들 틈은 생기지만 CPU를 정확히 나누는 것은 아니다.    


if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
