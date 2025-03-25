#!/usr/bin/env python
"""
Example script showing LangChain and GPT-4o-mini integration with PyMCP
"""

import os
import sys
import signal
import time
from typing import Optional, Dict, Any
from pymcp import PyMCP, mcpwrap
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

# 현재 디렉토리의 .env 파일 로드
load_dotenv()

# Global variable to track server state
server_running = True

# =================================================================
# API 키 설정 방법:
# 1. .env 파일을 생성하고 다음 내용 추가: OPENAI_API_KEY=your-api-key-here
# 2. 또는 환경 변수로 직접 설정: export OPENAI_API_KEY=your-api-key-here
# 3. 또는 아래 주석을 해제하고 직접 키 입력 (보안상 권장하지 않음)
# =================================================================
# os.environ["OPENAI_API_KEY"] = "your-api-key-here"
# =================================================================

def signal_handler(sig, frame):
    """Handle interrupt signals gracefully"""
    global server_running
    print("\nShutting down server gracefully...")
    server_running = False
    time.sleep(1)
    sys.exit(0)

# Register signal handlers
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def setup_openai_api():
    """Set up and verify OpenAI API key"""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("OPENAI_API_KEY를 찾을 수 없습니다.")
        print("다음 방법 중 하나로 API 키를 설정하세요:")
        print("1. 현재 디렉토리에 .env 파일 생성하고 다음 내용 추가:")
        print("   OPENAI_API_KEY=your-api-key-here")
        print("2. 환경 변수로 직접 설정:")
        print("   export OPENAI_API_KEY='your-api-key'")
        print("3. 스크립트 상단의 주석을 해제하고 API 키를 직접 입력")
        return False
    print(f"OpenAI API 키가 설정되었습니다: {api_key[:4]}...{api_key[-4:]}")
    return True

def create_model():
    """Create and return an OpenAI chat model with error handling"""
    try:
        api_key = os.environ.get("OPENAI_API_KEY")
        print(f"API 키 확인: {api_key[:4]}...{api_key[-4:]}")
        return ChatOpenAI(
            model="gpt-4o-mini", 
            temperature=0.7,
            api_key=api_key,
            timeout=60,
            max_retries=3
        )
    except Exception as e:
        print(f"OpenAI 모델 생성 오류: {str(e)}")
        return None

def safe_invoke(chain, inputs: Dict[str, Any]) -> Optional[str]:
    """Safely invoke a LangChain chain with error handling"""
    try:
        result = chain.invoke(inputs)
        return result.content
    except Exception as e:
        error_msg = f"LangChain 호출 오류: {str(e)}"
        print(error_msg)
        return f"죄송합니다, 오류가 발생했습니다: {error_msg}"

def main():
    """Set up and run a PyMCP server with LangChain and GPT-4o-mini."""
    print("\n============================================")
    print("LangChain GPT-4o-mini MCP 서버 시작 중...")
    print("============================================\n")
    
    # Check for OpenAI API key or prompt the user
    if not setup_openai_api():
        return

    # Create a PyMCP server with more robust error handling
    try:
        print("PyMCP 서버 생성 중...")
        server = PyMCP(
            name="LangChain GPT-4o-mini Server",
            instructions="This is a server that uses LangChain with GPT-4o-mini model. Available tools are for generating jokes, explaining concepts, and summarizing text.",
            debug=True,  # Enable debug mode for more verbose logs
        )
        print("PyMCP 서버 생성 완료!")
    except Exception as e:
        print(f"PyMCP 서버 생성 오류: {str(e)}")
        return

    # Initialize the chat model
    print("OpenAI 모델 초기화 중...")
    model = create_model()
    if not model:
        return
    print("OpenAI 모델 초기화 완료!")

    # Joke generation prompt
    print("프롬프트 템플릿 생성 중...")
    joke_prompt = ChatPromptTemplate.from_template(
        "Tell me a funny joke about {topic}. Keep it clean and suitable for all ages."
    )
    joke_chain = joke_prompt | model

    # Explanation prompt
    explain_prompt = ChatPromptTemplate.from_template(
        "Explain {concept} in simple terms, as if explaining to a middle school student."
    )
    explain_chain = explain_prompt | model

    # Summarization prompt
    summary_prompt = ChatPromptTemplate.from_template(
        "Summarize the following text in a concise way, highlighting the main points:\n\n{text}"
    )
    summary_chain = summary_prompt | model
    print("프롬프트 템플릿 생성 완료!")

    @server.wrap_function(name="generate_joke", description="Generate a joke about a given topic")
    def generate_joke(topic: str) -> str:
        """Generate a joke about the given topic."""
        print(f"'generate_joke' 함수 호출됨: topic={topic}")
        result = safe_invoke(joke_chain, {"topic": topic})
        print(f"'generate_joke' 함수 결과: {result[:30]}...")
        return result

    @server.wrap_function(name="explain_concept", description="Explain a concept in simple terms")
    def explain_concept(concept: str) -> str:
        """Explain a concept in simple terms."""
        print(f"'explain_concept' 함수 호출됨: concept={concept}")
        result = safe_invoke(explain_chain, {"concept": concept})
        print(f"'explain_concept' 함수 결과: {result[:30]}...")
        return result

    @server.wrap_function(name="summarize_text", description="Summarize the provided text")
    def summarize_text(text: str) -> str:
        """Summarize the provided text."""
        print(f"'summarize_text' 함수 호출됨: text={text[:30]}...")
        result = safe_invoke(summary_chain, {"text": text})
        print(f"'summarize_text' 함수 결과: {result[:30]}...")
        return result

    print("\nLangChain GPT-4o-mini MCP 서버가 시작되었습니다!")
    print("사용 가능한 도구:")
    print("1. generate_joke - 주제에 관한 농담 생성")
    print("2. explain_concept - 개념을 간단하게 설명")
    print("3. summarize_text - 텍스트 요약")
    print("\n서버를 종료하려면 Ctrl+C를 누르세요")
    
    # Run the server with error handling
    print("\n서버 실행 중...")
    try:
        server.run()
    except KeyboardInterrupt:
        print("\n서버 종료 요청...")
    except Exception as e:
        print(f"\n예상치 못한 오류: {str(e)}")
    finally:
        print("서버 종료 완료")

if __name__ == "__main__":
    main() 