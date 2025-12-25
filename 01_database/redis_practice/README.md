# 레디스 자료구조

Redis 는 단순한 Key-Value 스토리지에서 그치지 않고,  
제한된 자료구조들을 통해 성능과 예측 가능성을 확보한 시스템이다.  

실제 테스트를 기반으로,  
자주 마주치는 선택 지점들을 중심으로, 자료구조의 특성과 트레이드오프를 정리하려고 한다.

## 레디스 자료구조의 종류

Redis의 대표적인 자료구조는 다음과 같다.

- String
- List
- Set
- Sorted Set (ZSET)
- Hash (HSET)
- 그 외 Bitmap, HyperLogLog, Stream, Pub/Sub 등

하지만 실제 프로젝트나 서비스를 구상하면서  
무슨 자료구조가 있냐 보다는 비슷한 선택지 중 '어떤 것이 가장 정답에 가까운지' 이다.

이 글에서는 그 중에서도 실제로 많이 헷갈리는 네 가지를 다루어보려고한다.

---

### KEYS vs SCAN

#### KEYS
```redis-cli
KEYS user:*
```
- 모든 키를 한 번에 탐색
- 시간 복잡도는 $O(N)$ ($N$은 전체 키 개수)
- 실행 동안 Redis 는 블로킹

운영 환경에서 사용하는 것을 공식 문서에서도 권장하지 않고 있다.  

`keys_vs_scan_test.py` 에서처럼  
KEYS연산의 블로킹 때문에  
다른 가벼운 연산들의 지연이 누적되는 것을 확인할 수 있었다. 

---

#### SCAN
```redis-cli
SCAN 0 MATCH user:* COUNT 1000
```

- cursor 기반 점진적 탐색
- 시간 복잡도는 $O(N)$ 으로 동일
- 실행이 파편화되어, 논 블로킹처럼 동작

단, 여기서 COUNT는 단순 힌트에 불과하기 때문에,  
정확한 개수를 보장하지는 않는다.

그리고, 실행의 파편화로 인해 반복 호출이 필요하다.

---
### LIST vs ZSET 

#### List
- 내부 구조: quicklist
- push/pop: $O(1)$
- index 접근: $O(N)$

적합한 경우:
- 단순 FIFO/LIFO
- 최근 로그
- 작업 큐

순서만 중요하고, 기준이 단순할 때 사용하기 좋다.  
deque처럼 사용할 때 가장 효율이 좋다.

---

#### ZSET
```redis-cli
ZADD ranking 100 user1
ZRANGE ranking 0 9 WITHSCORES
```

- 내부 구조: skiplist + hash
- score 기반 정렬
- 삽입/삭제: $O(log N)$

적합한 경우:
- 랭킹
- 시간 기반 정렬
- 우선순위 큐

순서가 필요한 경우에 가장 적합하다.  
이를 통해 리더보드나, 대기열 같은 시스템을 만들기 쉽다.

---

### STRING vs HSET

#### STRING
```redis-cli
SET user:1:name "test"
```
- 가장 단순하고 일반적으로 사용
- GET/SET: $O(1)$

단점:
- 필드가 늘어날수록 KEY 폭증
- 네임스페이스 관리 어려움 

---

#### HSET
```redis-cli
HSET user:1 name "test" age 100
```
- 여러 필드를 하나의 key에 묶음
- 소규모 hash는 ziplist로 구현되어 매우 효율적임

적합한 경우:
- 객체 단위 캐시
- user profile
- 설정 값 묶음

`string_vs_hset_test.py`에서  
키가 폭증하는 상황을 가정했는데,  

수십 개 필드까지는 hash가 메모리/성능 모두 유리하다.  
field 단위 접근도 $O(1)$ 이다.

하나로 군집화 할 수 있는 경우는 HSET을 사용하는 것이 효율적이다.  
- 유저 정보 캐싱 (json 직렬화 비용 제거)
- 시간 단위 카운트 (하루를 키로, 내부 필드를 00-23 으로 설정)

---
### Hierachy vs Hash Tag (in Cluster)
Redis Cluster는 여러 개의 레디스 노드를 하나의 논리적 Redis 처럼 동작하게 만드는  
샤딩 기반 분산 구조다.  

모든 key는 내부적으로 16384 개의 hash slot 중 하나에 매핑되며,  
각 slot은 특정 Redis 노드에 할당된다.

즉, Redis Cluster의 실제 데이터 흐름은 다음과 같다.
```text
key -> hash(key) -> hash slot -> node
```

여기서 제약이 하나 발생하는데,  
서로 다른 hash slot에 속한 key들에 대해서는,  
원자적 연산이나 멀티 키 연산이 불가능하다.

위의 제약때문에, key 네이밍 전략 또한 활용해야한다.

---
#### Hierachy

```redis-cli
user:1:profile
user:1:score
```
일반적으로 사용하는 자연스러운 네이밍이지만,  
Redis Cluster의 slot은 전체 key 기준이다.

그래서 같은 user라도 서로 다른 노드에 저장되어 있을 수 있다.

이 경우, 
- `MGET`, `MULTI`, `PIPELINE` 같은 멀티키 연산 불가
- 논리적으로 하나의 개념을 다루는 데도 네트워크 hop 증가
- 트랜잭션 보장 불가

논리적인 묶음으로 보이지만, 레디스는 단순한 문자열로 판단할 뿐이고,  
물리적으로 분산되어 위와 같은 제약이 발생한다.

---

#### Hash Tag
```redis-cli
user:{1}:profile
user:{1}:score
```

`{}`안의 값으로 slot을 계산해 결정하고,  
같은 hash tag는 같은 노드에 들어가는 것이 보장된다.

장점:
- 멀티 키 연산 가능
- 트랜잭션/파이프라인 유지

단점:
- 특정 노드 쏠림 가능성
- 설계 실수 시 핫스팟 발생

---
