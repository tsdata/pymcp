"""
pymcp 라이브러리 사용 예제
"""

from pymcp import PyMCP, convert_function, mcpwrap


# 예제 1: 기본 함수를 MCP 서버로 변환
def hello(name: str) -> str:
    """인사말을 생성하는 함수"""
    return f"안녕하세요, {name}님!"

# 함수를 MCP 서버로 변환
hello_server = convert_function(hello)

# 다음 코드로 서버 실행 가능:
# hello_server.run()


# 예제 2: 데코레이터를 사용한 방법
@mcpwrap(name="덧셈_도구", description="두 숫자를 더하는 도구")
def add(a: int, b: int) -> int:
    """두 숫자를 더하는 함수"""
    return a + b

# 다음 코드로 서버 실행 가능:
# add.serve_mcp()


# 예제 3: 여러 함수를 하나의 MCP 서버로 결합
def multiply(a: int, b: int) -> int:
    """두 숫자를 곱하는 함수"""
    return a * b

def divide(a: int, b: int) -> float:
    """두 숫자를 나누는 함수"""
    if b == 0:
        return "0으로 나눌 수 없습니다."
    return a / b

# 여러 함수를 하나의 서버로 결합
calculator = PyMCP(name="계산기 서버", instructions="간단한 계산 기능을 제공하는 서버입니다.")
calculator.add_function(add)
calculator.add_function(multiply)
calculator.add_function(divide)

# 다음 코드로 서버 실행 가능:
# calculator.run()


# 예제 4: 데코레이터를 사용한 여러 함수 결합
math_server = PyMCP(name="수학 서버", instructions="수학 함수를 제공하는 서버입니다.")

@math_server.wrap_function()
def square(x: int) -> int:
    """숫자의 제곱을 계산"""
    return x * x

@math_server.wrap_function()
def factorial(n: int) -> int:
    """팩토리얼 계산"""
    if n <= 1:
        return 1
    return n * factorial(n - 1)

# 다음 코드로 서버 실행 가능:
# math_server.run()


if __name__ == "__main__":
    # 실행할 서버를 선택하고 주석 해제
    # hello_server.run()
    # add.serve_mcp()
    calculator.run()
    # math_server.run()
    
    # 안내 메시지
    print("어떤 서버를 실행할지 예제 파일에서 주석을 해제하세요.")
    print("예: 'hello_server.run()' 라인의 주석을 해제하고 다시 실행하세요.") 