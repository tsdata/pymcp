#!/usr/bin/env python
"""
PyMCP Command Line Interface
"""

import argparse
import sys
from pathlib import Path

from pymcp.utils.cursor_config import (
    add_pymcp_server,
    remove_pymcp_server,
    list_pymcp_servers,
    get_mcp_config_path
)


def main():
    """Main function for the pymcp command line interface"""
    parser = argparse.ArgumentParser(description="PyMCP - A tool for converting regular Python functions to MCP servers")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # cursor command and subcommands
    cursor_parser = subparsers.add_parser("cursor", help="Manage Cursor editor configuration")
    cursor_subparsers = cursor_parser.add_subparsers(dest="cursor_command", help="Cursor commands")
    
    # cursor add-server command
    add_server_parser = cursor_subparsers.add_parser("add-server", help="Add MCP server")
    add_server_parser.add_argument("name", help="Server name")
    add_server_parser.add_argument("script", help="Script path")
    add_server_parser.add_argument("--python", help="Python interpreter path")
    add_server_parser.add_argument("--cwd", help="Working directory")
    
    # cursor remove-server command
    remove_server_parser = cursor_subparsers.add_parser("remove-server", help="Remove MCP server")
    remove_server_parser.add_argument("name", help="Server name")
    
    # cursor list-servers command
    cursor_subparsers.add_parser("list-servers", help="List MCP servers")
    
    # cursor config-path command
    cursor_subparsers.add_parser("config-path", help="Show MCP configuration file path")
    
    # Additional command groups can be added here
    
    # Parse command line arguments
    args = parser.parse_args()
    
    # Print help if no command specified
    if args.command is None:
        parser.print_help()
        return 1
    
    # Process cursor commands
    if args.command == "cursor":
        if args.cursor_command is None:
            cursor_parser.print_help()
            return 1
        
        if args.cursor_command == "add-server":
            add_pymcp_server(args.name, args.script, args.python, args.cwd)
        elif args.cursor_command == "remove-server":
            success = remove_pymcp_server(args.name)
            return 0 if success else 1
        elif args.cursor_command == "list-servers":
            list_pymcp_servers()
        elif args.cursor_command == "config-path":
            print(get_mcp_config_path())
        else:
            cursor_parser.print_help()
            return 1
    else:
        parser.print_help()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 