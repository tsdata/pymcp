"""
Module for converting regular Python functions to MCP servers.
This module allows you to easily convert regular Python functions to MCP servers.
"""

import inspect
import functools
from typing import Any, Callable, Dict, List, Optional, Union, Literal, Sequence, Type, cast, get_type_hints, TypeVar

from mcp.server.fastmcp import FastMCP
from mcp.types import (
    TextContent, 
    ImageContent, 
    EmbeddedResource,
)
from mcp.server.fastmcp.utilities.types import Image

# Type definitions
FunctionType = Callable[..., Any]
McpResultType = Sequence[Union[TextContent, ImageContent, EmbeddedResource]]

# Type for decorator functions
F = TypeVar('F', bound=Callable[..., Any])

class PyMCP:
    """
    Class for converting regular Python functions to MCP servers.
    This class allows you to combine multiple functions into one MCP server.
    """
    
    def __init__(self, name: str = "PyMCP Server", instructions: Optional[str] = None, **kwargs: Any):
        """
        Initialize a PyMCP server.
        
        Args:
            name: Server name
            instructions: Server usage instructions (optional)
            **kwargs: Additional settings to pass to FastMCP
        """
        self.mcp = FastMCP(name=name, instructions=instructions, **kwargs)
        self.functions: Dict[str, FunctionType] = {}
    
    def add_function(self, func: FunctionType, name: Optional[str] = None, description: Optional[str] = None) -> None:
        """
        Add a regular Python function to the MCP server as a tool.
        
        Args:
            func: Python function to register
            name: Tool name (defaults to function name)
            description: Tool description (defaults to function docstring)
        """
        func_name = name or func.__name__
        func_description = description or inspect.getdoc(func) or f"Function {func_name}"
        
        # Create a wrapper function that converts function results to MCP-compatible format
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> McpResultType:
            result = func(*args, **kwargs)
            return self._convert_to_mcp_format(result)
        
        # Register the wrapper function as an MCP tool
        self.mcp.add_tool(wrapper, name=func_name, description=func_description)
        self.functions[func_name] = func
    
    def _convert_to_mcp_format(self, result: Any) -> McpResultType:
        """
        Convert function result to MCP-compatible format.
        
        Args:
            result: Function result to convert
            
        Returns:
            Result converted to MCP-compatible format
        """
        # If already in MCP-compatible format, return as is
        if isinstance(result, (TextContent, ImageContent, EmbeddedResource)) or (
            isinstance(result, list) and all(isinstance(item, (TextContent, ImageContent, EmbeddedResource)) for item in result)
        ):
            return result if isinstance(result, list) else [result]
        
        # Handle image objects
        if isinstance(result, Image):
            return [ImageContent(type="image", data=result.data, mimeType=result.mime_type)]
        
        # Convert to text and return
        text_result = str(result)
        return [TextContent(type="text", text=text_result)]
    
    def run(self, transport: Literal["stdio", "sse"] = "stdio") -> None:
        """
        Run the MCP server.
        
        Args:
            transport: Transport protocol ("stdio" or "sse")
        """
        self.mcp.run(transport=transport)
    
    def wrap_function(self, name: Optional[str] = None, description: Optional[str] = None) -> Callable[[F], F]:
        """
        Decorator that registers a function as an MCP tool.
        
        Args:
            name: Tool name (defaults to function name)
            description: Tool description (defaults to function docstring)
            
        Returns:
            Decorator that registers a function as an MCP tool
        """
        def decorator(func: F) -> F:
            self.add_function(func, name=name, description=description)
            return func
        return decorator


def convert_function(func: FunctionType, name: Optional[str] = None,
                    description: Optional[str] = None,
                    server_name: str = "PyMCP Function Server",
                    instructions: Optional[str] = None,
                    **kwargs: Any) -> PyMCP:
    """
    Convert a single function to an MCP server.
    
    Args:
        func: Function to convert
        name: Tool name (defaults to function name)
        description: Tool description (defaults to function docstring)
        server_name: Server name
        instructions: Server usage instructions (optional)
        **kwargs: Additional settings to pass to FastMCP
        
    Returns:
        Created PyMCP instance
    """
    pymcp = PyMCP(name=server_name, instructions=instructions, **kwargs)
    pymcp.add_function(func, name=name, description=description)
    return pymcp


def mcpwrap(name: Optional[str] = None, description: Optional[str] = None,
           server_name: str = "PyMCP Function Server",
           instructions: Optional[str] = None, **kwargs: Any) -> Callable[[F], F]:
    """
    Decorator that converts a function to an MCP server.
    
    Args:
        name: Tool name (defaults to function name)
        description: Tool description (defaults to function docstring)
        server_name: Server name
        instructions: Server usage instructions (optional)
        **kwargs: Additional settings to pass to FastMCP
        
    Returns:
        Decorator that takes a function and converts it to an MCP server
    """
    def decorator(func: F) -> F:
        # Add MCP server creation function to function attributes
        setattr(func, '_pymcp_convert', lambda: convert_function(
            func, name=name, description=description,
            server_name=server_name, instructions=instructions, **kwargs
        ))
        
        # Add run function to function attributes
        setattr(func, 'serve_mcp', lambda transport="stdio": convert_function(
            func, name=name, description=description,
            server_name=server_name, instructions=instructions, **kwargs
        ).run(transport=transport))
        
        return func
    
    return decorator 