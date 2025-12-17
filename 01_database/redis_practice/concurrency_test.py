"""
간단한 동시 요청 테스트 스크립트.

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
    scan_result = run_pair("scan", "/scan", "/ping")
    time.sleep(0.5)
    keys_result = run_pair("keys", "/keys", "/ping")

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
'''
