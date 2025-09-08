#!/usr/bin/env python3
"""
Runtime Installer - Silent installation of GGUF runtime
Optimized for CPU-only inference with minimal resource usage
"""

import os
import subprocess
import sys
import platform
import logging
from pathlib import Path
from typing import Optional, List

class RuntimeInstaller:
    def __init__(self, install_dir: str = "./runtime"):
        self.install_dir = Path(install_dir)
        self.install_dir.mkdir(exist_ok=True)
        self.logger = self._setup_logger()
        self.system = platform.system().lower()
        
    def _setup_logger(self):
        logger = logging.getLogger('RuntimeInstaller')
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger
    
    def install_llama_cpp(self) -> bool:
        """Install llama-cpp-python with CPU-only support"""
        try:
            self.logger.info("Installing llama-cpp-python (CPU-only)...")
            
            # Uninstall existing version if any
            subprocess.run([sys.executable, "-m", "pip", "uninstall", "-y", "llama-cpp-python"], 
                         capture_output=True, check=False)
            
            # Install with CPU-only flags
            cmd = [
                sys.executable, "-m", "pip", "install", 
                "llama-cpp-python", 
                "--no-cache-dir",
                "--disable-pip-version-check",
                "--quiet"
            ]
            
            # Add CPU-only compilation flags
            env = os.environ.copy()
            env["CMAKE_ARGS"] = "-DLLAMA_CUBLAS=OFF -DLLAMA_CUDA=OFF -DLLAMA_METAL=OFF"
            env["FORCE_CMAKE"] = "1"
            
            result = subprocess.run(cmd, env=env, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.logger.info("llama-cpp-python installed successfully")
                return True
            else:
                self.logger.error(f"Installation failed: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to install llama-cpp-python: {e}")
            return False
    
    def install_dependencies(self) -> bool:
        """Install required dependencies"""
        dependencies = [
            "requests",
            "psutil",
            "fastapi",
            "uvicorn[standard]",
            "pydantic"
        ]
        
        try:
            self.logger.info("Installing dependencies...")
            
            for dep in dependencies:
                result = subprocess.run([
                    sys.executable, "-m", "pip", "install", 
                    dep, "--no-cache-dir", "--quiet"
                ], capture_output=True, text=True)
                
                if result.returncode != 0:
                    self.logger.error(f"Failed to install {dep}: {result.stderr}")
                    return False
                    
            self.logger.info("All dependencies installed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to install dependencies: {e}")
            return False
    
    def verify_installation(self) -> bool:
        """Verify that all components are properly installed"""
        try:
            # Test llama-cpp-python import
            import llama_cpp
            self.logger.info("llama-cpp-python import successful")
            
            # Test other dependencies
            import requests
            import psutil
            import fastapi
            import uvicorn
            
            self.logger.info("All dependencies verified successfully")
            return True
            
        except ImportError as e:
            self.logger.error(f"Import verification failed: {e}")
            return False
    
    def install_all(self) -> bool:
        """Install all required components"""
        self.logger.info("Starting silent installation...")
        
        # Check if already installed
        if self.verify_installation():
            self.logger.info("All dependencies already installed and verified")
            return True
        
        if not self.install_dependencies():
            return False
            
        if not self.install_llama_cpp():
            return False
            
        if not self.verify_installation():
            return False
            
        self.logger.info("Installation completed successfully")
        return True

if __name__ == "__main__":
    installer = RuntimeInstaller()
    success = installer.install_all()
    sys.exit(0 if success else 1)
