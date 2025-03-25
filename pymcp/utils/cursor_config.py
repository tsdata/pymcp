"""
Utility module for creating MCP server configuration files for Cursor editor.
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any, Union


def get_cursor_config_dir() -> Path:
    """Returns the Cursor configuration directory path."""
    if sys.platform == "darwin":  # macOS
        return Path.home() / ".cursor"
    elif sys.platform == "win32":  # Windows
        return Path.home() / "AppData" / "Roaming" / "cursor"
    else:  # Linux and other platforms
        return Path.home() / ".config" / "cursor"


def get_mcp_config_path() -> Path:
    """Returns the MCP configuration file path."""
    return get_cursor_config_dir() / "mcp.json"


def read_mcp_config() -> Dict[str, Any]:
    """Reads existing MCP configuration."""
    config_path = get_mcp_config_path()
    if not config_path.exists():
        # Return default structure
        return {"mcpServers": {}}
    
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def write_mcp_config(config: Dict[str, Any]) -> None:
    """Writes MCP configuration to file."""
    config_path = get_mcp_config_path()
    
    # Create configuration directory if it doesn't exist
    config_dir = get_cursor_config_dir()
    if not config_dir.exists():
        config_dir.mkdir(parents=True, exist_ok=True)
    
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)


def add_pymcp_server(
    server_name: str, 
    script_path: str, 
    python_path: Optional[str] = None,
    working_dir: Optional[str] = None,
    env_vars: Optional[Dict[str, str]] = None
) -> None:
    """Adds a PyMCP server to the Cursor MCP configuration.
    
    Args:
        server_name: MCP server name
        script_path: Path to the Python script to execute
        python_path: Path to the Python interpreter (default: system Python)
        working_dir: Working directory (default: script directory)
        env_vars: Environment variables (default: includes PYTHONPATH)
    """
    # Convert to absolute path
    script_path = os.path.abspath(script_path)
    
    # Use script directory as working directory if not specified
    if working_dir is None:
        working_dir = os.path.dirname(script_path)
    else:
        working_dir = os.path.abspath(working_dir)
    
    # Determine Python interpreter path
    if python_path is None:
        # Try to use virtual environment Python
        venv_path = os.path.join(working_dir, '.venv', 'bin', 'python')
        if os.path.exists(venv_path):
            python_path = venv_path
        else:
            # Use system Python
            python_path = "python"
    
    # Set environment variables
    if env_vars is None:
        env_vars = {}
    
    # Add working directory to PYTHONPATH
    if "PYTHONPATH" not in env_vars:
        env_vars["PYTHONPATH"] = working_dir
    
    # Read existing configuration
    config = read_mcp_config()
    
    # Add server configuration
    config["mcpServers"][server_name] = {
        "command": python_path,
        "args": [script_path],
        "cwd": working_dir,
        "env": env_vars
    }
    
    # Save configuration
    write_mcp_config(config)
    
    print(f"Added '{server_name}' server to Cursor MCP configuration.")
    print(f"Configuration file location: {get_mcp_config_path()}")


def remove_pymcp_server(server_name: str) -> bool:
    """Removes a PyMCP server from the Cursor MCP configuration.
    
    Args:
        server_name: Name of the MCP server to remove
        
    Returns:
        bool: Whether removal was successful
    """
    # Read existing configuration
    config = read_mcp_config()
    
    # Check if server exists
    if server_name not in config["mcpServers"]:
        print(f"Server '{server_name}' does not exist in configuration.")
        return False
    
    # Remove server configuration
    del config["mcpServers"][server_name]
    
    # Save configuration
    write_mcp_config(config)
    
    print(f"Removed '{server_name}' server from Cursor MCP configuration.")
    return True


def list_pymcp_servers() -> List[str]:
    """Returns a list of servers registered in the Cursor MCP configuration."""
    config = read_mcp_config()
    servers = list(config["mcpServers"].keys())
    
    print("Servers registered in Cursor MCP configuration:")
    for server in servers:
        print(f"- {server}")
    
    return servers


if __name__ == "__main__":
    # Test code
    import argparse
    
    parser = argparse.ArgumentParser(description="Cursor MCP Configuration Management Tool")
    subparsers = parser.add_subparsers(dest="command", help="Command")
    
    # add command
    add_parser = subparsers.add_parser("add", help="Add server")
    add_parser.add_argument("name", help="Server name")
    add_parser.add_argument("script", help="Script path")
    add_parser.add_argument("--python", help="Python interpreter path")
    add_parser.add_argument("--cwd", help="Working directory")
    
    # remove command
    remove_parser = subparsers.add_parser("remove", help="Remove server")
    remove_parser.add_argument("name", help="Server name")
    
    # list command
    subparsers.add_parser("list", help="List servers")
    
    args = parser.parse_args()
    
    if args.command == "add":
        add_pymcp_server(args.name, args.script, args.python, args.cwd)
    elif args.command == "remove":
        remove_pymcp_server(args.name)
    elif args.command == "list":
        list_pymcp_servers()
    else:
        parser.print_help() 