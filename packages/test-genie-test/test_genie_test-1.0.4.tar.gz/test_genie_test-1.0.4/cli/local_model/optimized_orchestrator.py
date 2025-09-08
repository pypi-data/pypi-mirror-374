#!/usr/bin/env python3
"""
Optimized Orchestrator - Lightweight version for CLI integration
Minimal resource usage with essential functionality only
"""

import os
import sys
import time
import logging
import signal
from pathlib import Path
from typing import Optional, Dict, Any

# Import only essential modules
from model_downloader import ModelDownloader
from runtime_installer import RuntimeInstaller
from server_manager import ServerManager
from prompt_handler import CodePromptHandler
from resource_manager import ResourceManager

class OptimizedOrchestrator:
    def __init__(self, 
                 model_url: str = "https://drive.google.com/file/d/1Pdmqn3AqXdlaZyj7iPVCAcRVHP3n9Eht/view?usp=drive_link",
                 models_dir: str = "./models",
                 server_host: str = "127.0.0.1",
                 server_port: int = 8123):
        
        self.model_url = model_url
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(exist_ok=True)
        self.server_host = server_host
        self.server_port = server_port
        
        # Initialize only essential components
        self.downloader = ModelDownloader(str(self.models_dir))
        self.installer = RuntimeInstaller()
        self.server_manager: Optional[ServerManager] = None
        self.prompt_handler: Optional[CodePromptHandler] = None
        self.resource_manager = ResourceManager()
        
        # Minimal logging
        self.logger = self._setup_logger()
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        self.running = False
        
    def _setup_logger(self):
        logger = logging.getLogger('OptimizedOrchestrator')
        logger.setLevel(logging.WARNING)  # Minimal logging
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(levelname)s: %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        self.logger.warning(f"Received signal {signum}, shutting down...")
        self.running = False
        self.cleanup()
        sys.exit(0)
    
    def _ensure_setup(self) -> bool:
        """Ensure dependencies and model are ready"""
        try:
            # Check dependencies (skip if already installed)
            if not self.installer.verify_installation():
                self.logger.warning("Installing dependencies...")
                if not self.installer.install_all():
                    return False
            
            # Check model (skip if already downloaded)
            model_files = list(self.models_dir.glob("*.gguf"))
            if not model_files:
                self.logger.warning("Downloading model...")
                try:
                    self.downloader.download_model(self.model_url)
                except Exception as e:
                    self.logger.error(f"Model download failed: {e}")
                    return False
            
            return True
        except Exception as e:
            self.logger.error(f"Setup failed: {e}")
            return False
    
    def _start_server(self) -> bool:
        """Start server with minimal resource usage"""
        try:
            # Find model
            model_files = list(self.models_dir.glob("*.gguf"))
            if not model_files:
                return False
            
            model_path = str(model_files[0])
            
            # Start server
            self.server_manager = ServerManager(
                model_path=model_path,
                host=self.server_host,
                port=self.server_port
            )
            
            success = self.server_manager.start()
            if success:
                server_url = self.server_manager.get_server_url()
                self.prompt_handler = CodePromptHandler(server_url)
                return True
            
            return False
        except Exception as e:
            self.logger.error(f"Server startup failed: {e}")
            return False
    
    def _stop_server(self):
        """Stop server and cleanup"""
        if self.server_manager:
            self.server_manager.stop()
            self.server_manager = None
    
    def generate_tests(self, source_code: str, positive: int = 3, negative: int = 2) -> Optional[str]:
        """Generate test cases with optimized parameters"""
        try:
            # Ensure setup
            if not self._ensure_setup():
                return None
            
            # Start server
            if not self._start_server():
                return None
            
            # Wait for server
            if not self.prompt_handler.wait_for_server():
                return None
            
            # Generate optimized prompt
            function_count = source_code.count('def ')
            if function_count <= 2:
                prompt = f"Write pytest tests for: {source_code}"
            else:
                prompt = f"Write {positive} positive and {negative} negative pytest tests for: {source_code}"
            
            # Generate with optimized parameters
            result = self.prompt_handler.send_prompt(
                prompt=prompt,
                max_tokens=512,
                temperature=0.3,
                top_p=0.9,
                timeout=120
            )
            
            if result and result.get("text"):
                return result["text"]
            
            return None
            
        except Exception as e:
            self.logger.error(f"Generation failed: {e}")
            return None
        finally:
            self._stop_server()
    
    def cleanup(self):
        """Cleanup resources"""
        try:
            self._stop_server()
            self.resource_manager.cleanup_all()
        except Exception as e:
            self.logger.error(f"Cleanup error: {e}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python optimized_orchestrator.py <source_code> [positive] [negative]")
        sys.exit(1)
    
    source_code = sys.argv[1]
    positive = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    negative = int(sys.argv[3]) if len(sys.argv) > 3 else 2
    
    orchestrator = OptimizedOrchestrator()
    
    try:
        result = orchestrator.generate_tests(source_code, positive, negative)
        if result:
            print(result)
            sys.exit(0)
        else:
            print("Generation failed", file=sys.stderr)
            sys.exit(1)
    finally:
        orchestrator.cleanup()

if __name__ == "__main__":
    main()
