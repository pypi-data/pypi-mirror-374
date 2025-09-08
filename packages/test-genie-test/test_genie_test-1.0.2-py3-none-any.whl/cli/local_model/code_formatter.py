#!/usr/bin/env python3
"""
Code Formatter and Validator - Formats and validates generated code
Optimized for CPU-only processing with minimal resource usage
"""

import re
import ast
import logging
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path
import subprocess
import tempfile
import os

class CodeFormatter:
    def __init__(self):
        self.logger = self._setup_logger()
        
    def _setup_logger(self):
        logger = logging.getLogger('CodeFormatter')
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger
    
    def clean_generated_code(self, code: str) -> str:
        """Clean and format generated code"""
        if not code:
            return ""
        
        # Remove markdown code blocks
        code = re.sub(r'```(?:python|py|cpp|c\+\+|javascript|js|java|c|go|rust)?\n?', '', code)
        code = re.sub(r'```\n?', '', code)
        
        # Remove common prefixes/suffixes
        code = re.sub(r'^(Here\'s|Here is|Here\'s the|The following|Generated code:?)\s*', '', code, flags=re.IGNORECASE)
        code = re.sub(r'\n*(This code|The code|Note:|Explanation:).*$', '', code, flags=re.IGNORECASE | re.DOTALL)
        
        # Clean up whitespace
        code = code.strip()
        
        # Ensure proper line endings
        lines = code.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Remove trailing whitespace
            line = line.rstrip()
            # Skip empty lines at the beginning
            if not cleaned_lines and not line:
                continue
            cleaned_lines.append(line)
        
        # Remove trailing empty lines
        while cleaned_lines and not cleaned_lines[-1]:
            cleaned_lines.pop()
        
        return '\n'.join(cleaned_lines)
    
    def format_python_code(self, code: str) -> Tuple[str, bool]:
        """Format Python code using black (if available) or basic formatting"""
        try:
            # Try using black formatter
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                temp_file = f.name
            
            try:
                result = subprocess.run([
                    'black', '--line-length', '88', '--quiet', temp_file
                ], capture_output=True, text=True, timeout=10)
                
                if result.returncode == 0:
                    with open(temp_file, 'r') as f:
                        formatted_code = f.read()
                    os.unlink(temp_file)
                    return formatted_code, True
                else:
                    os.unlink(temp_file)
                    return self._basic_python_format(code), False
                    
            except (subprocess.TimeoutExpired, FileNotFoundError):
                os.unlink(temp_file)
                return self._basic_python_format(code), False
                
        except Exception as e:
            self.logger.warning(f"Black formatting failed: {e}")
            return self._basic_python_format(code), False
    
    def _basic_python_format(self, code: str) -> str:
        """Basic Python code formatting"""
        try:
            # Parse and unparse to fix basic formatting
            tree = ast.parse(code)
            formatted = ast.unparse(tree)
            return formatted
        except SyntaxError:
            # If parsing fails, return cleaned code
            return self.clean_generated_code(code)
    
    def format_cpp_code(self, code: str) -> Tuple[str, bool]:
        """Format C++ code using clang-format (if available) or basic formatting"""
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.cpp', delete=False) as f:
                f.write(code)
                temp_file = f.name
            
            try:
                result = subprocess.run([
                    'clang-format', '-style=Google', temp_file
                ], capture_output=True, text=True, timeout=10)
                
                if result.returncode == 0:
                    formatted_code = result.stdout
                    os.unlink(temp_file)
                    return formatted_code, True
                else:
                    os.unlink(temp_file)
                    return self._basic_cpp_format(code), False
                    
            except (subprocess.TimeoutExpired, FileNotFoundError):
                os.unlink(temp_file)
                return self._basic_cpp_format(code), False
                
        except Exception as e:
            self.logger.warning(f"Clang-format failed: {e}")
            return self._basic_cpp_format(code), False
    
    def _basic_cpp_format(self, code: str) -> str:
        """Basic C++ code formatting"""
        # Clean up common formatting issues
        code = re.sub(r'\n\s*\n\s*\n+', '\n\n', code)  # Multiple blank lines
        code = re.sub(r'{\s*\n', '{\n', code)  # Opening braces
        code = re.sub(r'\n\s*}', '\n}', code)  # Closing braces
        code = re.sub(r';\s*\n', ';\n', code)  # Semicolons
        
        return self.clean_generated_code(code)

class CodeValidator:
    def __init__(self):
        self.logger = self._setup_logger()
        
    def _setup_logger(self):
        logger = logging.getLogger('CodeValidator')
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger
    
    def validate_python_code(self, code: str) -> Dict[str, Any]:
        """Validate Python code syntax and basic structure"""
        result = {
            "valid": False,
            "errors": [],
            "warnings": [],
            "suggestions": []
        }
        
        try:
            # Parse the code
            tree = ast.parse(code)
            
            # Basic validation
            if not code.strip():
                result["errors"].append("Code is empty")
                return result
            
            # Check for common issues
            self._check_python_issues(tree, result)
            
            result["valid"] = len(result["errors"]) == 0
            
        except SyntaxError as e:
            result["errors"].append(f"Syntax error: {e}")
        except Exception as e:
            result["errors"].append(f"Validation error: {e}")
        
        return result
    
    def _check_python_issues(self, tree: ast.AST, result: Dict[str, Any]):
        """Check for common Python code issues"""
        for node in ast.walk(tree):
            # Check for print statements (suggest logging)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == 'print':
                result["warnings"].append("Consider using logging instead of print statements")
            
            # Check for bare except clauses
            if isinstance(node, ast.ExceptHandler) and node.type is None:
                result["warnings"].append("Bare except clause - consider specifying exception type")
            
            # Check for unused imports (basic check)
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.asname:
                        result["suggestions"].append(f"Consider using 'import {alias.name}' instead of 'import {alias.name} as {alias.asname}'")
    
    def validate_cpp_code(self, code: str) -> Dict[str, Any]:
        """Validate C++ code syntax (basic validation)"""
        result = {
            "valid": False,
            "errors": [],
            "warnings": [],
            "suggestions": []
        }
        
        try:
            if not code.strip():
                result["errors"].append("Code is empty")
                return result
            
            # Basic C++ validation
            self._check_cpp_issues(code, result)
            
            result["valid"] = len(result["errors"]) == 0
            
        except Exception as e:
            result["errors"].append(f"Validation error: {e}")
        
        return result
    
    def _check_cpp_issues(self, code: str, result: Dict[str, Any]):
        """Check for common C++ code issues"""
        # Check for proper includes
        if '#include' not in code and ('std::' in code or 'cout' in code or 'cin' in code):
            result["warnings"].append("Missing standard library includes")
        
        # Check for main function
        if 'int main(' not in code and 'void main(' not in code:
            result["suggestions"].append("Consider adding a main function for executable code")
        
        # Check for proper namespace usage
        if 'using namespace std;' in code:
            result["warnings"].append("Consider avoiding 'using namespace std' in header files")
        
        # Check for memory management
        if 'new ' in code and 'delete ' not in code:
            result["warnings"].append("Memory allocated with 'new' should be freed with 'delete'")

class CodeProcessor:
    """Main class that combines formatting and validation"""
    
    def __init__(self):
        self.formatter = CodeFormatter()
        self.validator = CodeValidator()
        self.logger = self._setup_logger()
        
    def _setup_logger(self):
        logger = logging.getLogger('CodeProcessor')
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger
    
    def process_code(self, code: str, language: str = "python") -> Dict[str, Any]:
        """Process code: clean, format, and validate"""
        result = {
            "original_code": code,
            "cleaned_code": "",
            "formatted_code": "",
            "validation": {},
            "success": False
        }
        
        try:
            # Clean the code
            cleaned = self.formatter.clean_generated_code(code)
            result["cleaned_code"] = cleaned
            
            # Format the code
            if language.lower() == "python":
                formatted, format_success = self.formatter.format_python_code(cleaned)
                validation = self.validator.validate_python_code(formatted)
            elif language.lower() in ["cpp", "c++", "c"]:
                formatted, format_success = self.formatter.format_cpp_code(cleaned)
                validation = self.validator.validate_cpp_code(formatted)
            else:
                formatted = cleaned
                format_success = False
                validation = {"valid": True, "errors": [], "warnings": [], "suggestions": []}
            
            result["formatted_code"] = formatted
            result["validation"] = validation
            result["format_success"] = format_success
            result["success"] = validation.get("valid", False)
            
            self.logger.info(f"Code processing completed. Valid: {result['success']}")
            
        except Exception as e:
            self.logger.error(f"Code processing failed: {e}")
            result["error"] = str(e)
        
        return result

if __name__ == "__main__":
    # Example usage
    processor = CodeProcessor()
    
    sample_python = """
    def factorial(n):
        if n < 0:
            return None
        if n == 0:
            return 1
        return n * factorial(n-1)
    """
    
    result = processor.process_code(sample_python, "python")
    print("Processing result:")
    print(f"Success: {result['success']}")
    print(f"Formatted code:\n{result['formatted_code']}")
    if result['validation']['warnings']:
        print(f"Warnings: {result['validation']['warnings']}")
