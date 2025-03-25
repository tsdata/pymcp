#!/usr/bin/env python
"""
Example script showing LangGraph and GPT-4o-mini integration with PyMCP
"""

import os
import sys
import json
import signal
import time
from typing import Dict, List, Any, Optional
from pymcp import PyMCP
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
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

class State:
    """State object for the research workflow."""
    def __init__(self, query: str = ""):
        self.query = query
        self.entities: List[str] = []
        self.information: Dict[str, str] = {}
        self.response: str = ""

def extract_entities(state: State) -> State:
    """Extract key entities from the user query."""
    try:
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY를 찾을 수 없습니다")
        
        print(f"extract_entities 함수 실행 중 - 쿼리: {state.query[:30]}...")
        model = ChatOpenAI(
            model="gpt-4o-mini", 
            temperature=0.3,
            timeout=60,
            max_retries=3
        )
        prompt = ChatPromptTemplate.from_template("""
        Extract the key entities/topics that need to be researched from the query.
        Return ONLY a JSON array of strings with no explanation.

        Query: {query}
        
        JSON Array:
        """)
        
        chain = prompt | model
        
        result = chain.invoke({"query": state.query})
        # Process the JSON string to get a list of entities
        try:
            entities = json.loads(result.content)
            if not isinstance(entities, list):
                entities = [entities]
        except:
            # Fallback if JSON parsing fails
            entities = [e.strip() for e in result.content.strip("[]").split(",")]
        
        state.entities = entities
        print(f"추출된 엔티티: {entities}")
    except Exception as e:
        print(f"extract_entities 함수 오류: {str(e)}")
        # Fallback to a generic entity if extraction fails
        state.entities = ["general information"]
        print(f"기본 엔티티로 대체: {state.entities}")
    
    return state

def lookup_info(state: State) -> State:
    """Look up information about the extracted entities."""
    try:
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY를 찾을 수 없습니다")
        
        print(f"lookup_info 함수 실행 중 - 엔티티: {state.entities}")
        model = ChatOpenAI(
            model="gpt-4o-mini", 
            temperature=0.3,
            timeout=60,
            max_retries=3
        )
        prompt = ChatPromptTemplate.from_template("""
        Provide a concise summary of information about: {entity}
        Focus only on the most important facts and keep it to 2-3 sentences.
        """)
        
        chain = prompt | model
        
        info = {}
        for entity in state.entities:
            try:
                print(f"정보 검색 중: {entity}")
                result = chain.invoke({"entity": entity})
                info[entity] = result.content
                print(f"정보 검색 결과 ({entity}): {result.content[:30]}...")
            except Exception as e:
                print(f"{entity} 정보 검색 오류: {str(e)}")
                info[entity] = f"{entity}에 대한 정보를 현재 사용할 수 없습니다."
        
        state.information = info
    except Exception as e:
        print(f"lookup_info 함수 오류: {str(e)}")
        # Set fallback information
        state.information = {entity: f"{entity}에 대한 정보를 검색할 수 없습니다." 
                            for entity in state.entities}
    
    return state

def generate_response(state: State) -> State:
    """Generate a final response based on the information gathered."""
    try:
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY를 찾을 수 없습니다")
        
        print(f"generate_response 함수 실행 중 - 정보 수집 완료")
        model = ChatOpenAI(
            model="gpt-4o-mini", 
            temperature=0.5,
            timeout=60,
            max_retries=3
        )
        
        # Create context from the information gathered
        context = ""
        for entity, info in state.information.items():
            context += f"{entity}: {info}\n\n"
        
        prompt = ChatPromptTemplate.from_template("""
        Based on the following information, provide a comprehensive response to the query.
        Make sure to address all aspects of the query and integrate the information seamlessly.
        
        INFORMATION:
        {context}
        
        QUERY:
        {query}
        
        RESPONSE:
        """)
        
        chain = prompt | model
        
        result = chain.invoke({
            "context": context,
            "query": state.query
        })
        
        state.response = result.content
        print(f"최종 응답 생성: {state.response[:30]}...")
    except Exception as e:
        print(f"generate_response 함수 오류: {str(e)}")
        # Generate fallback response
        state.response = "죄송합니다만, 귀하의 요청을 처리하는 동안 오류가 발생했습니다. 나중에 다시 시도해 주세요."
    
    return state

def setup_openai_api() -> bool:
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

def safe_invoke_workflow(workflow, query: str) -> str:
    """Safely invoke a workflow with error handling"""
    try:
        print(f"워크플로우 실행 중 - 쿼리: {query[:30]}...")
        state = State(query=query)
        result = workflow.invoke(state)
        # result가 State 객체인지 확인
        if isinstance(result, State):
            response = result.response if hasattr(result, 'response') else "응답이 생성되지 않았습니다"
        elif isinstance(result, dict) and 'response' in result:
            response = result['response']
        else:
            response = f"알 수 없는 응답 형식: {type(result)}"
        print(f"워크플로우 완료 - 응답: {response[:30]}...")
        return response
    except Exception as e:
        error_msg = f"워크플로우 실행 오류: {str(e)}"
        print(error_msg)
        return f"죄송합니다, 오류가 발생했습니다: {error_msg}"

def main():
    """Set up and run a PyMCP server with LangGraph and GPT-4o-mini."""
    print("\n============================================")
    print("LangGraph GPT-4o-mini MCP 서버 시작 중...")
    print("============================================\n")
    
    # Check for OpenAI API key
    if not setup_openai_api():
        return
        
    # Create a PyMCP server with more robust error handling
    try:
        print("PyMCP 서버 생성 중...")
        server = PyMCP(
            name="LangGraph GPT-4o-mini Server",
            instructions="This server processes research queries through a multi-step workflow using LangGraph and GPT-4o-mini.",
            debug=True  # Enable debug mode for more verbose logs
        )
        print("PyMCP 서버 생성 완료!")
    except Exception as e:
        print(f"PyMCP 서버 생성 오류: {str(e)}")
        return
    
    # Create a StateGraph for the workflow
    try:
        print("워크플로우 그래프 생성 중...")
        workflow = StateGraph(State)
        
        # Add nodes
        workflow.add_node("extract_entities", extract_entities)
        workflow.add_node("lookup_info", lookup_info)
        workflow.add_node("generate_response", generate_response)
        
        # Add edges
        workflow.add_edge("extract_entities", "lookup_info")
        workflow.add_edge("lookup_info", "generate_response")
        workflow.add_edge("generate_response", END)
        
        # Set entry point
        workflow.set_entry_point("extract_entities")
        
        # Compile the graph
        app = workflow.compile()
        print("워크플로우 그래프 생성 및 컴파일 완료!")
    except Exception as e:
        print(f"워크플로우 그래프 생성 오류: {str(e)}")
        return
    
    @server.wrap_function(name="research_query", description="Process a research query through a multi-step workflow")
    def research_query(query: str) -> str:
        """Process a research query through a multi-step workflow."""
        print(f"'research_query' 함수 호출됨: query={query[:30]}...")
        result = safe_invoke_workflow(app, query)
        return result
    
    print("\nLangGraph GPT-4o-mini MCP 서버가 시작되었습니다!")
    print("사용 가능한 도구:")
    print("1. research_query - 다단계 워크플로우를 통한 연구 쿼리 처리")
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