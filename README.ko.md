# PyMCP

> [English](README.md) | [한국어](#korean)

파이썬 함수를 MCP(Model Context Protocol) 서버로 변환하는 도구입니다.

**Copyright (c) 2025 Pandas-Studio (ontofinance@gmail.com)**

---

<a name="korean"></a>
## 한국어 문서

- [소개](#소개)
- [설치](#설치)
- [빠른 시작](#빠른-시작)
- [사용법](#사용법)
  - [기본 함수 변환](#기본-함수-변환)
  - [데코레이터 사용](#데코레이터-사용)
  - [여러 함수 결합](#여러-함수-결합)
  - [여러 데코레이터 사용](#여러-데코레이터-사용)
- [Cursor 에디터 연동](#cursor-에디터-연동)
  - [명령줄 설정](#명령줄-설정)
  - [파이썬 코드 설정](#파이썬-코드-설정)
  - [자동 설정](#자동-설정)
- [함수 타입과 반환값](#함수-타입과-반환값)
- [고급 사용법](#고급-사용법)
- [예제](#예제)
  - [기본 예제](#기본-예제)
  - [LangChain 연동](#langchain-연동)
  - [LangGraph 연동](#langgraph-연동)
- [라이선스](#라이선스)
- [기여하기](#기여하기)

### 소개

PyMCP는 일반 파이썬 함수를 MCP 서버로 변환하는 과정을 간소화합니다. 이를 통해 Cursor 에디터와 같은 AI 모델이 파이썬 함수를 직접 호출할 수 있게 됩니다. MCP 프로토콜에 대한 깊은 이해가 필요하지 않습니다.

### 설치

```bash
pip install pymcp
```

### 빠른 시작

1. 일반 파이썬 함수를 정의합니다:

```python
def add(a: int, b: int) -> int:
    """두 숫자를 더합니다"""
    return a + b
```

2. 한 줄로 MCP 서버로 변환합니다:

```python
from pymcp import convert_function
server = convert_function(add)
server.run()
```

3. 이게 전부입니다! 이제 함수가 MCP 도구로 사용 가능합니다.

### 사용법

#### 기본 함수 변환

```python
from pymcp import convert_function

def hello(name: str) -> str:
    """인사말 생성"""
    return f"안녕하세요, {name}님!"

# 함수를 MCP 서버로 변환
hello_server = convert_function(hello)

# 서버 실행
hello_server.run()
```

#### 데코레이터 사용

```python
from pymcp import mcpwrap

@mcpwrap(name="덧셈_도구", description="두 숫자를 더하는 도구")
def add(a: int, b: int) -> int:
    """두 숫자를 더함"""
    return a + b

# 서버 실행
add.serve_mcp()
```

#### 여러 함수 결합

```python
from pymcp import PyMCP

def multiply(a: int, b: int) -> int:
    """두 숫자를 곱함"""
    return a * b

def divide(a: int, b: int) -> float:
    """두 숫자를 나눔"""
    if b == 0:
        return "0으로 나눌 수 없습니다"
    return a / b

# 여러 함수를 하나의 서버로 결합
calculator = PyMCP(name="계산기 서버", instructions="계산 기능을 제공하는 서버")
calculator.add_function(multiply)
calculator.add_function(divide)

# 서버 실행
calculator.run()
```

#### 여러 데코레이터 사용

```python
from pymcp import PyMCP

math_server = PyMCP(name="수학 서버", instructions="수학 함수를 제공하는 서버")

@math_server.wrap_function()
def square(x: int) -> int:
    """숫자의 제곱 계산"""
    return x * x

@math_server.wrap_function()
def factorial(n: int) -> int:
    """팩토리얼 계산"""
    if n <= 1:
        return 1
    return n * factorial(n - 1)

# 서버 실행
math_server.run()
```

### Cursor 에디터 연동

PyMCP는 Cursor 에디터와 쉽게 연동할 수 있습니다.

#### 명령줄 설정

```bash
# MCP 서버 추가
pymcp cursor add-server calculator examples/examples.py

# 가상 환경의 파이썬 인터프리터 명시적 지정
pymcp cursor add-server calculator examples/examples.py --python /path/to/venv/bin/python

# 서버 목록 확인
pymcp cursor list-servers

# 서버 제거
pymcp cursor remove-server calculator

# 설정 파일 경로 표시
pymcp cursor config-path
```

#### 파이썬 코드 설정

```python
from pymcp import add_pymcp_server, list_pymcp_servers, remove_pymcp_server

# MCP 서버 추가
add_pymcp_server(
    "calculator",
    "/path/to/examples/examples.py",
    python_path="/path/to/venv/bin/python"
)

# 서버 목록 확인
servers = list_pymcp_servers()

# 서버 제거
remove_pymcp_server("calculator")
```

#### 자동 설정

패키지에는 계산기 서버를 자동으로 등록하는 setup_cursor.py 스크립트가 포함되어 있습니다:

```bash
# 가상 환경 활성화
source .venv/bin/activate

# 설정 스크립트 실행
python setup_cursor.py
```

이 스크립트는 다음 작업을 수행합니다:
1. 가상 환경 감지
2. 예제 계산기 서버를 Cursor에 등록
3. 필요한 모든 경로와 환경 변수 설정

스크립트 실행 후, Cursor 에디터를 재시작하고 AI 패널에서 'pymcp-calculator' 서버를 선택하여 사용하세요!

### 함수 타입과 반환값

PyMCP는 다양한 함수 타입과 반환값을 지원합니다:

- **기본 타입**: 정수, 실수, 문자열, 불리언 값이 자동으로 변환됩니다
- **리스트와 딕셔너리**: 복잡한 데이터 구조는 텍스트로 변환됩니다
- **MCP 특정 타입**: TextContent, ImageContent, EmbeddedResource가 지원됩니다
- **오류 처리**: 예외와 오류 메시지가 적절히 처리됩니다

예시:

```python
# 문자열 반환
def greet(name: str) -> str:
    return f"안녕하세요, {name}님!"

# 이미지 반환 (PIL 필요)
def generate_image() -> Image:
    from PIL import Image
    image = Image.new('RGB', (100, 100), color='red')
    return image

# 복잡한 반환 (텍스트로 변환)
def get_data() -> dict:
    return {"name": "홍길동", "age": 30}
```

### 고급 사용법

#### 커스텀 서버 설정

```python
from pymcp import PyMCP

# 커스텀 설정으로 서버 구성
server = PyMCP(
    name="커스텀 서버",
    instructions="서버에 대한 상세 지침",
    debug=True,
    log_level="DEBUG",
    host="127.0.0.1",
    port=9000
)

@server.wrap_function()
def my_function():
    pass

# SSE 트랜스포트로 실행 (stdio 대신)
server.run(transport="sse")
```

#### 동적 함수 등록

```python
from pymcp import PyMCP

server = PyMCP()

# 함수 동적 등록
for function_name, function in get_functions():
    server.add_function(function)

server.run()
```

### 예제

패키지에는 `examples` 디렉토리에 다양한 사용 사례를 보여주는 여러 예제 파일이 포함되어 있습니다.

#### 기본 예제

`examples/examples.py` 파일에는 기본 사용법 예제가 포함되어 있습니다:

```python
from pymcp import PyMCP, convert_function, mcpwrap

# 기본 함수 변환
def hello(name: str) -> str:
    return f"안녕하세요, {name}님!"

# 데코레이터 사용
@mcpwrap(name="덧셈_도구")
def add(a: int, b: int) -> int:
    return a + b

# 여러 함수 결합
calculator = PyMCP(name="계산기 서버")
calculator.add_function(add)
```

다음과 같이 예제를 실행합니다:

```bash
python examples/examples.py
```

#### LangChain 연동

`examples/langchain_example.py` 파일은 LangChain과 OpenAI 모델과의 연동을 보여줍니다:

```python
from pymcp import PyMCP
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

# PyMCP 서버 생성
server = PyMCP(name="LangChain 서버")

# LangChain 컴포넌트 생성
model = ChatOpenAI(model="gpt-4o-mini")
joke_prompt = ChatPromptTemplate.from_template(
    "{topic}에 관한 재미있는 농담을 해주세요."
)
joke_chain = joke_prompt | model

@server.wrap_function(name="generate_joke")
def generate_joke(topic: str) -> str:
    """주어진 주제에 관한 농담을 생성합니다."""
    result = joke_chain.invoke({"topic": topic})
    return result.content
```

다음과 같이 예제를 실행합니다:

```bash
python examples/langchain_example.py
```

#### LangGraph 연동

`examples/langgraph_example.py` 파일은 다단계 워크플로우를 위한 LangGraph 연동을 보여줍니다:

```python
from pymcp import PyMCP
from langgraph.graph import StateGraph, END

# PyMCP 서버 생성
server = PyMCP(name="LangGraph 서버")

# LangGraph 워크플로우 생성
workflow = StateGraph()
workflow.add_node("extract_entities", extract_entities)
workflow.add_node("lookup_info", lookup_info)
workflow.add_node("generate_response", generate_response)
workflow.add_edge("extract_entities", "lookup_info")
workflow.add_edge("lookup_info", "generate_response")
workflow.add_edge("generate_response", END)
app = workflow.compile()

@server.wrap_function(name="research_query")
def research_query(query: str) -> str:
    """다단계 워크플로우를 통해 연구 쿼리를 처리합니다."""
    result = app.invoke({"query": query})
    return result.get("response", "응답이 생성되지 않았습니다")
```

다음과 같이 예제를 실행합니다:

```bash
python examples/langgraph_example.py
```

LangChain 및 LangGraph 서버를 위한 설정 스크립트도 있습니다:

```bash
python examples/setup_langchain_server.py
```

### 라이선스

[MIT](LICENSE) © 2025 Pandas-Studio (ontofinance@gmail.com)

### 기여하기

이슈와 풀 리퀘스트를 환영합니다. 중요한 변경 사항을 작업하기 전에 먼저 이슈를 열어 변경하고자 하는 내용에 대해 논의해 주세요. 