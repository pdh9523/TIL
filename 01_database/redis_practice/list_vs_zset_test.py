import time
import threading
import random
import string
from typing import List, Any

import requests

BASE_URL = "http://127.0.0.1:8000"
TIMEOUT = 600

def get_random_users(size: int) -> List[str]:
    return [f"user_{''.join(random.choices(string.ascii_lowercase + string.digits, k=8))}" for _ in range(size)]

def call(name: str, method: str, path: str, body: Any | None = None, debug=True):
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
    return name, dt

if __name__ == "__main__":
    print("=== 데이터 정리 중 ===") 
    call("clear test data", "delete", "/clear", debug=False)
    print("=== 데이터 정리 완료 ===") 

    print("=== 테스트 데이터 생성 중 ===") 
    call("create_first_user", "post", "/queue/list/enqueue", ["user_first"], debug=False)
    for i in range(100):
        call("create_random_users", "post", "/queue/list/enqueue", get_random_users(size=100000), debug=False)
        if (i+1) % 10 == 0:
            print(f"=== 테스트 데이터 생성 중 === {i+1}/100") 
    call("create_last_uesr", "post", "/queue/list/enqueue", ["user_last"], debug=False)
    print("=== 테스트 데이터 생성 완료 ===")

    call("get_bottom100", "get", "/queue/list/bottom100", debug=True)
    call("get_top100", "get", "/queue/list/top100", debug=True)
    _, first_user_time = call("get_first_user", "get", "/queue/list/position?user_id=user_first", debug=True)
    _, last_user_time = call("get_last_user", "get", "/queue/list/position?user_id=user_last", debug=True)

    # 예상: 리스트 앞의 유저를 가지고 오는 시간이 리스트 뒤의 유저를 가지고 오는 시간보다 빠를 것이다.
    assert first_user_time < last_user_time

'''
get_bottom100: 200, 0.001s, body={'status': 'ok', 'total': 10000002, 'count': 100}
get_top100: 200, 0.002s, body={'status': 'ok', 'total': 10000002, 'count': 100}

get_first_user: 200, 0.001s, body={'status': 'ok', 'type': 'list', 'total': 10000002, 'position': 0}
get_last_user: 200, 0.111s, body={'status': 'ok', 'type': 'list', 'total': 10000002, 'position': 10000001}

1000만개의 테스트 세팅에서 시작했다.

- lrange를 통한 상위 100명, 하위 100명을 선택하는 것은 성능 차이가 거의 없었으나,
- 첫번째 유저를 가지고 오는 것과 마지막 유저를 가지고 오는 것은 큰 차이를 보였다.

Redis LIST는 내부적으로 quicklist(양방향 linked list + packed array)라 
인덱스를 직접 알면 head/tail 중 가까운 쪽에서 시작해 O(n)으로 이동한다.

`LRANGE`는 시작점이 tail에 가까우면 tail부터 바로 100개만 직렬화해서 끝에 있는 요소를 찾더라도 시간이 오래 걸리지 않고,  
`LPOS` 기본은 앞에서부터 비교하므로 끝 요소를 찾을 때 전체를 훑어 시간이 더 든다.
'''
