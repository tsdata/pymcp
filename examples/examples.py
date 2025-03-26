"""
Python library pymcp usage examples
"""

from pymcp import PyMCP, convert_function, mcpwrap


# Example 1: Converting a basic function to an MCP server
def hello(name: str) -> str:
    """Function that generates a greeting"""
    return f"Hello, {name}!"

# Converting the function to an MCP server
hello_server = convert_function(hello)

# You can run the server with:
# hello_server.run()


# Example 2: Using a decorator
@mcpwrap(name="addition_tool", description="A tool that adds two numbers")
def add(a: int, b: int) -> int:
    """Function that adds two numbers"""
    return a + b

# You can run the server with:
# add.serve_mcp()


# Example 3: Combining multiple functions into one MCP server
def multiply(a: int, b: int) -> int:
    """Function that multiplies two numbers"""
    return a * b

def divide(a: int, b: int) -> float:
    """Function that divides two numbers"""
    if b == 0:
        return "Cannot divide by zero."
    return a / b

# Combining multiple functions into one server
calculator = PyMCP(name="Calculator Server", instructions="A server that provides simple calculation functions.")
calculator.add_function(add)
calculator.add_function(multiply)
calculator.add_function(divide)

# You can run the server with:
# calculator.run()


# Example 4: Combining multiple functions using decorators
math_server = PyMCP(name="Math Server", instructions="A server that provides mathematical functions.")

@math_server.wrap_function()
def square(x: int) -> int:
    """Calculate the square of a number"""
    return x * x

@math_server.wrap_function()
def factorial(n: int) -> int:
    """Calculate factorial"""
    if n <= 1:
        return 1
    return n * factorial(n - 1)

# You can run the server with:
# math_server.run()


if __name__ == "__main__":
    # Choose which server to run and uncomment
    # hello_server.run()
    # add.serve_mcp()
    calculator.run()
    # math_server.run()
    
    # Guidance message
    print("Uncomment the line in the example file to run a specific server.")
    print("Example: Uncomment the 'hello_server.run()' line and run again.") 