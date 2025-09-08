#!/usr/bin/env python3
"""
CLI Integration Helper - Add this to your existing testgenie CLI
"""

import os
import sys
import subprocess
from pathlib import Path

def run_offline_test_generation(file_path: str, positive: int = 3, negative: int = 2, **kwargs):
    """
    Run offline test generation
    
    Args:
        file_path: Path to the Python file
        positive: Number of positive test cases
        negative: Number of negative test cases
        **kwargs: Additional arguments (verbose, quiet, etc.)
    
    Returns:
        str: Path to generated test file, or None if failed
    """
    
    # Get the directory of this script
    script_dir = Path(__file__).parent
    
    # Build command
    cmd = [
        sys.executable,
        str(script_dir / "testgenie_offline_cli.py"),
        file_path,
        "-p", str(positive),
        "-n", str(negative)
    ]
    
    # Add optional arguments
    if kwargs.get("verbose"):
        cmd.append("-v")
    if kwargs.get("quiet"):
        cmd.append("-q")
    if kwargs.get("port"):
        cmd.extend(["--server-port", str(kwargs["port"])])
    if kwargs.get("model_url"):
        cmd.extend(["--model-url", kwargs["model_url"]])
    
    try:
        # Run the command
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            # Extract test file path from output
            output_lines = result.stdout.strip().split('\n')
            for line in output_lines:
                if line.startswith("✅ Success! Test file generated:"):
                    return line.split(": ")[1]
                elif line.endswith(".py") and "test_" in line:
                    return line
            
            # If no specific path found, return success
            return "success"
        else:
            print(f"Error: {result.stderr}", file=sys.stderr)
            return None
            
    except subprocess.TimeoutExpired:
        print("Error: Test generation timed out", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return None

def main():
    """Example usage"""
    if len(sys.argv) < 2:
        print("Usage: python cli_integration.py <file_path> [positive] [negative]")
        sys.exit(1)
    
    file_path = sys.argv[1]
    positive = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    negative = int(sys.argv[3]) if len(sys.argv) > 3 else 2
    
    result = run_offline_test_generation(file_path, positive, negative, verbose=True)
    
    if result:
        print(f"✅ Test generation successful: {result}")
    else:
        print("❌ Test generation failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
