# 코틀린 투어

[Welcome to our tour of Kotlin! | Kotlin Documentation](https://kotlinlang.org/docs/kotlin-tour-welcome.html)
를 참조합니다. 

# Kotlin 기본 구조

```kotlin
fun main() {
    println("Hello world!")
} // Hello world!
```
`fun`: 함수 선언에 사용된다.  

`main()`: **main** 이름을 가진 함수는 해당 프로그램의 시작점을 의미한다.  

`{}`: 함수의 구현부는 중괄호 내에 정의된다.

`println()`: 해당 함수는 매개변수를 표준 출력으로 내보내는 함수다.

해당 구조를 통해 기본적인 실행 가능한 프로그램을 작성할 수 있다.

**`Main.kt` 파일명을 강제하는 것은 아니다.**

---
## 불변 변수와 가변 변수

```kotlin
fun main() {
    val popcorn = 5
    popcorn = 8 // IMPOSSIBLE

    var customers = 10
    customers = 8 // POSSIBLE
}

val tickets = 10
```

읽기 전용의, 불변 변수를 선언하려면 `val`을,  
수정 가능한, 가변 변수를 선언하려면 `var`을 통해 선언한다. 

`customers`의 경우 `var` 키워드로 선언 후,  
바로 아래줄에서 재할당되었다.  

**Kotlin**에서는 기본적으로 `val` 키워드로 선언하고,  
재할당이 꼭 필요한 경우에만 `var`을 사용하는 것을 권장한다. 

해당 변수들은 `main()`함수 바깥에서도 선언이 가능하다.

---
## 문자열 템플릿

```kotlin
fun main() {
    val customers = 10
    
    println("Customers: $customers")
    println("Customers+1: ${customers+1}")
}
```
문자열 템플릿 기능은 표준 출력을 할 때 용이하다.

변수 앞에 `$`를 앞에 붙이는 것으로 출력할 문자열 내에 변수를 넣어 함께 출력할 수 있다.

---

# 타입

**Kotlin**의 모든 변수와 자료구조는 '타입'을 가지고 있다.  
타입은 컴파일러에게 해당 변수나 자료구조가 어떤 것이 허용되는지.  
즉, 어떤 메서드와 속성을 가지고 있는지 알려준다. 

## 타입 추론

`## 불변 변수와 가변 변수`에서 선언했던 `customers`의 경우 `Int` 타입을 가지고 있다.  

**Kotlin**은 기본적으로 타입 추론 언어이기 때문에,  
변수를 선언할 때 항상 타입을 명시하지 않아도 된다.

```kotlin
var customers = 10
// var customers: Int = 10 와 동일하다.

customers = 8

customers = customers + 3 // 11 
customers += 7 // 18
customers -= 3 // 15
customers *= 2 // 30
customers /= 3 // 10
customers %= 3 // 1
```

## 기본 타입

**Kotlin**은 아래와 같은 기본 타입을 가지고 있다. 

| 카테고리      | 타입                                 | 예시                                                            |
|-----------|------------------------------------|---------------------------------------------------------------|
| 정수형       | `Byte`, `Short`, `Int`, `Long`     | `val year: Int = 2026`                                        |
| 부호 없는 정수형 | `UByte`, `UShort`, `UInt`, `ULong` | `val score: UInt = 100u`                                      |
| 실수형       | `Float`, `Double`                  | `val currentTemp: Float = 24.5f`, `val price: Double = 14.99` |
| 불리언       | `Boolean`                          | `val isTrue: Boolean = true`                                  |
| 문자        | `Char`                             | `val separator: Char = ':'`                                   |
| 문자열       | `String`                           | `val message: String = "Hello, world!"`                       |

### 정수형
`Byte` : 8  비트 크기의 타입으로, -2<sup>7</sup> ~ 2<sup>7</sup>-1 까지의 정수를 표현할 수 있다.  
`Short`: 16 비트 크기의 타입으로, -2<sup>15</sup> ~ 2<sup>15</sup>-1 까지의 정수를 표현할 수 있다.  
`Int`  : 32 비트 크기의 타입으로, -2<sup>31</sup> ~ 2<sup>31</sup>-1 까지의 정수를 표현할 수 있다. 정수형의 기본 추론 타입이다.  
`Long` : 64 비트 크기의 타입으로, -2<sup>63</sup> ~ 2<sup>63</sup>-1 까지의 정수를 표현할 수 있다.

### 부호 없는 정수형
`UByte` : 8  비트 크기의 타입으로, 0 ~ 2<sup>8</sup>-1 까지의 정수를 표현할 수 있다.  
`UShort`: 16 비트 크기의 타입으로, 0 ~ 2<sup>16</sup>-1 까지의 정수를 표현할 수 있다.  
`UInt`  : 32 비트 크기의 타입으로, 0 ~ 2<sup>32</sup>-1 까지의 정수를 표현할 수 있다.  
`ULong` : 64 비트 크기의 타입으로, 0 ~2<sup>64</sup>-1 까지의 정수를 표현할 수 있다.

### 실수형
`Float` : 32 비트 크기의 타입으로, 유효 24비트/지수 8비트의 실수 타입이다.  
`Double`: 64 비트 크기의 타입으로, 유효 53비트/지수 11비트의 실수 타입이다. 실수형의 기본 추론 타입이다.

### 불리언

불리언 타입은 JVM 환경에서 일반적으로 1바이트 크기로 표현된다.

`Boolean` : `true`, `false` 두 가지 값만 가질 수 있다.   
`Boolean?` : `Boolean` 타입에 `null`이 허용된 nullable 타입이다.

### 문자

문자형 타입은 JVM 환경에서 일반적으로 16비트 유니코드 문자로 표현된다. 

`Char` : 하나의 유니코드 문자를 저장하는 타입이다. 작은따옴표`' '`로 감싸서 표현한다. 

### 문자열

문자열 타입은 여러 문자를 순서대로 저장하는 타입이다. JVM 환경에서는 내부적으로 문자 배열을 기반으로 구현된다.

`String` : 일렬의 문자를 저장하는 타입이다. 큰따옴표 `" "`로 감싸서 표현한다.