# Struct 는 필드가 정해진 가벼운 객체다.
User = Struct.new(:name, :age)

u = User.new("admin", 1)
u.name # admin
u.age  # 1

# 이는 의미적으로 아래의 class 선언과 같다.
class User
  attr_accessor :name, :age

  def initialize(name, age)
    @name = name
    @age = age
  end
end

# Struct는 ==, to_h, members를 제공한다.
# 다만, == 는 object_id 비교가 아니라, 필드 값 기준으로 비교한다.
# 가볍고 빠르며, 내부는 Array 기반으로 이루어져 있다.

# 블록으로 메서드를 추가할 수 있다.
Point = Struct.new(:x, :y) do
  def dist
    Math.sqrt(x**2 + y**2)
  end
end
# Struct는 일반적으로 DTO, Req/Res, 등 간단한 값 객체를 나타낼 때 사용한다.


# Data는 Ruby 3.2 + 버전 이후의 문법으로, Struct의 설계상 문제를 해결한 방식이다.
# Struct는 가변성으로 인해 모델링을 위해서는 맞지 않았었는데,
# 이를 위해 Data 를 추가해 불변인 객체를 생성하도록 했다.
User = Data.define(:name, :age)
u = User.new("admin", 1)
# writer 메서드가 없기 떄문에 새로운 값을 할당할 수 없다.
# u.name = "test" # NoMethodError
# 대신, 만들어진 Data 객체를 기반으로 새로운 값을 만들어 낼 수 있다.

u2 = u.with(name: "superuser")
# 이를 통해 Command / Query 모델, 도메인 값 객체를 안전하게 사용할 수 있고,
# 스레드 안전 등 사이드 이펙트를 제거할 수 있다.

# OpenStruct는 런타임에 필드가 바뀌는 객체다.
require 'ostruct'

u = OpenStruct.new
u.name = "kim"
u.age = 20

# 내부적으로 Hash를 사용하며, 정의 되지 않은 메서드는 method_missing 으로 동적 처리된다.
# 필드가 완전히 동적으로 이루어져있기 때문에, 주의 깊게 사용해야 한다.

u.mane = "lee" # 같이 오타가 발생하더라도
u.name # kim  // 디버깅이 어려워 조용히 망가질 위험이 있다.

# 또한 Struct / Data 대비 현저히 느리고, 메모리 사용량이 크다.
# json 파싱 후 임시 래핑이나, 콘솔 및 스크립트에서 사용할 수 있다.