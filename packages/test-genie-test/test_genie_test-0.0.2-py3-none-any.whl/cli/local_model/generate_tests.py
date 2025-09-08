#!/usr/bin/env python3
"""
Script to generate test cases from a Python file using TestGenie
"""

import sys
import os
from pathlib import Path

def generate_tests_for_file(file_path: str, output_file: str = None):
    """Generate test cases for a Python file using TestGenie"""
    
    # Read the source file
    with open(file_path, 'r') as f:
        file_content = f.read()
    
    # Create the prompt
    prompt = f"""Generate comprehensive pytest test cases for the following Python functions:

{file_content}

Create pytest test cases that cover:
- Normal functionality with positive and negative numbers
- Edge cases (zero, large numbers)  
- Error handling (TypeError for non-integers)
- Division by zero case
- Use proper pytest structure with classes and methods
- Include proper imports and setup"""
    
    # Run TestGenie
    cmd = f"""cd /Users/kushagra/Desktop/TestGenie/StarCoder2_3B && source ../venv/bin/activate && python main_orchestrator.py --prompt "{prompt}" --max-tokens 1024 --temperature 0.2"""
    
    print("🚀 Running TestGenie to generate test cases...")
    print(f"📁 Source file: {file_path}")
    print(f"🎯 Command: {cmd}")
    print("\n" + "="*80)
    
    # Execute the command
    os.system(cmd)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python generate_tests.py <path_to_python_file>")
        print("Example: python generate_tests.py /Users/kushagra/Desktop/TestGenie/test_gen/python_examples/func.py")
        sys.exit(1)
    
    file_path = sys.argv[1]
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        sys.exit(1)
    
    generate_tests_for_file(file_path)
