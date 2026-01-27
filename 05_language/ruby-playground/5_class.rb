# 기본적인 클래스 정의
class User

end

# User 클래스 또한 Class 라는 객체에 속한다.
User.class # Class

# Ruby는 생성자를 오버라이드하지 않는다.
# new는 항상 Class#new이고, 우리가 제어할 수 있는건 initialize 뿐이다.
# new 호출 시 객체에 메모리를 할당하고, initialize를 호출한다. 이 때, initialize의 반환값은 무시된다.

class User
  def initialize(name)
    @name = name
    puts "hello, #{name}!"
  end
end

User.new("admin") # hello, admin!

class User
  def initialize(name)
    @name = name
  end

  def set_id(id)
    @id = id
  end
end

# 인스턴스 변수는 선언 키워드, 접근 제어자가 없이 메서드 내부에서 처음 등장하는 순간 생성된다.
# 위의 User에서, initialize 를 통해 @name이 선언되는 순간부터 생성되는 것이다.
user = User.new("admin")
user.instance_variables # [:@name]
user.set_id(1)
user.instance_variables # [:@name, :@id]

# 접근자 매크로가 존재한다.
# attr_reader 는 오른쪽 항의 getter 메서드를 만들어준다.
# def name()
#   @name
# end
# 를 선언한 것과 같다.
# attr_writer 는 오른쪽 항의 setter 메서드를 만들어준다.
# def id=(id)
#   @id = id
# end
# 를 선언한 것과 같다.
# 대신, attr_writer는 좀 더 특별한데,
# user.id = 1, user.id += 1 등으로 다양하게 호출할 수 있다.
# attr_accessor는 getter + setter 를 동시에 선언하는 것이고,
# 의미적으로는 '이 객체의 해당 속성은 아무나 마음대로 바꿔도 된다.'라고 말하는 것과 같다.
class User
  attr_reader :name
  attr_writer :id
  attr_accessor :age, :data

  def initialize(name = "user")
    @name = name
  end
end

user = User.new("admin")
user.age = 1
user.age += 1
# user.data += 1 # 아직 user의 id 인스턴스 선언 전에 할당 연산자를 사용해 오류가 발생한다.
