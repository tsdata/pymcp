#!/usr/bin/env python
"""
Example script to register a calculator server in Cursor
"""

import os
import sys
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from pymcp import add_pymcp_server, list_pymcp_servers

# Get current directory and file paths
current_dir = Path(__file__).parent.absolute()
examples_path = current_dir / "examples" / "examples.py"
venv_python = current_dir / ".venv" / "bin" / "python"

# Check if virtual environment Python exists
python_path = str(venv_python) if venv_python.exists() else "python"

# Register calculator server in Cursor
add_pymcp_server(
    "pymcp-calculator",
    str(examples_path),
    python_path=python_path,
    working_dir=str(current_dir),
    env_vars={"PYTHONPATH": str(current_dir)}
)

print(f"\nCalculator server has been registered! Here's how to use it:")
print(f"1. Restart your Cursor editor.")
print(f"2. Select the 'pymcp-calculator' server in the AI panel.")
print(f"3. Ask the AI to perform calculations like 'add 5 and 7' or 'divide 10 by 2'.\n")

# List registered servers
list_pymcp_servers() 