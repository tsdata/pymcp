# PyMCP

> [English](#english) | [한국어](README.ko.md)

A tool for converting regular Python functions to MCP (Model Context Protocol) servers.

**Copyright (c) 2024 Pandas-Studio (ontofinance@gmail.com)**

---

<a name="english"></a>
## English Documentation

- [Introduction](#introduction)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Usage](#usage)
  - [Basic Function Conversion](#basic-function-conversion)
  - [Using Decorators](#using-decorators)
  - [Combining Multiple Functions](#combining-multiple-functions)
  - [Using Multiple Decorators](#using-multiple-decorators)
- [Integration with Cursor Editor](#integration-with-cursor-editor)
  - [Command Line Configuration](#command-line-configuration)
  - [Python Code Configuration](#python-code-configuration)
  - [Automatic Setup](#automatic-setup)
- [Function Types and Return Values](#function-types-and-return-values)
- [Advanced Usage](#advanced-usage)
- [Examples](#examples)
  - [Basic Examples](#basic-examples)
  - [LangChain Integration](#langchain-integration)
  - [LangGraph Integration](#langgraph-integration)
- [License](#license)
- [Contributing](#contributing)

### Introduction

PyMCP simplifies the process of converting regular Python functions into MCP servers. This allows AI models like those in Cursor editor to call your Python functions directly. No deep understanding of the MCP protocol is required.

### Installation

```bash
pip install pymcp
```

### Quick Start

1. Define a regular Python function:

```python
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b
```

2. Convert it to an MCP server with one line:

```python
from pymcp import convert_function
server = convert_function(add)
server.run()
```

3. That's it! Your function is now available as an MCP tool.

### Usage

#### Basic Function Conversion

```python
from pymcp import convert_function

def hello(name: str) -> str:
    """Generate a greeting"""
    return f"Hello, {name}!"

# Convert function to MCP server
hello_server = convert_function(hello)

# Run the server
hello_server.run()
```

#### Using Decorators

```python
from pymcp import mcpwrap

@mcpwrap(name="addition_tool", description="A tool to add two numbers")
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

# Run the server
add.serve_mcp()
```

#### Combining Multiple Functions

```python
from pymcp import PyMCP

def multiply(a: int, b: int) -> int:
    """Multiply two numbers"""
    return a * b

def divide(a: int, b: int) -> float:
    """Divide two numbers"""
    if b == 0:
        return "Cannot divide by zero"
    return a / b

# Combine multiple functions into one server
calculator = PyMCP(name="Calculator Server", instructions="A server providing calculator functions")
calculator.add_function(multiply)
calculator.add_function(divide)

# Run the server
calculator.run()
```

#### Using Multiple Decorators

```python
from pymcp import PyMCP

math_server = PyMCP(name="Math Server", instructions="A server providing mathematical functions")

@math_server.wrap_function()
def square(x: int) -> int:
    """Calculate the square of a number"""
    return x * x

@math_server.wrap_function()
def factorial(n: int) -> int:
    """Calculate the factorial of a number"""
    if n <= 1:
        return 1
    return n * factorial(n - 1)

# Run the server
math_server.run()
```

### Integration with Cursor Editor

PyMCP provides easy integration with the Cursor editor.

#### Command Line Configuration

```bash
# Add an MCP server
pymcp cursor add-server calculator examples/examples.py

# Explicitly specify the Python interpreter of a virtual environment
pymcp cursor add-server calculator examples/examples.py --python /path/to/venv/bin/python

# List servers
pymcp cursor list-servers

# Remove a server
pymcp cursor remove-server calculator

# Show configuration file path
pymcp cursor config-path
```

#### Python Code Configuration

```python
from pymcp import add_pymcp_server, list_pymcp_servers, remove_pymcp_server

# Add an MCP server
add_pymcp_server(
    "calculator",
    "/path/to/examples/examples.py",
    python_path="/path/to/venv/bin/python"
)

# List servers
servers = list_pymcp_servers()

# Remove a server
remove_pymcp_server("calculator")
```

#### Automatic Setup

The package includes a setup_cursor.py script that automatically registers a calculator server:

```bash
# Activate virtual environment
source .venv/bin/activate

# Run setup script
python setup_cursor.py
```

This script:
1. Detects your virtual environment
2. Registers the example calculator server in Cursor
3. Sets up all necessary paths and environment variables

After running this script, restart Cursor editor, select the 'pymcp-calculator' server in the AI panel, and start using it!

### Function Types and Return Values

PyMCP supports various function types and return values:

- **Basic Types**: integers, floats, strings, and booleans are automatically converted
- **Lists and Dictionaries**: complex data structures are converted to text
- **MCP-Specific Types**: TextContent, ImageContent, and EmbeddedResource are supported
- **Error Handling**: exceptions and error messages are properly handled

Examples:

```python
# String return
def greet(name: str) -> str:
    return f"Hello, {name}!"

# Image return (requires PIL)
def generate_image() -> Image:
    from PIL import Image
    image = Image.new('RGB', (100, 100), color='red')
    return image

# Complex return (converted to text)
def get_data() -> dict:
    return {"name": "John", "age": 30}
```

### Advanced Usage

#### Custom Server Configuration

```python
from pymcp import PyMCP

# Configure the server with custom settings
server = PyMCP(
    name="Custom Server",
    instructions="Detailed instructions for the server",
    debug=True,
    log_level="DEBUG",
    host="127.0.0.1",
    port=9000
)

@server.wrap_function()
def my_function():
    pass

# Run with SSE transport (instead of stdio)
server.run(transport="sse")
```

#### Dynamic Function Registration

```python
from pymcp import PyMCP

server = PyMCP()

# Register functions dynamically
for function_name, function in get_functions():
    server.add_function(function)

server.run()
```

### Examples

The package includes several example files in the `examples` directory that demonstrate various use cases.

#### Basic Examples

The `examples/examples.py` file contains basic usage examples:

```python
from pymcp import PyMCP, convert_function, mcpwrap

# Basic function conversion
def hello(name: str) -> str:
    return f"Hello, {name}!"

# Using decorators
@mcpwrap(name="addition_tool")
def add(a: int, b: int) -> int:
    return a + b

# Combining multiple functions
calculator = PyMCP(name="Calculator Server")
calculator.add_function(add)
```

Run this example with:

```bash
python examples/examples.py
```

#### LangChain Integration

The `examples/langchain_example.py` file demonstrates integration with LangChain and OpenAI models:

```python
from pymcp import PyMCP
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

# Create a PyMCP server
server = PyMCP(name="LangChain Server")

# Create LangChain components
model = ChatOpenAI(model="gpt-4o-mini")
joke_prompt = ChatPromptTemplate.from_template(
    "Tell me a funny joke about {topic}."
)
joke_chain = joke_prompt | model

@server.wrap_function(name="generate_joke")
def generate_joke(topic: str) -> str:
    """Generate a joke about the given topic."""
    result = joke_chain.invoke({"topic": topic})
    return result.content
```

Run this example with:

```bash
python examples/langchain_example.py
```

#### LangGraph Integration

The `examples/langgraph_example.py` file demonstrates integration with LangGraph for multi-step workflows:

```python
from pymcp import PyMCP
from langgraph.graph import StateGraph, END

# Create a PyMCP server
server = PyMCP(name="LangGraph Server")

# Create a LangGraph workflow
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
    """Process a research query through a multi-step workflow."""
    result = app.invoke({"query": query})
    return result.get("response", "No response generated")
```

Run this example with:

```bash
python examples/langgraph_example.py
```

There's also a setup script for LangChain and LangGraph servers:

```bash
python examples/setup_langchain_server.py
```

### License

[MIT](LICENSE) © 2025 Pandas-Studio (ontofinance@gmail.com)

### Contributing

Issues and pull requests are welcome. Before making significant changes, please open an issue to discuss what you would like to change. 