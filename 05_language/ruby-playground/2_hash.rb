# Ruby의 hash 의 경우 기본적으로 아래의 두 가지로 선언할 수 있다.
h = {}
h = Hash.new

# Hash의 키 타입에 심볼을 사용할 수 있다.
# 문자열과 심볼은 다르며, Rails 프레임워크에서는 심볼 키가 사실상의 표준이다.
h = Hash.new
h["a"] = 1
h[:a] = 1
h # {"a" => 1, a: 1}

# Hash.new() 에 매개변수를 입력하는 경우 '기본값'을 설정하게 되는데,
# 아래와 같은 경우 '[]'의 object_id를 기본값으로 가져가므로 복사가 아닌 참조가 일어난다.
h = Hash.new([])
h[:a] <<= 1
h[:b] <<= 2
h["1"] <<= 3
# {a: [1, 2, 3], b: [1, 2, 3], "1" => [1, 2, 3]}

# 올바른 패턴은 Array에서 다루었던 것처럼 블록 기반 생성자를 활용하는 방법이다.
h = Hash.new { |hash, key| hash[key] = [] }
h[:a] << 1
h[:b] << 2
# {a: [1], b: [2]}

# 없는 키에 접근 시 예외가 아닌 nil을 반환한다.
h = Hash.new
h[:a] = 3
h[:c] # nil
# '이 키는 반드시 있어야 한다.'는 의도가 필요하다면 fetch 메서드를 사용한다.
h.fetch(:a) # 3
# h.fetch(:b) # KeyError
h.fetch(:c, 0) # 0

# 삽입이나 수정은 대입을 통해 바로 가능하며, 삭제는 delete 메서드를 통해 이루어진다.
h[:a] = 4
h[:a] # 4
h.delete(:a)
h[:a] # nil

# Ruby Hash도 Python과 동일하게 삽입 순서를 유지한다.
h = { a: 1, b: 2, c: 3 }
h.each do |k, v|
  "#{k} => #{v}"
  # a => 1
  # b => 2
  # c => 3
end

# 핵심 메서드들은 다음과 같다.
h.keys # [:a, :b, :c]
h.values # [1, 2, 3]
h.key?(:a) # true
h.has_key?(:a) # true
h.value?(2) # true
h.empty? # false
h.size # 3

# 변환의 경우 Array처럼 !가 있으면 원본을 수정한다.
h.select { |k,v| v.even? } # {b: 2}
h # {a: 1, b: 2, c: 3}
h.select! { |k, v| v.even? } # {b: 2}
h # {b: 2}

# merge 의 경우, 기본적으로 h1에 h2의 모든 값을 덮어쓰기 하는 형태이고,
# 블록 연산을 통해 충돌 시 행동을 제어할 수 있다.
h1 = {a: 1, b: 2}
h2 = {a: 3, b: 5, c: 7}
h1.merge(h2) # {a: 3, b: 5, c: 7}
h1.merge(h2) { |key, old, new| old } # {a: 1, b: 2, c: 7}

# tally는 array의 메서드로, python의 counter와 같은 역할을 한다.
arr = %w[1 2 1 2 1 2 1 2 1 2 1 2 3].map(&:to_i)
arr.tally #{1 => 6, 2 => 6, 3 => 1}

# tally로 하기 복잡하거나, 불가능한 경우 each_with_object 를 통해 누적형 Hash를 구성할 수 있다.
counts = arr.each_with_object(Hash.new(0)) do |x, h|
  h[x] += 1
end
counts # {1 => 6, 2 => 6, 3 => 1}

# group_by를 통해 특정 기준에 따라 배열을 Hash로 변환할 수 있다.
# 아래의 예시는 첫글자를 기준으로 문자열을 묶은 것이다.
arr = %w[cat apple ant banana bear cnt]
arr.group_by { |x| x[0] } # {"c" => ["cat", "cnt"], "a" => ["apple", "ant"], "b" => ["banana", "bear"]}

# transform_keys / transform_values는 일괄적으로 key 또는 values에 변환을 적용한다.
# 여기도 ! 에 의해 원본의 변화를 결정할 수 있다.
params = { "user_id" => 1, "user_name" => "kim" }
params.transform_keys(&:to_sym) # {user_id: 1, user_name: "kim"}
params # {"user_id" => 1, "user_name" => "kim"}
params.transform_keys!(&:to_sym) # {user_id: 1, user_name: "kim"}
params # {user_id: 1, user_name: "kim"}
params.transform_values(&:to_s) #{user_id: "1", user_name: "kim"}
params # {user_id: 1, user_name: "kim"}
params.transform_values!(&:to_s) #{user_id: "1", user_name: "kim"}
params # {user_id: "1", user_name: "kim"}

# slice와 except는 Hash에서 특정 key만 필터링하기 위해 사용된다.
params = {user_id: 1, user_name: "kim", user_password: "secret"}
params.slice(:user_id, :user_name) # {user_id: 1, user_name: "kim"}
params.except(:user_password) # {user_id: 1, user_name: "kim"}

# Hash in Hash의 경우, dig를 통해 안전하게 접근 가능하다.
# dig의 경우 중간 키가 없어도 예외를 발생시키지 않는다.
h = { user: { profile: { age: 20 } } }
h[:user][:profile][:age] # 20
# h[:user][:community][:comment] # NoMethodError
h.dig(:user, :profile, :age) # 20
h.dig(:user, :community, :comment) # nil
