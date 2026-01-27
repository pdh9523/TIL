# 이렇게 uniq 메서드를 통해 표현하는 것은 결과가 집합과 같지만,
# 구조 자체가 집합이라는 보장은 없다.
arr = [1, 2, 2, 3]
arr.uniq

# Set은 python과 마찬가지로 내부적으로 Hash를 감싸고 있기 때문에,
# 포함 여부, 삽입, 삭제에 O(1) 의 시간복잡도를 가지며, 순서를 가지지 않는다.
s = Set.new

s.add(1) # Set[1]
s << 2   # Set[1,2]
s.add(2) # Set[1,2]
s = Set.new([1,2,2,3]) # Set[1, 2, 3]

# 포함 여부는 include? 메서드를 통해,
s.include?(3) # true
s.include?(4) # false

# 삭제는 delete 메서드를 통해 가능하다. 이 경우, 존재하지 않는 요소를 삭제해도 변화가 없다.
s.delete(2) # Set[1, 3]
s.delete(4) # Set[1, 3]

# Array에서 to_set 메서드를 통해 Set으로 변환할 수 있다.
arr = [1, 2, 2, 3]
arr.to_set # Set[1,2,3]

# 그리고, Set에서 to_a 메서드를 통해 Array로 변환할 수 있다.
s.to_a # [1, 3]

# 합집합, 교집합, 차집합, 대칭 차집합 등의 연산을 지원한다.
a = Set.new([1, 2, 3])
b = Set.new([3, 5, 6])
a | b # Set[1, 2, 3, 5, 6]
a & b # Set[3]
a - b # Set[1, 2]
a ^ b # Set[1, 2, 4, 5]