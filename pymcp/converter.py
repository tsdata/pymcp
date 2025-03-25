"""
일반 파이썬 함수를 MCP 서버로 변환하는 모듈입니다.
이 모듈을 사용하여 일반 파이썬 함수를 MCP 서버로 쉽게 변환할 수 있습니다.
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

# 타입 정의
FunctionType = Callable[..., Any]
McpResultType = Sequence[Union[TextContent, ImageContent, EmbeddedResource]]

# 데코레이터 함수의 타입
F = TypeVar('F', bound=Callable[..., Any])

class PyMCP:
    """
    일반 파이썬 함수를 MCP 서버로 변환하는 클래스입니다.
    이 클래스를 사용하여 여러 함수를 하나의 MCP 서버로 결합할 수 있습니다.
    """
    
    def __init__(self, name: str = "PyMCP Server", instructions: Optional[str] = None, **kwargs: Any):
        """
        PyMCP 서버를 초기화합니다.
        
        Args:
            name: 서버 이름
            instructions: 서버 사용 지침 (선택 사항)
            **kwargs: FastMCP에 전달할 추가 설정
        """
        self.mcp = FastMCP(name=name, instructions=instructions, **kwargs)
        self.functions: Dict[str, FunctionType] = {}
    
    def add_function(self, func: FunctionType, name: Optional[str] = None, description: Optional[str] = None) -> None:
        """
        일반 파이썬 함수를 MCP 서버에 도구로 추가합니다.
        
        Args:
            func: 등록할 파이썬 함수
            name: 도구 이름 (기본값은 함수 이름)
            description: 도구 설명 (기본값은 함수 독스트링)
        """
        func_name = name or func.__name__
        func_description = description or inspect.getdoc(func) or f"{func_name} 함수"
        
        # 함수의 결과를 MCP 호환 형식으로 변환하는 래퍼 함수 생성
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> McpResultType:
            result = func(*args, **kwargs)
            return self._convert_to_mcp_format(result)
        
        # 래퍼 함수를 MCP 도구로 등록
        self.mcp.add_tool(wrapper, name=func_name, description=func_description)
        self.functions[func_name] = func
    
    def _convert_to_mcp_format(self, result: Any) -> McpResultType:
        """
        함수 결과를 MCP 호환 형식으로 변환합니다.
        
        Args:
            result: 변환할 함수 결과
            
        Returns:
            MCP 호환 형식으로 변환된 결과
        """
        # 이미 MCP 호환 형식이면 그대로 반환
        if isinstance(result, (TextContent, ImageContent, EmbeddedResource)) or (
            isinstance(result, list) and all(isinstance(item, (TextContent, ImageContent, EmbeddedResource)) for item in result)
        ):
            return result if isinstance(result, list) else [result]
        
        # 이미지 객체 처리
        if isinstance(result, Image):
            return [ImageContent(type="image", data=result.data, mimeType=result.mime_type)]
        
        # 텍스트로 변환하여 반환
        text_result = str(result)
        return [TextContent(type="text", text=text_result)]
    
    def run(self, transport: Literal["stdio", "sse"] = "stdio") -> None:
        """
        MCP 서버를 실행합니다.
        
        Args:
            transport: 전송 프로토콜 ("stdio" 또는 "sse")
        """
        self.mcp.run(transport=transport)
    
    def wrap_function(self, name: Optional[str] = None, description: Optional[str] = None) -> Callable[[F], F]:
        """
        함수를 MCP 도구로 등록하는 데코레이터입니다.
        
        Args:
            name: 도구 이름 (기본값은 함수 이름)
            description: 도구 설명 (기본값은 함수 독스트링)
            
        Returns:
            함수를 MCP 도구로 등록하는 데코레이터
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
    단일 함수를 MCP 서버로 변환합니다.
    
    Args:
        func: 변환할 함수
        name: 도구 이름 (기본값은 함수 이름)
        description: 도구 설명 (기본값은 함수 독스트링)
        server_name: 서버 이름
        instructions: 서버 사용 지침 (선택 사항)
        **kwargs: FastMCP에 전달할 추가 설정
        
    Returns:
        생성된 PyMCP 인스턴스
    """
    pymcp = PyMCP(name=server_name, instructions=instructions, **kwargs)
    pymcp.add_function(func, name=name, description=description)
    return pymcp


def mcpwrap(name: Optional[str] = None, description: Optional[str] = None,
           server_name: str = "PyMCP Function Server",
           instructions: Optional[str] = None, **kwargs: Any) -> Callable[[F], F]:
    """
    함수를 MCP 서버로 변환하는 데코레이터입니다.
    
    Args:
        name: 도구 이름 (기본값은 함수 이름)
        description: 도구 설명 (기본값은 함수 독스트링)
        server_name: 서버 이름
        instructions: 서버 사용 지침 (선택 사항)
        **kwargs: FastMCP에 전달할 추가 설정
        
    Returns:
        함수를 받아 MCP 서버로 변환하는 데코레이터
    """
    def decorator(func: F) -> F:
        # 함수 속성에 MCP 서버 생성 함수 추가
        setattr(func, '_pymcp_convert', lambda: convert_function(
            func, name=name, description=description,
            server_name=server_name, instructions=instructions, **kwargs
        ))
        
        # 함수 속성에 실행 함수 추가
        setattr(func, 'serve_mcp', lambda transport="stdio": convert_function(
            func, name=name, description=description,
            server_name=server_name, instructions=instructions, **kwargs
        ).run(transport=transport))
        
        return func
    
    return decorator 