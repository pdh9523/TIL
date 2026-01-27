# 여타 언어들과 다르게, Ruby의 String은 mutable 하다.
# 아래와 같이 주석으로
#'# frozen_string_literal: true'
# 와 같이 작성하면,
# 리터럴 문자열을 freeze 설정할 수 있다.
# 이 경우, 문자열 변수를 수정하는 경우, FrozenError를 반환한다.

# Java의 StringBuilder와 유사하게 동작한다.
s = "hello"
s << ", world" # "hello, world"

# "", '' 가 구분된다.
# "" 의 경우 인터폴레이션, 이스케이프 구문이 가능하지만
# '' 의 경우 리터럴 그대로 표시된다.

name = "Ruby"
"hello #{name}" # "hello Ruby"
'hello #{name}' # "hello \#{name}" // Expression substitution in single-quoted string

# string은 Array의 %w 처럼, %q 문법을 사용할 수 있다.
%Q(hello #{name}) # "hello Ruby"
%q(hello #{name}) # "hello \#{name}" // Expression substitution in single-quoted string

# heredoc은 여러 줄 문자열을 정의할 때 사용하며,
# <<~ 는 모든 줄에 공통으로 들어간 최소 들여쓰기를 제거한다.
# "SELECT *\nFROM users\nWHERE age > 20\n"
<<~SQL
    SELECT *
    FROM users
    WHERE age > 20
SQL
# <<- 는 들여쓰기를 제거하지 않아 Ruby 코드 들여쓰기를 하면 문자열도 같이 밀린다.
# "    SELECT *\n    FROM users\n    WHERE age > 20\n"
<<-SQL
    SELECT *
    FROM users
    WHERE age > 20
SQL

# 인덱싱, 슬라이싱은 Array와 유사하게 동작한다.
s = "abcdefg"
s[0] # a
s[-1] # g
s[100] # nil
s[1..3] # bcd
s[1...3] # bc
s[3, 2] # de

# case 변환이 가능하다.
h = "hello world"
h.downcase # hello world
h.upcase # HELLO WORLD
h.capitalize #Hello world

# strip을 통해 공백을 정리할 수 있다.
str = "    hi      "
str.strip # "hi"
str.lstrip # "hi      "
str.rstrip # "    hi"


# split, join을 통해 분리 및 결합할 수 있다.
# split 의 기본 값은 " " 이다. 공백을 기준으로 분리한다.
"a b c".split # ["a", "b" ,"c"]
%w[a b c].join(" ") # a b c

# 탐색 및 검사
s = "hello world"
s.include?("world") # true
s.start_with?("he") # true
s.end_with?("ll") # false

# 빈 문자열 구분
# Rails 에서는 기본적으로 blank / present 를 통해 문자열을 검증한다.
"".empty? # true
" ".empty? # false

# 치환
"hello world".sub("l", "x") # hexlo world"
"hello world".gsub("l", "x") # hexxo worxd"
"abc123".gsub(/\d+/, "") # "abc"
"hello world".tr("aeiou", "x") # "hxllx wxrld"
