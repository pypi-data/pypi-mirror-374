#!/usr/bin/env python3
"""
Prompt Handler - Handles prompt requests and captures output
Optimized for CPU-only inference with minimal resource usage
"""

import requests
import time
import logging
from typing import Dict, Any, Optional, List
import json

class PromptHandler:
    def __init__(self, server_url: str = "http://127.0.0.1:8000"):
        self.server_url = server_url
        self.logger = self._setup_logger()
        
    def _setup_logger(self):
        logger = logging.getLogger('PromptHandler')
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger
    
    def _preprocess_prompt(self, prompt: str) -> str:
        """Preprocess prompt for complete code generation"""
        # Check if this is a test generation request
        if "test" in prompt.lower() and ("pytest" in prompt.lower() or "assert" in prompt.lower()):
            return self._preprocess_test_prompt(prompt)
        
        # Add context for complete, runnable code
        if "python" in prompt.lower() or "function" in prompt.lower():
            enhanced_prompt = f"""Write a complete, runnable Python script. The code should be:
- Complete and executable
- Include proper function definitions
- Include a main block or direct execution
- No comments or explanations, just the code

Task: {prompt}

```python
"""
        elif "cpp" in prompt.lower() or "c++" in prompt.lower():
            enhanced_prompt = f"""Write a complete, runnable C++ program. The code should be:
- Complete and executable
- Include proper headers and main function
- No comments or explanations, just the code

Task: {prompt}

```cpp
"""
        else:
            enhanced_prompt = f"""Write a complete, runnable Python script. The code should be:
- Complete and executable
- Include proper function definitions
- Include a main block or direct execution
- No comments or explanations, just the code

Task: {prompt}

```python
"""
        
        return enhanced_prompt
    
    def _preprocess_test_prompt(self, prompt: str) -> str:
        """Preprocess prompt specifically for test generation"""
        # Simplified test generation prompt to avoid timeout
        enhanced_prompt = f"""Write pytest test cases. Keep it simple and focused.

{prompt}

```python
"""
        return enhanced_prompt
    
    def send_prompt(self, 
                   prompt: str, 
                   max_tokens: int = 1024,  # Increased for complete code
                   temperature: float = 0.1,  # Lower for more focused output
                   top_p: float = 0.9,
                   timeout: int = 120) -> Optional[Dict[str, Any]]:
        """Send prompt to server and capture output"""
        try:
            # Preprocess prompt for better generation
            processed_prompt = self._preprocess_prompt(prompt)
            self.logger.info(f"Sending prompt (length: {len(processed_prompt)})")
            
            payload = {
                "text": processed_prompt,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "top_p": top_p
            }
            
            start_time = time.time()
            response = requests.post(
                f"{self.server_url}/generate",
                json=payload,
                timeout=timeout
            )
            end_time = time.time()
            
            if response.status_code == 200:
                result = response.json()
                result["generation_time"] = end_time - start_time
                
                # Clean up the generated code
                generated_text = result["text"]
                if "```" in generated_text:
                    # Extract code from markdown blocks
                    code_blocks = generated_text.split("```")
                    if len(code_blocks) > 1:
                        generated_text = code_blocks[1].strip()
                        if generated_text.startswith("python\n"):
                            generated_text = generated_text[7:]
                        elif generated_text.startswith("cpp\n"):
                            generated_text = generated_text[4:]
                
                result["text"] = generated_text.strip()
                self.logger.info(f"Generated {len(result['text'])} characters in {result['generation_time']:.2f}s")
                return result
            else:
                self.logger.error(f"Server error: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.Timeout:
            self.logger.error("Request timeout")
            return None
        except requests.exceptions.ConnectionError:
            self.logger.error("Connection error - server may not be running")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            return None
    
    def send_batch_prompts(self, 
                          prompts: List[str],
                          max_tokens: int = 512,
                          temperature: float = 0.7,
                          top_p: float = 0.9,
                          delay_between_requests: float = 0.1) -> List[Optional[Dict[str, Any]]]:
        """Send multiple prompts with delay between requests"""
        results = []
        
        for i, prompt in enumerate(prompts):
            self.logger.info(f"Processing prompt {i+1}/{len(prompts)}")
            result = self.send_prompt(prompt, max_tokens, temperature, top_p)
            results.append(result)
            
            # Small delay to prevent overwhelming the server
            if i < len(prompts) - 1:
                time.sleep(delay_between_requests)
        
        return results
    
    def check_server_health(self) -> bool:
        """Check if server is healthy and ready"""
        try:
            response = requests.get(f"{self.server_url}/health", timeout=5)
            if response.status_code == 200:
                health_data = response.json()
                return health_data.get("model_loaded", False)
            return False
        except:
            return False
    
    def wait_for_server(self, max_wait: int = 60) -> bool:
        """Wait for server to be ready"""
        self.logger.info("Waiting for server to be ready...")
        
        for i in range(max_wait):
            if self.check_server_health():
                self.logger.info("Server is ready")
                return True
            time.sleep(1)
        
        self.logger.error("Server not ready within timeout")
        return False

class CodePromptHandler(PromptHandler):
    """Specialized handler for code generation prompts"""
    
    def __init__(self, server_url: str = "http://127.0.0.1:8000"):
        super().__init__(server_url)
        self.code_prompts = {
            "python_function": """Write a Python function that {description}. 
Include proper error handling and docstring. Return only the function code.""",
            
            "python_class": """Write a Python class that {description}. 
Include proper methods, error handling, and docstrings. Return only the class code.""",
            
            "cpp_function": """Write a C++ function that {description}. 
Include proper headers, error handling, and comments. Return only the function code.""",
            
            "test_cases": """Generate comprehensive test cases for the following code:
{code}

Return test cases in the same language as the code."""
        }
    
    def generate_code(self, 
                     code_type: str, 
                     description: str,
                     max_tokens: int = 1024,
                     temperature: float = 0.3) -> Optional[str]:
        """Generate code based on type and description"""
        if code_type not in self.code_prompts:
            self.logger.error(f"Unknown code type: {code_type}")
            return None
        
        prompt = self.code_prompts[code_type].format(description=description)
        result = self.send_prompt(prompt, max_tokens, temperature)
        
        if result:
            return result["text"].strip()
        return None
    
    def generate_test_cases(self, 
                           code: str,
                           max_tokens: int = 1024,
                           temperature: float = 0.3) -> Optional[str]:
        """Generate test cases for given code"""
        prompt = self.code_prompts["test_cases"].format(code=code)
        result = self.send_prompt(prompt, max_tokens, temperature)
        
        if result:
            return result["text"].strip()
        return None

if __name__ == "__main__":
    # Example usage
    handler = CodePromptHandler()
    
    if handler.wait_for_server():
        # Generate a Python function
        code = handler.generate_code(
            "python_function",
            "calculates the factorial of a number"
        )
        
        if code:
            print("Generated code:")
            print(code)
            
            # Generate test cases
            test_cases = handler.generate_test_cases(code)
            if test_cases:
                print("\nGenerated test cases:")
                print(test_cases)
    else:
        print("Server not ready")
