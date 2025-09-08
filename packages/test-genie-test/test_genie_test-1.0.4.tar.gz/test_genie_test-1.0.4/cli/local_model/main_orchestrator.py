#!/usr/bin/env python3
"""
Main Orchestrator - Executes the complete pipeline
Optimized for CPU-only inference with minimal resource usage
"""

import os
import sys
import time
import logging
import signal
import argparse
from pathlib import Path
from typing import Dict, Any, Optional, List

# Import our modules
from model_downloader import ModelDownloader
from runtime_installer import RuntimeInstaller
from server_manager import ServerManager
from prompt_handler import CodePromptHandler
from code_formatter import CodeProcessor
from resource_manager import ResourceManager

MODEL_URL = "https://drive.google.com/file/d/1Pdmqn3AqXdlaZyj7iPVCAcRVHP3n9Eht/view?usp=drive_link"

class TestGenieOrchestrator:
    def __init__(self, 
                model_url: str = MODEL_URL,
                 models_dir: str = "./models",
                 server_host: str = "127.0.0.1",
                 server_port: int = 8123):
        
        self.model_url = model_url
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(exist_ok=True)
        self.server_host = server_host
        self.server_port = server_port
        
        # Initialize components
        self.downloader = ModelDownloader(str(self.models_dir))
        self.installer = RuntimeInstaller()
        self.server_manager: Optional[ServerManager] = None
        self.prompt_handler: Optional[CodePromptHandler] = None
        self.code_processor = CodeProcessor()
        self.resource_manager = ResourceManager()
        
        # Setup logging
        self.logger = self._setup_logger()
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        self.running = False
        
    def _setup_logger(self):
        logger = logging.getLogger('TestGenieOrchestrator')
        logger.setLevel(logging.INFO)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
        
        # File handler
        log_file = Path("testgenie.log")
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(console_formatter)
        logger.addHandler(file_handler)
        
        return logger
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        self.logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.running = False
        self.cleanup()
        sys.exit(0)
    
    def step1_download_model(self) -> bool:
        """Step 1: Download GGUF model from storage"""
        self.logger.info("=== Step 1: Downloading model ===")
        
        try:
            model_path = self.downloader.download_model(self.model_url)
            self.logger.info(f"Model downloaded to: {model_path}")
            return True
        except Exception as e:
            self.logger.error(f"Model download failed: {e}")
            return False
    
    def step2_install_runtime(self) -> bool:
        """Step 2: Install runtime (silent)"""
        self.logger.info("=== Step 2: Installing runtime ===")
        
        try:
            success = self.installer.install_all()
            if success:
                self.logger.info("Runtime installation completed")
            else:
                self.logger.error("Runtime installation failed")
            return success
        except Exception as e:
            self.logger.error(f"Runtime installation failed: {e}")
            return False
    
    def step3_start_server(self) -> bool:
        """Step 3: Start server in background (detached)"""
        self.logger.info("=== Step 3: Starting server ===")
        
        try:
            # Find the downloaded model
            model_files = list(self.models_dir.glob("*.gguf"))
            if not model_files:
                self.logger.error("No GGUF model found in models directory")
                return False
            
            model_path = str(model_files[0])
            self.logger.info(f"Using model: {model_path}")
            
            # Start server manager
            self.server_manager = ServerManager(
                model_path=model_path,
                host=self.server_host,
                port=self.server_port
            )
            
            success = self.server_manager.start()
            if success:
                self.logger.info("Server started successfully")
                # Initialize prompt handler
                server_url = self.server_manager.get_server_url()
                self.prompt_handler = CodePromptHandler(server_url)
                return True
            else:
                self.logger.error("Server startup failed")
                return False
                
        except Exception as e:
            self.logger.error(f"Server startup failed: {e}")
            return False
    
    def step4_send_prompt(self, prompt: str, timeout: int = 120, **kwargs) -> Optional[Dict[str, Any]]:
        """Step 4: Send prompt request and capture output"""
        self.logger.info("=== Step 4: Processing prompt ===")
        
        if not self.prompt_handler:
            self.logger.error("Prompt handler not initialized")
            return None
        
        try:
            # Wait for server to be ready
            if not self.prompt_handler.wait_for_server():
                self.logger.error("Server not ready")
                return None
            
            # Send prompt
            result = self.prompt_handler.send_prompt(prompt, timeout=timeout, **kwargs)
            if result:
                self.logger.info(f"Generated {len(result['text'])} characters")
                return result
            else:
                self.logger.error("Prompt processing failed")
                return None
                
        except Exception as e:
            self.logger.error(f"Prompt processing failed: {e}")
            return None
    
    def step5_format_validate(self, code: str, language: str = "python") -> Dict[str, Any]:
        """Step 5: Format and validate code"""
        self.logger.info("=== Step 5: Formatting and validating code ===")
        
        try:
            result = self.code_processor.process_code(code, language)
            if result["success"]:
                self.logger.info("Code formatting and validation successful")
            else:
                self.logger.warning("Code validation failed")
            return result
        except Exception as e:
            self.logger.error(f"Code processing failed: {e}")
            return {"success": False, "error": str(e)}
    
    def step6_cleanup(self):
        """Step 6: Stop server and clean resources"""
        self.logger.info("=== Step 6: Cleaning up resources ===")
        self.cleanup()
    
    def cleanup(self):
        """Complete cleanup of all resources"""
        try:
            # Stop server
            if self.server_manager:
                self.server_manager.stop()
                self.server_manager = None
            
            # Cleanup resources
            self.resource_manager.cleanup_all()
            
            self.logger.info("Cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Cleanup error: {e}")
    
    def run_pipeline(self, prompt: str, language: str = "python", timeout: int = 120, **prompt_kwargs) -> Dict[str, Any]:
        """Run the complete pipeline"""
        self.logger.info("Starting TestGenie pipeline...")
        self.running = True
        
        # Start resource monitoring
        self.resource_manager.start_monitoring()
        
        pipeline_result = {
            "success": False,
            "steps_completed": [],
            "generated_code": "",
            "formatted_code": "",
            "validation": {},
            "errors": []
        }
        
        try:
            # Step 1: Download model
            if not self.step1_download_model():
                pipeline_result["errors"].append("Model download failed")
                return pipeline_result
            pipeline_result["steps_completed"].append("download_model")
            
            # Step 2: Install runtime
            if not self.step2_install_runtime():
                pipeline_result["errors"].append("Runtime installation failed")
                return pipeline_result
            pipeline_result["steps_completed"].append("install_runtime")
            
            # Step 3: Start server
            if not self.step3_start_server():
                pipeline_result["errors"].append("Server startup failed")
                return pipeline_result
            pipeline_result["steps_completed"].append("start_server")
            
            # Step 4: Send prompt
            generation_result = self.step4_send_prompt(prompt, timeout=timeout, **prompt_kwargs)
            if not generation_result:
                pipeline_result["errors"].append("Prompt processing failed")
                return pipeline_result
            pipeline_result["steps_completed"].append("send_prompt")
            pipeline_result["generated_code"] = generation_result["text"]
            
            # Step 5: Format and validate
            formatting_result = self.step5_format_validate(
                generation_result["text"], 
                language
            )
            pipeline_result["steps_completed"].append("format_validate")
            pipeline_result["formatted_code"] = formatting_result.get("formatted_code", "")
            pipeline_result["validation"] = formatting_result.get("validation", {})
            
            # Check if all steps completed successfully
            pipeline_result["success"] = (
                len(pipeline_result["steps_completed"]) == 5 and
                len(pipeline_result["errors"]) == 0
            )
            
            self.logger.info("Pipeline completed successfully")
            
        except Exception as e:
            self.logger.error(f"Pipeline error: {e}")
            pipeline_result["errors"].append(str(e))
        
        finally:
            # Step 6: Cleanup
            self.step6_cleanup()
            pipeline_result["steps_completed"].append("cleanup")
        
        return pipeline_result
    
    def run_interactive(self):
        """Run in interactive mode"""
        self.logger.info("Starting interactive mode...")
        
        # Initialize pipeline
        if not self.step1_download_model():
            return
        if not self.step2_install_runtime():
            return
        if not self.step3_start_server():
            return
        
        self.running = True
        self.resource_manager.start_monitoring()
        
        try:
            while self.running:
                print("\n" + "="*50)
                print("TestGenie Interactive Mode")
                print("="*50)
                print("Commands:")
                print("  generate <prompt> - Generate code")
                print("  test <code> - Generate test cases")
                print("  status - Show system status")
                print("  quit - Exit")
                print("="*50)
                
                command = input("Enter command: ").strip()
                
                if command.lower() == "quit":
                    break
                elif command.lower() == "status":
                    status = self.resource_manager.get_status()
                    print(f"CPU: {status['system_metrics']['cpu_percent']:.1f}%")
                    print(f"Memory: {status['system_metrics']['memory_percent']:.1f}%")
                    print(f"Server running: {self.server_manager.is_running() if self.server_manager else False}")
                elif command.startswith("generate "):
                    prompt = command[9:].strip()
                    if prompt:
                        result = self.step4_send_prompt(prompt)
                        if result:
                            formatted = self.step5_format_validate(result["text"])
                            print("\nGenerated Code:")
                            print("-" * 30)
                            print(formatted.get("formatted_code", result["text"]))
                elif command.startswith("test "):
                    code = command[5:].strip()
                    if code and self.prompt_handler:
                        test_cases = self.prompt_handler.generate_test_cases(code)
                        if test_cases:
                            print("\nGenerated Test Cases:")
                            print("-" * 30)
                            print(test_cases)
                else:
                    print("Unknown command")
        
        except KeyboardInterrupt:
            pass
        finally:
            self.cleanup()

def main():
    parser = argparse.ArgumentParser(description="TestGenie - AI Code Generation Pipeline")
    parser.add_argument("--model-url", default=MODEL_URL, 
                       help="URL to GGUF model file")
    parser.add_argument("--models-dir", default="./models", 
                       help="Directory to store models")
    parser.add_argument("--server-host", default="127.0.0.1", 
                       help="Server host")
    parser.add_argument("--server-port", type=int, default=8000, 
                       help="Server port")
    parser.add_argument("--prompt", help="Single prompt to process")
    parser.add_argument("--language", default="python", 
                       help="Programming language (python, cpp, java)")
    parser.add_argument("--interactive", action="store_true", 
                       help="Run in interactive mode")
    parser.add_argument("--max-tokens", type=int, default=512, 
                       help="Maximum tokens to generate")
    parser.add_argument("--temperature", type=float, default=0.7, 
                       help="Generation temperature")
    parser.add_argument("--timeout", type=int, default=120, 
                       help="Request timeout in seconds")
    
    args = parser.parse_args()
    
    # Create orchestrator
    orchestrator = TestGenieOrchestrator(
        model_url=args.model_url,
        models_dir=args.models_dir,
        server_host=args.server_host,
        server_port=args.server_port
    )
    
    try:
        if args.interactive:
            orchestrator.run_interactive()
        elif args.prompt:
            result = orchestrator.run_pipeline(
                prompt=args.prompt,
                language=args.language,
                max_tokens=args.max_tokens,
                temperature=args.temperature,
                timeout=args.timeout
            )
            
            if result["success"]:
                print("Pipeline completed successfully!")
                print("\nGenerated Code:")
                print("-" * 30)
                print(result["formatted_code"])
                
                if result["validation"].get("warnings"):
                    print("\nWarnings:")
                    for warning in result["validation"]["warnings"]:
                        print(f"  - {warning}")
            else:
                print("Pipeline failed!")
                for error in result["errors"]:
                    print(f"Error: {error}")
        else:
            print("Please provide --prompt or use --interactive mode")
            parser.print_help()
    
    except KeyboardInterrupt:
        print("\nShutting down...")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        orchestrator.cleanup()

if __name__ == "__main__":
    main()
