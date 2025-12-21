import random
import string
import threading
import time
from typing import Any, List

import requests

BASE_URL = "http://127.0.0.1:8000"
TIMEOUT = 600

def get_random_users(size: int) -> List[str]:
    return [f"user_{''.join(random.choices(string.ascii_lowercase + string.digits, k=10))}" for _ in range(size)]

def call(
        name: str, 
        method: str, 
        path: str, 
        start_evt: threading.Thread | None = None,
        body: Any | None = None, 
        debug: bool = True
    ) -> float:
    if start_evt is not None:
        start_evt.wait()
    
    t0 = time.perf_counter()

    if method == "get":
        resp = requests.get(f"{BASE_URL}{path}", timeout=TIMEOUT)
    elif method == "post":
        resp = requests.post(f"{BASE_URL}{path}", json=body, timeout=TIMEOUT)
    elif method == "delete":
        resp  = requests.delete(f"{BASE_URL}{path}", timeout=TIMEOUT)
    
    dt = time.perf_counter() - t0
    if debug:
        print(f"{name}: {resp.status_code}, {dt:.3f}s, body={resp.json()}")
    return dt