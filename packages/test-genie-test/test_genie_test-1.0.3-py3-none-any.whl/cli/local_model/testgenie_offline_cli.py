#!/usr/bin/env python3
"""
TestGenie Offline CLI - Integration with existing testgenie CLI
Usage: test-genie offline <file_path> -p <positive> -n <negative>
"""

import os
import sys
import argparse
import time
import tempfile
import logging
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from offline_test_generator import OfflineTestGenerator

def main():
    parser = argparse.ArgumentParser(
        description="TestGenie Offline Test Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  test-genie offline func.py -p 5 -n 3
  test-genie offline /path/to/file.py --positive 4 --negative 2
  test-genie offline script.py -p 2 -n 1 --port 8124
        """
    )
    
    parser.add_argument("file_path", help="Path to the Python file to generate tests for")
    parser.add_argument("-p", "--positive", type=int, default=3, 
                       help="Number of positive test cases per function (default: 3)")
    parser.add_argument("-n", "--negative", type=int, default=2, 
                       help="Number of negative test cases per function (default: 2)")
    parser.add_argument("--model-url", 
                       default="https://drive.google.com/file/d/1Pdmqn3AqXdlaZyj7iPVCAcRVHP3n9Eht/view?usp=drive_link",
                       help="URL to GGUF model file")
    parser.add_argument("--models-dir", default="./models", 
                       help="Directory to store models")
    parser.add_argument("--server-host", default="127.0.0.1", 
                       help="Server host")
    parser.add_argument("--server-port", type=int, default=8123, 
                       help="Server port")
    parser.add_argument("--verbose", "-v", action="store_true", 
                       help="Enable verbose logging")
    parser.add_argument("--quiet", "-q", action="store_true", 
                       help="Suppress output except errors")
    
    args = parser.parse_args()
    
    # Validate file path
    if not os.path.exists(args.file_path):
        print(f"❌ Error: File not found: {args.file_path}", file=sys.stderr)
        sys.exit(1)
    
    if not (args.file_path.endswith('.py') or args.file_path.endswith('.cpp') or args.file_path.endswith('.c')):
        print(f"❌ Error: File must be a Python file (.py) or C++ file (.cpp/.c)", file=sys.stderr)
        sys.exit(1)
    
    # Validate parameters
    if args.positive < 1 or args.negative < 1:
        print("❌ Error: Positive and negative test counts must be at least 1", file=sys.stderr)
        sys.exit(1)
    
    # Setup logging
    if args.quiet:
        logging.getLogger().setLevel(logging.ERROR)
    elif args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    else:
        logging.getLogger().setLevel(logging.INFO)
    
    # Create generator
    generator = OfflineTestGenerator(
        model_url=args.model_url,
        models_dir=args.models_dir,
        server_host=args.server_host,
        server_port=args.server_port
    )
    
    if not args.quiet:
        print(f"🚀 TestGenie Offline - Generating tests for {args.file_path}")
        print(f"📊 Parameters: {args.positive} positive, {args.negative} negative test cases")
        print("=" * 60)
    
    start_time = time.time()
    
    try:
        test_file_path = generator.generate_tests_for_file(
            file_path=args.file_path,
            positive=args.positive,
            negative=args.negative
        )
        
        end_time = time.time()
        
        if test_file_path:
            if not args.quiet:
                print("=" * 60)
                print(f"✅ Success! Test file generated: {test_file_path}")
                print(f"⏱️  Total time: {end_time - start_time:.2f} seconds")
                print(f"🧪 You can run the tests with: python -m pytest {test_file_path}")
            else:
                print(test_file_path)  # Just output the file path for scripting
            sys.exit(0)
        else:
            if not args.quiet:
                print("=" * 60)
                print("❌ Failed to generate test cases")
            sys.exit(1)
            
    except KeyboardInterrupt:
        if not args.quiet:
            print("\n⚠️  Interrupted by user")
        sys.exit(1)
    except Exception as e:
        if not args.quiet:
            print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
