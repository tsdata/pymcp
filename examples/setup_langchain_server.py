#!/usr/bin/env python
"""
Script to register LangChain and LangGraph MCP servers in Cursor editor
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from pymcp import add_pymcp_server, list_pymcp_servers
except ImportError:
    print("오류: pymcp 패키지를 찾을 수 없습니다. 다음 명령어로 설치하세요: pip install pymcp")
    sys.exit(1)

def parse_arguments():
    """명령줄 인수를 파싱합니다"""
    parser = argparse.ArgumentParser(description="LangChain 및 LangGraph MCP 서버 설정 도구")
    parser.add_argument('--run', choices=['langchain', 'langgraph'], 
                        help='지정된 서버를 등록 없이 바로 실행합니다')
    parser.add_argument('--set-api-key', type=str, metavar='API_KEY',
                        help='OpenAI API 키를 스크립트 실행 중에만 설정합니다')
    parser.add_argument('--create-env', action='store_true',
                        help='.env 파일을 현재 디렉토리에 생성합니다')
    parser.add_argument('--debug', action='store_true',
                        help='디버그 모드를 활성화합니다')
    return parser.parse_args()

def create_env_file(api_key=None):
    """현재 디렉토리에 .env 파일을 생성합니다"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    env_path = os.path.join(current_dir, ".env")
    
    # 이미 존재하는 파일 확인
    if os.path.exists(env_path):
        print(f"경고: .env 파일이 이미 존재합니다: {env_path}")
        overwrite = input("파일을 덮어쓰시겠습니까? (y/n): ").lower()
        if overwrite != 'y':
            print(".env 파일 생성이 취소되었습니다.")
            return False
    
    # API 키 입력 받기
    if not api_key:
        api_key = input("OpenAI API 키를 입력하세요: ")
        if not api_key:
            print("API 키를 입력하지 않았습니다. .env 파일 생성이 취소되었습니다.")
            return False
    
    # .env 파일 작성
    try:
        with open(env_path, 'w') as f:
            f.write(f"OPENAI_API_KEY={api_key}\n")
        print(f".env 파일이 생성되었습니다: {env_path}")
        print(f"API 키: {api_key[:4]}...{api_key[-4:]}")
        return True
    except Exception as e:
        print(f".env 파일 생성 중 오류가 발생했습니다: {str(e)}")
        return False

def run_server_directly(server_type, api_key=None, debug=False):
    """지정된 서버를 직접 실행합니다"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    if server_type == 'langchain':
        script_path = os.path.join(current_dir, "langchain_example.py")
    elif server_type == 'langgraph':
        script_path = os.path.join(current_dir, "langgraph_example.py")
    else:
        print(f"오류: 유효하지 않은 서버 유형 '{server_type}'")
        return False
    
    if not os.path.exists(script_path):
        print(f"오류: {script_path} 파일이 존재하지 않습니다")
        return False
    
    # 실행 환경 설정
    env = os.environ.copy()
    if api_key:
        env["OPENAI_API_KEY"] = api_key
        print(f"OpenAI API 키가 설정되었습니다: {api_key[:4]}...{api_key[-4:]}")
    
    # 실행 권한 부여
    try:
        os.chmod(script_path, 0o755)
    except Exception as e:
        print(f"경고: {script_path}에 실행 권한을 부여할 수 없습니다: {str(e)}")
    
    # 서버 실행
    print(f"{server_type} 서버를 직접 실행합니다...")
    
    try:
        cmd = [sys.executable, script_path]
        subprocess.run(cmd, env=env)
        return True
    except Exception as e:
        print(f"서버 실행 중 오류 발생: {str(e)}")
        return False

def register_servers():
    """LangChain 및 LangGraph 서버를 Cursor에 등록합니다"""
    # Define directories and paths
    current_dir = os.path.dirname(os.path.abspath(__file__))
    langchain_path = os.path.join(current_dir, "langchain_example.py")
    langgraph_path = os.path.join(current_dir, "langgraph_example.py")

    # Get the virtual environment Python executable
    venv_dir = os.path.join(current_dir, ".venv")
    if os.name == "nt":  # Windows
        venv_python = os.path.join(venv_dir, "Scripts", "python.exe")
        terminal_cmd = "cmd /k"
    else:  # macOS/Linux
        venv_python = os.path.join(venv_dir, "bin", "python")
        terminal_cmd = "osascript -e 'tell app \"Terminal\" to do script \""

    # Make scripts executable
    for script in [langchain_path, langgraph_path]:
        if os.path.exists(script):
            try:
                os.chmod(script, 0o755)
            except Exception as e:
                print(f"경고: {script}를 실행 가능하게 만들 수 없습니다: {str(e)}")

    # Check if the example files exist
    if not os.path.exists(langchain_path):
        print(f"오류: {langchain_path} 파일이 존재하지 않습니다")
        sys.exit(1)

    if not os.path.exists(langgraph_path):
        print(f"오류: {langgraph_path} 파일이 존재하지 않습니다")
        sys.exit(1)

    # Check if OpenAI API key is set
    openai_api_key = os.environ.get("OPENAI_API_KEY")
    if not openai_api_key:
        print("\n⚠️ 경고: OPENAI_API_KEY 환경 변수가 설정되지 않았습니다!")
        print("이 서버들은 제대로 작동하기 위해 OpenAI API 키가 필요합니다.")
        print("다음 방법 중 하나로 API 키를 설정하세요:")
        print("1. 현재 디렉토리에 .env 파일 생성 (아래 명령어 사용):")
        print(f"   python {os.path.basename(__file__)} --create-env")
        print("2. 환경 변수로 직접 설정:")
        print("   export OPENAI_API_KEY='your-api-key'")
        print("\n등록을 계속합니다...\n")

    # Register the LangChain Server
    print("LangChain GPT-4o-mini MCP 서버를 Cursor에 추가하는 중...")
    add_pymcp_server(
        server_name="pymcp-langchain-gpt4o",
        script_path=langchain_path,
        python_path=venv_python,
        working_dir=current_dir,
        env_vars={"PYTHONPATH": current_dir}
    )

    # Register the LangGraph Server
    print("LangGraph GPT-4o-mini MCP 서버를 Cursor에 추가하는 중...")
    add_pymcp_server(
        server_name="pymcp-langgraph-gpt4o",
        script_path=langgraph_path,
        python_path=venv_python,
        working_dir=current_dir,
        env_vars={"PYTHONPATH": current_dir}
    )

    print("\n✅ MCP 서버가 Cursor 설정에 성공적으로 추가되었습니다!")
    print(f"설정 파일: {os.path.expanduser('~/.cursor/mcp.json')}")

    # List the registered servers
    print("\n현재 등록된 서버:")
    list_pymcp_servers()

def print_instructions():
    """사용 안내 사항을 출력합니다"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    venv_dir = os.path.join(current_dir, ".venv")
    if os.name == "nt":  # Windows
        venv_python = os.path.join(venv_dir, "Scripts", "python.exe")
    else:  # macOS/Linux
        venv_python = os.path.join(venv_dir, "bin", "python")

    print("\n📋 사용 안내:")
    print("1. Cursor 에디터를 재시작하세요")
    print("2. Cursor에서 AI 패널을 열고")
    print("3. 서버 드롭다운 메뉴에서 등록된 서버 중 하나를 선택하세요:")
    print("   - pymcp-langchain-gpt4o")
    print("   - pymcp-langgraph-gpt4o")
    print("4. API 키 설정 방법:")
    print("   A. .env 파일 생성 (권장):")
    print(f"      python {os.path.basename(__file__)} --create-env")
    print("   B. 환경 변수로 직접 설정:")
    print("      export OPENAI_API_KEY='your-api-key'")
    print("\n🚀 터미널에서 서버를 직접 실행하려면:")
    print(f"  cd {current_dir} && {venv_python} langchain_example.py")
    print(f"  cd {current_dir} && {venv_python} langgraph_example.py")
    print("\n또는 다음 명령어로 서버를 직접 실행할 수 있습니다:")
    print(f"  python {os.path.basename(__file__)} --run langchain [--set-api-key YOUR_API_KEY]")
    print(f"  python {os.path.basename(__file__)} --run langgraph [--set-api-key YOUR_API_KEY]")

    print("\n🔀 'Client closed' 오류가 발생하는 경우:")
    print("1. 터미널 창에서 서버를 직접 실행해 보세요")
    print("2. OpenAI API 키가 올바르게 설정되어 있는지 확인하세요")
    print("3. 필요한 패키지가 설치되어 있는지 확인하세요:")
    print("   - langchain-core")
    print("   - langchain-openai")
    print("   - langgraph")
    print("   - python-dotenv")

    print("\n🔍 다음 예시 쿼리를 시도해 보세요:")
    print("• LangChain 서버의 경우:")
    print("  - 프로그래밍에 관한 농담 생성")
    print("  - 양자 컴퓨팅 설명")
    print("  - 이 문단을 요약해 주세요: [여기에 텍스트 입력]")
    print("\n• LangGraph 서버의 경우:")
    print("  - 연구 쿼리: Python, JavaScript, Rust 프로그래밍 언어 비교")
    print("  - 연구 쿼리: 인공지능의 역사와 미래 설명")

def main():
    """메인 함수"""
    args = parse_arguments()
    
    # .env 파일 생성 모드인 경우
    if args.create_env:
        create_env_file(args.set_api_key)
        return
    
    # 직접 실행 모드인 경우
    if args.run:
        run_server_directly(args.run, args.set_api_key, args.debug)
        return
    
    # 등록 모드인 경우 (기본)
    register_servers()
    print_instructions()

if __name__ == "__main__":
    main() 