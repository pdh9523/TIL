from datetime import datetime

from src.utils.tests import call, get_random_users


target_user = [
    ("user_target", datetime(2025, 12, 18, 12, 0, 0).isoformat())
]

def test_timescale(struct_type: str):
    print("=== 데이터 정리 중 ===") 
    call("clear test data", "delete", "/clear", debug=False)
    print("=== 데이터 정리 완료 ===") 

    users = get_random_users(1000000)
    for i in range(24):
        if (i+1) % 3 == 0:
            print(f"=== {struct_type} 테스트 데이터 생성 중 === {i+1}/24")
        users_with_time = [(user, datetime(2025, 1, 1, i, 0, 0).isoformat()) for user in users]
        call(name="create_sample_data", method="post", path=f"/time-scale/{struct_type}", body=users_with_time, debug=False)

    call(name="create_target_data", method="post", path=f"/time-scale/{struct_type}", body=target_user, debug=False)
    print(f"=== {struct_type} 테스트 데이터 생성 완료 ===")
    call(name="get_key_count", method="get", path=f"/count?pattern=test:*")
    return call(name="get_user_data", method="get", path=f"/time-scale/{struct_type}?user_id=user_target")


if __name__ == "__main__":
    test_timescale("hset")
    test_timescale("string")

'''
=== HSET ===
get_key_count: 200, 2.343s, body={'status': 'ok', 'count': 1000001}
get_user_data: 200, 0.569s, body={'status': 'ok', 'user_id': 'user_target'}

=== STRING ===
get_key_count: 200, 69.797s, body={'status': 'ok', 'count': 24000001}
get_user_data: 200, 10.670s, body={'status': 'ok', 'user_id': 'user_target'}

테스트 시나리오
- 하루(24시간) 동안 100만 명의 기록을 시간별로 저장한 뒤, user_target 데이터를 추가하고 조회한다.

결론
- HSET은 날짜 단위 키 아래 시간별 필드로 묶여 키 수가 적고 조회도 빠르다.
- STRING은 시간마다 키가 분리돼 키 수가 약 24배 증가하며 조회가 상대적으로 느려진다.
- 패턴이 반복되는 경우, 또는 특정 군집으로 묶을 수 있는 경우 HSET을 활용하는 것이 성능적으로 우수하다.
  단, 개별 필드가 많아지는 경우나, TTL을 필드 단위로 줄 수 없다는 점은 함께 고려해야한다.
'''
