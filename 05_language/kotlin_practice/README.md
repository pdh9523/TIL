# 코틀린 투어

[Welcome to our tour of Kotlin! | Kotlin Documentation](https://kotlinlang.org/docs/kotlin-tour-welcome.html)
를 참조합니다. 

## Kotlin 기본 구조

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

`customer`의 경우 `var` 키워드로 선언 후,  
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

