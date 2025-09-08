#!/usr/bin/env python3
"""
Optimized Test Generation Script - Fixes timeout issues
"""

import sys
import os
import time
from pathlib import Path

def generate_tests_optimized(file_path: str):
    """Generate test cases with optimized parameters to avoid timeouts"""
    
    # Read the source file
    with open(file_path, 'r') as f:
        file_content = f.read()
    
    print("🚀 Generating test cases with optimized parameters...")
    print(f"📁 Source file: {file_path}")
    print("⚡ Using optimized settings to avoid timeouts")
    print("\n" + "="*80)
    
    # Create a simplified, focused prompt
    prompt = f"Write pytest test cases for these functions:\n\n{file_content}\n\nKeep tests simple and focused."
    
    # Use optimized parameters
    cmd = f"""cd /Users/kushagra/Desktop/TestGenie/StarCoder2_3B && source ../venv/bin/activate && python main_orchestrator.py --prompt "{prompt}" --max-tokens 512 --temperature 0.4"""
    
    print(f"🎯 Command: {cmd}")
    print("\n" + "="*80)
    
    # Execute with timeout monitoring
    start_time = time.time()
    result = os.system(cmd)
    end_time = time.time()
    
    print(f"\n⏱️  Execution time: {end_time - start_time:.2f} seconds")
    
    if result == 0:
        print("✅ Test generation completed successfully!")
    else:
        print("❌ Test generation failed or timed out")
        print("\n🔧 Try these alternatives:")
        print("1. Reduce max-tokens to 256")
        print("2. Increase temperature to 0.5")
        print("3. Break down the prompt into smaller parts")

def generate_tests_simple(file_path: str):
    """Generate test cases with very simple prompts"""
    
    # Read the source file
    with open(file_path, 'r') as f:
        file_content = f.read()
    
    print("🚀 Generating test cases with simple prompts...")
    
    # Try generating tests for each function individually
    functions = []
    lines = file_content.split('\n')
    current_function = []
    
    for line in lines:
        if line.strip().startswith('def '):
            if current_function:
                functions.append('\n'.join(current_function))
            current_function = [line]
        elif line.strip() and not line.startswith('#'):
            current_function.append(line)
    
    if current_function:
        functions.append('\n'.join(current_function))
    
    print(f"📊 Found {len(functions)} functions to test")
    
    for i, func in enumerate(functions, 1):
        print(f"\n🧪 Generating tests for function {i}/{len(functions)}")
        
        # Very simple prompt
        prompt = f"Write a simple test for: {func}"
        
        cmd = f"""cd /Users/kushagra/Desktop/TestGenie/StarCoder2_3B && source ../venv/bin/activate && python main_orchestrator.py --prompt "{prompt}" --max-tokens 256 --temperature 0.3"""
        
        print(f"🎯 Testing: {func.split('(')[0].replace('def ', '')}")
        result = os.system(cmd)
        
        if result == 0:
            print("✅ Success!")
        else:
            print("❌ Failed - trying with even simpler prompt...")
            
            # Ultra-simple fallback
            simple_prompt = f"assert {func.split('(')[0].replace('def ', '')}(1, 2) == 3"
            cmd = f"""cd /Users/kushagra/Desktop/TestGenie/StarCoder2_3B && source ../venv/bin/activate && python main_orchestrator.py --prompt "{simple_prompt}" --max-tokens 128 --temperature 0.2"""
            os.system(cmd)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python generate_tests_optimized.py <path_to_python_file> [simple]")
        print("Example: python generate_tests_optimized.py /Users/kushagra/Desktop/TestGenie/test_gen/python_examples/func.py")
        print("Add 'simple' for individual function testing")
        sys.exit(1)
    
    file_path = sys.argv[1]
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        sys.exit(1)
    
    if len(sys.argv) > 2 and sys.argv[2] == "simple":
        generate_tests_simple(file_path)
    else:
        generate_tests_optimized(file_path)
