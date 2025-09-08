#!/usr/bin/env python3
"""
Example script showing how to use TestGenie pipeline
"""

from main_orchestrator import TestGenieOrchestrator
import time

def main():
    # Initialize the orchestrator
    orchestrator = TestGenieOrchestrator(
        model_url="https://drive.google.com/file/d/1Pdmqn3AqXdlaZyj7iPVCAcRVHP3n9Eht/view?usp=drive_link",  # Replace with your model URL
        models_dir="./models",
        server_host="127.0.0.1",
        server_port=8123
    )
    
    # Example prompts
    prompts = [
        "Write a Python function to calculate the factorial of a number",
        "Create a Python class for a simple calculator with basic operations",
        "Write a C++ function to reverse a string",
        "Generate test cases for a function that checks if a number is prime"
    ]
    
    print("TestGenie Pipeline Example")
    print("=" * 50)
    
    for i, prompt in enumerate(prompts, 1):
        print(f"\nExample {i}: {prompt}")
        print("-" * 30)
        
        # Run the pipeline
        result = orchestrator.run_pipeline(
            prompt=prompt,
            language="python" if "Python" in prompt else "cpp",
            max_tokens=512,
            temperature=0.3
        )
        
        if result["success"]:
            print("✅ Success!")
            print("Generated Code:")
            print(result["formatted_code"])
            
            if result["validation"].get("warnings"):
                print("\n⚠️  Warnings:")
                for warning in result["validation"]["warnings"]:
                    print(f"   - {warning}")
        else:
            print("❌ Failed!")
            for error in result["errors"]:
                print(f"   Error: {error}")
        
        print("\n" + "=" * 50)
        
        # Small delay between examples
        if i < len(prompts):
            time.sleep(2)
    
    print("\nPipeline examples completed!")

if __name__ == "__main__":
    main()
