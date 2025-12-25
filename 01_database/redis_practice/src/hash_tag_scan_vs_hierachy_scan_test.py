from utils.tests import call


def test_hash_tag(struct_type: str):
    print("=== 데이터 정리 중 ===") 
    call(name="clear cluster data", method="delete", path="/cluster/clear", debug=False)
    call(name="clear cluster stats", method="post", path="/cluster/stats/reset", debug=False)
    print("=== 데이터 정리 완료 ===") 

    user_ids = [*range(100)]
    call(name = f"add_hash_with_{struct_type}", method="post", body=user_ids, path=f"/search/{struct_type}/add")
    call(name = f"search_with_{struct_type}", method="get", path=f"/search/{struct_type}?user_id=1")

    call(name="get_cluster_stats", method="get", path="/cluster/stats")

if __name__ == "__main__":
    test_hash_tag("hash-tag")
    test_hash_tag("hierachy")

'''
=== HASH TAG ===
add_hash_with_hash-tag: 200, 79.331s, body={'status': 'created', 'type': 'hash-tag', 'length': 10000000}
search_with_hash-tag: 200, 1.026s, body={'status': 'ok', 'type': 'hash-tag', 'count': 100000}
get_cluster_stats: 200, 0.003s, body={
    'redis1:6379': {
        'scan_calls': 0, 
        'usec_total': 0, 
        'usec_per_call': 0
    }, 
    'redis2:6379': {
        'scan_calls': 3599, 
        'usec_total': 720503, 
        'usec_per_call': 200.2
    }, 
    'redis3:6379': {
        'scan_calls': 0, 
        'usec_total': 0, 
        'usec_per_call': 0
    }, 'status': 'ok'}

=== HIERACHY ===
add_hash_with_hierachy: 200, 79.917s, body={'status': 'created', 'type': 'hierachy', 'length': 10000000}
search_with_hierachy: 200, 3.041s, body={'status': 'ok', 'type': 'hierachy', 'count': 100000}
get_cluster_stats: 200, 0.004s, body={
    'redis1:6379': {
        'scan_calls': 3330, 
        'usec_total': 754741, 
        'usec_per_call': 226.65
    }, 
    'redis2:6379': {
        'scan_calls': 3330, 
        'usec_total': 752414, 
        'usec_per_call': 225.95
    }, 
    'redis3:6379': {
        'scan_calls': 3337, 
        'usec_total': 758213, 
        'usec_per_call': 227.21
    }, 'status': 'ok'}
    
테스트 시나리오
- 100명의 유저가 각 10만개의 키를 가지는 상태에서 user_id=1의 모든 키를 SCAN

결과 요약
- hash-tag: 적재 ~80s, 조회 ~1s, `cmdstat_scan`이 특정 노드(redis2)에서만 ~3.6k 증가 → 단일 노드 스캔
- hierachy: 적재 ~80s, 조회 ~3s, 세 노드 모두 ~3.3k씩 증가 → 전체 노드 스캔

결론
- 해시태그로 슬롯을 고정하고 `target_nodes`를 지정하면 해당 슬롯 노드만 스캔해 왕복/처리 비용이 줄어든다.
- 해시태그 없이 계층형 키로 두면 모든 노드에서 SCAN이 돌며 노드 수만큼 비용이 늘어난다.
- 3노드 구성에서 단일 노드 스캔이 약 3배 빠르게 측정되었다.
'''
