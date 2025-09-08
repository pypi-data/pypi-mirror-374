#!/usr/bin/env python3
"""
Model Downloader - Downloads GGUF models from storage
Optimized for CPU-only inference with minimal resource usage
"""

import os
import requests
import hashlib
from pathlib import Path
from typing import Optional
import logging

class ModelDownloader:
    def __init__(self, models_dir: str = "/models"):
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(exist_ok=True)
        self.logger = self._setup_logger()
        
    def _setup_logger(self):
        logger = logging.getLogger('ModelDownloader')
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger
    
    def download_model(self, model_url: str, filename: Optional[str] = None) -> str:
        """Download GGUF model with progress tracking and resume capability"""
        if not filename:
            if "drive.google.com" in model_url:
                filename = "model.gguf"  # Default filename for Google Drive
            else:
                filename = model_url.split('/')[-1]
            
        model_path = self.models_dir / filename
        
        # Check if already exists
        if model_path.exists():
            self.logger.info(f"Model {filename} already exists")
            return str(model_path)
            
        self.logger.info(f"Downloading {filename} from {model_url}")
        
        try:
            # Handle Google Drive URLs
            if "drive.google.com" in model_url:
                model_url = self._convert_google_drive_url(model_url)
            
            # Stream download with resume capability
            headers = {}
            if model_path.exists():
                headers['Range'] = f'bytes={model_path.stat().st_size}-'
                
            response = requests.get(model_url, headers=headers, stream=True)
            response.raise_for_status()
            
            mode = 'ab' if headers else 'wb'
            total_size = int(response.headers.get('content-length', 0))
            
            with open(model_path, mode) as f:
                downloaded = model_path.stat().st_size if headers else 0
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            progress = (downloaded / total_size) * 100
                            if downloaded % (1024 * 1024) == 0:  # Log every MB
                                self.logger.info(f"Downloaded {downloaded}/{total_size} bytes ({progress:.1f}%)")
                                
            self.logger.info(f"Successfully downloaded {filename}")
            return str(model_path)
            
        except Exception as e:
            self.logger.error(f"Failed to download {filename}: {e}")
            if model_path.exists():
                model_path.unlink()  # Clean up partial download
            raise
    
    def verify_model(self, model_path: str, expected_hash: Optional[str] = None) -> bool:
        """Verify model integrity"""
        if not expected_hash:
            return True
            
        self.logger.info("Verifying model integrity...")
        sha256_hash = hashlib.sha256()
        
        with open(model_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
                
        actual_hash = sha256_hash.hexdigest()
        is_valid = actual_hash == expected_hash
        
        if is_valid:
            self.logger.info("Model verification successful")
        else:
            self.logger.error(f"Model verification failed. Expected: {expected_hash}, Got: {actual_hash}")
            
        return is_valid
    
    def _convert_google_drive_url(self, url: str) -> str:
        """Convert Google Drive sharing URL to direct download URL"""
        try:
            # Extract file ID from Google Drive URL
            if "/file/d/" in url:
                file_id = url.split("/file/d/")[1].split("/")[0]
            else:
                raise ValueError("Invalid Google Drive URL format")
            
            # Convert to direct download URL
            direct_url = f"https://drive.google.com/uc?export=download&id={file_id}"
            
            self.logger.info(f"Converted Google Drive URL to direct download URL")
            return direct_url
            
        except Exception as e:
            self.logger.error(f"Failed to convert Google Drive URL: {e}")
            return url

if __name__ == "__main__":
    downloader = ModelDownloader()
    # Example usage
    # model_path = downloader.download_model("<LINK_TO_FILES>/model.gguf")
    # downloader.verify_model(model_path)
