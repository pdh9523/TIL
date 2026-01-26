# frozen_string_literal: true

# a와 b는 같은 선언이다.
# python에서 a = [], b = list() 와 같다고 생각하면 된다.
a = []
b = Array.new

# Array의 크기를 미리 선언할 수 있다.
# 이 경우, [nil, nil, nil, nil, nil] 으로 선언된다.
# nil은 go의 nil, 또는 python의 None과 동일하다.
c = Array.new(5)

# Array의 크기를 미리 선언한 경우, 기본값을 설정할 수 있다.
# 이 경우, 5개의 [0,0,0,0,0] 으로 선언된다.
d = Array.new(5, 0)

# 이렇게 선언하는 경우 새로운 Array 하나가 만들어지고, e의 5개의 인덱스 모두 같은 객체를 가진다.
# 그래서 -1번 인덱스에 값을 넣더라도, [[1],[1],[1],[1],[1]] 처럼 모든 인덱스에 들어가는 것처럼 보인다.
# python 처럼 음수 인덱스를 지원한다.
e = Array.new(5, []); e[-1] << 1

# 위의 경우 올바른 선언 형태는 아래와 같다.
f = Array.new(5) { Array.new }
f[-1] << 1 # [[], [], [], [], [1]]

# 인덱스의 특이사항으로,
# 범위를 벗어나는 경우 에러가 발생하는 것이 아니라, nil을 반환한다.
f[10] # nil

arr = [10,20,30,40,50,60,70,80,90]
# 5번 인덱스에서 시작해서, 3길이만큼 슬라이싱
arr[5, 3] # [60,70,80]

# 5번 인덱스에서 시작해서, 100길이만큼 슬라이싱
arr[5, 100] # [60,70,80,90]

# 100번 인덱스에서 시작해서, 2길이만큼 슬라이싱
arr[100, 2] # nil

# 5번 인덱스에서 시작해서, 6번 인덱스를 포함하지 않고 슬라이싱
arr[5...6] # [60]

# 5번 인덱스에서 시작해서, 6번 인덱스를 포함하고 슬라이싱
arr[5..6] # [60,70]

# 5번 인덱스에서 시작해서, 100번 인덱스까지 슬라이싱
arr[5..100] # [60,70,80,90]

# 슬라이스 대입이 가능하다.
arr[0,2] = [11,22] # [11,22,30,40,50,60,70,80,90]

# 슬라이스 대입을 하는데, 길이를 맞추지 않아도 괜찮다.
# 이 경우, 2부터 시작한 2길이만큼(2,3 인덱스)의 슬라이싱 부분을 [1,2,3,4,5]를 넣어서 변환한다.
arr[2,2] = [1,2,3,4,5]  # [11, 22, 1, 2, 3, 4, 5, 50, 60, 70, 80, 90]

# 삽입은 두 가지 형태를 가진다.
arr << 100
arr.push(110)

# 앞에 추가는 unshift를 통해 할 수 있다. (시간복잡도는 O(N)이다.)
arr.unshift(0) # [0, 11, 22, 1, 2, 3, 4, 5, 50, 60, 70, 80, 90, 100, 110]

# 중간 삽입은 insert를 통해 가능하다.
arr.insert(0, 999) # [999, 0, 11, 22, 1, 2, 3, 4, 5, 50, 60, 70, 80, 90, 100, 110]
# 여러 개의 값도 insert할 수 있다.
arr.insert(3, -1,-2,-3,-4,-5) # [999, 0, 11, -1, -2, -3, -4, -5, 22, 1, 2, 3, 4, 5, 50, 60, 70, 80, 90, 100, 110]

arr = [1,2,3,4,5]

# 원소의 제거는 pop, shift를 통해 할 수 있다.
a = arr.pop # [1,2,3,4], a = 5
b = arr.shift # [2,3,4] b = 1
c = arr.delete(3) # [2,4], c = 3
d = arr.delete(100) # [2,4], d = nil
e = arr.delete_at(0) # [4], e = 2

# slice를 사용해서 Array의 일부를 가져올 수 있다.
arr = [1,2,3,4,5]

sliced = arr.slice(1,2)  # sliced: [2,3], arr: [1,2,3,4,5]

# slice!를 사용하는 경우, 원본이 변경된다.
sliced_with_bang = arr.slice!(1, 2)  # sliced_with_bang: [2,3], arr: [1,4,5]

arr = [1,2,3,4,5]

selected = arr.select {
  |x| x.even?
} # selected: [2,4], arr: [1,2,3,4,5]

selected_with_bang = arr.select! {
  |x| x.even?
} # selected_with_bang: [2,4], arr: [2,4] // 여기서 selected_with_bang은 arr과 같은 객체(object_id)를 가진다.

# select!는 변경이 없으면 nil을 반환한다.
# 이로 인해 사이드 이펙트가 발생할 수 있다.
selected_not_changed = arr.select!(&:even?) # select_not_changed: nil, arr: [2,4]

arr.include?(2) # true

arr = [1,3,2,4,5]
sorted_arr = arr.sort # sorted_arr: [1,2,3,4,5], arr: [1,3,2,4,5]
arr.sort! # arr: [1,2,3,4,5]
sorted_arr = arr.sort_by { |x| -x } # sorted_arr: [5,4,3,2,1]

arr = [1,2,3,4,nil]
# size와 length가 모두 있는 이유는, size가 Array외에 다른 Ruby의 컬렉션 전반에 쓰이는 범용 인터페이스이기 때문이다.
# length는 '길이' 라는 의미를 직관적으로 표현하기 위함이고, 의미적으로는 size의 alias로 동작한다.
arr.size # 5
arr.length # 5
arr.empty? # false
