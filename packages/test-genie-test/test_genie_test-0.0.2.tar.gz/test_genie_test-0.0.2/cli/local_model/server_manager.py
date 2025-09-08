#!/usr/bin/env python3
"""
Server Manager - Manages background GGUF inference server
Optimized for CPU-only inference with minimal resource usage
"""

import os
import time
import signal
import subprocess
import threading
import logging
import psutil
from pathlib import Path
from typing import Optional, Dict, Any
import requests
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import uvicorn
from llama_cpp import Llama

class GGUFServer:
    def __init__(self, model_path: str, host: str = "127.0.0.1", port: int = 8000):
        self.model_path = model_path
        self.host = host
        self.port = port
        self.llm: Optional[Llama] = None
        self.app = FastAPI(title="GGUF Inference Server")
        self.server_process: Optional[subprocess.Popen] = None
        self.logger = self._setup_logger()
        self._setup_routes()
        
    def _setup_logger(self):
        logger = logging.getLogger('GGUFServer')
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger
    
    def _setup_routes(self):
        @self.app.post("/generate")
        async def generate(prompt: Dict[str, Any]):
            try:
                if not self.llm:
                    return JSONResponse(
                        status_code=503, 
                        content={"error": "Model not loaded"}
                    )
                
                text = prompt.get("text", "")
                max_tokens = prompt.get("max_tokens", 512)
                temperature = prompt.get("temperature", 0.7)
                top_p = prompt.get("top_p", 0.9)
                
                # Generate response
                response = self.llm(
                    text,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    top_p=top_p,
                    echo=False,
                    stop=["</s>", "```", "---", "\n\n\n\n"]
                )
                
                return JSONResponse(content={
                    "text": response["choices"][0]["text"],
                    "usage": response.get("usage", {})
                })
                
            except Exception as e:
                self.logger.error(f"Generation error: {e}")
                return JSONResponse(
                    status_code=500,
                    content={"error": str(e)}
                )
        
        @self.app.get("/health")
        async def health():
            return JSONResponse(content={
                "status": "healthy" if self.llm else "loading",
                "model_loaded": self.llm is not None
            })
    
    def load_model(self):
        """Load GGUF model with CPU optimization"""
        try:
            self.logger.info(f"Loading model: {self.model_path}")
            
            # CPU-optimized parameters
            self.llm = Llama(
                model_path=self.model_path,
                n_ctx=4096,  # Larger context window
                n_threads=os.cpu_count(),  # Use all CPU cores
                n_gpu_layers=0,  # CPU-only
                verbose=False,
                use_mmap=True,  # Memory mapping for efficiency
                use_mlock=False,  # Don't lock memory
                low_vram=False,  # Not applicable for CPU
                f16_kv=True,  # Use 16-bit for key-value cache
                logits_all=False,  # Only compute logits for last token
                embedding=False,  # Disable embeddings
                offload_kqv=False,  # Keep everything in memory
                last_n_tokens_size=512,  # Larger cache for better context
                batch_size=512,  # Batch size for processing
                n_batch=512,  # Number of tokens to process in parallel
                seed=-1,  # Random seed
                n_parts=1,  # Number of model parts
                rope_freq_base=10000.0,
                rope_freq_scale=1.0,
                mul_mat_q=True,  # Use quantized matrix multiplication
                ftype=None,  # Auto-detect quantization type
                typical_p=1.0,
                repeat_penalty=1.05,  # Lower penalty for better code generation
                repeat_last_n=512,  # Larger context for repetition
                penalize_nl=False,  # Allow newlines in code
                stop=None,  # No stop tokens during model loading
                stream=False
            )
            
            self.logger.info("Model loaded successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to load model: {e}")
            raise
    
    def start_server(self):
        """Start the FastAPI server in background"""
        try:
            self.logger.info("Starting GGUF inference server...")
            
            # Load model first
            self.load_model()
            
            # Start server in background thread
            def run_server():
                uvicorn.run(
                    self.app,
                    host=self.host,
                    port=self.port,
                    log_level="warning",  # Reduce logging
                    access_log=False,  # Disable access logs
                    loop="asyncio"
                )
            
            server_thread = threading.Thread(target=run_server, daemon=True)
            server_thread.start()
            
            # Wait for server to be ready
            max_retries = 30
            for i in range(max_retries):
                try:
                    response = requests.get(f"http://{self.host}:{self.port}/health", timeout=1)
                    if response.status_code == 200:
                        self.logger.info(f"Server started successfully on {self.host}:{self.port}")
                        return True
                except:
                    pass
                time.sleep(1)
            
            self.logger.error("Server failed to start within timeout")
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to start server: {e}")
            return False
    
    def stop_server(self):
        """Stop the server and cleanup resources"""
        try:
            self.logger.info("Stopping server...")
            
            # Clear model from memory
            if self.llm:
                del self.llm
                self.llm = None
            
            # Force garbage collection
            import gc
            gc.collect()
            
            self.logger.info("Server stopped and resources cleaned up")
            
        except Exception as e:
            self.logger.error(f"Error stopping server: {e}")

class ServerManager:
    def __init__(self, model_path: str, host: str = "127.0.0.1", port: int = 8000):
        self.server: Optional[GGUFServer] = None
        self.model_path = model_path
        self.host = host
        self.port = port
        self.logger = self._setup_logger()
        
    def _setup_logger(self):
        logger = logging.getLogger('ServerManager')
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger
    
    def start(self) -> bool:
        """Start the background server"""
        try:
            self.server = GGUFServer(self.model_path, self.host, self.port)
            return self.server.start_server()
        except Exception as e:
            self.logger.error(f"Failed to start server: {e}")
            return False
    
    def stop(self):
        """Stop the background server"""
        if self.server:
            self.server.stop_server()
            self.server = None
    
    def is_running(self) -> bool:
        """Check if server is running"""
        try:
            response = requests.get(f"http://{self.host}:{self.port}/health", timeout=1)
            return response.status_code == 200
        except:
            return False
    
    def get_server_url(self) -> str:
        """Get server URL"""
        return f"http://{self.host}:{self.port}"

if __name__ == "__main__":
    # Example usage
    manager = ServerManager("/models/model.gguf")
    if manager.start():
        print("Server started successfully")
        time.sleep(10)  # Keep running for demo
        manager.stop()
    else:
        print("Failed to start server")
