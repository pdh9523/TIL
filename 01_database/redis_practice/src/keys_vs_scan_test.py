"""
조건:
서버가 8000포트에서 실행중이고, 'POST /add' 를 통해 1000만개의 데이터를 생성했습니다.
"""

import threading
import time
from concurrent.futures import ThreadPoolExecutor

import requests

BASE_URL = "http://127.0.0.1:8000"
TIMEOUT = 600


def call(name: str, path: str, start_evt: threading.Event | None = None):
    if start_evt is not None:
        start_evt.wait()
    t0 = time.perf_counter()
    resp = requests.get(f"{BASE_URL}{path}", timeout=TIMEOUT)
    dt = time.perf_counter() - t0
    print(f"{name}: {resp.status_code}, {dt:.3f}s, body={resp.json()}")
    return name, dt

def run_pair(label: str, query_path: str, ping_path: str):
    print(f"\n=== {label} ===")
    start_evt = threading.Event()
    with ThreadPoolExecutor(max_workers=2) as pool:
        futs = [
            pool.submit(call, f"{label}-query", query_path, start_evt),
            pool.submit(call, f"{label}-ping", ping_path, start_evt),
        ]
        start_evt.set()
        result = dict(f.result() for f in futs)
    return result

def test_query():
    scan_result = run_pair("scan", "/query/scan", "/ping")
    time.sleep(0.5)
    keys_result = run_pair("keys", "/query/keys", "/ping")

    # 기대: KEYS가 쿼리는 더 빠르고, ping은 더 느리다.
    assert scan_result["scan-query"] >= keys_result["keys-query"]
    assert scan_result["scan-ping"] < keys_result["keys-ping"]

if __name__ == "__main__":
    test_query()

'''
=== scan ===
scan-ping: 200, 0.039s, body={'status': 'ok'}
scan-query: 200, 10.898s, body={'status': 'ok', 'length': 10000000}

=== keys ===
keys-ping: 200, 1.410s, body={'status': 'ok'}
keys-query: 200, 8.059s, body={'status': 'ok', 'length': 10000000}

결론:
keys 의 블로킹 연산으로 인해 ping 테스트 조차 1초 이상의 딜레이가 발생했습니다.
(두 쿼리 모두 8초 이상 소요된 이유는 app 단에서 JSON 직렬화 등 계산 시간이 포함되어 있습니다.)
같은 조건에서 scan 은 잘게 나누어 요청을 처리하기에 시간이 많이 걸리는 요청과 함께 있더라도 더 적은 지연 시간을 기대할 수 있습니다.
'''
