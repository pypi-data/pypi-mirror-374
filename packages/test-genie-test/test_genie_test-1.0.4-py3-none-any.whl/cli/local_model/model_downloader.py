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
                # Use special Google Drive handler
                if self._handle_google_drive_download(model_url, model_path):
                    return str(model_path)
                else:
                    raise Exception("Google Drive download failed")
            else:
                # Regular download for non-Google Drive URLs
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
    
    def _handle_google_drive_download(self, url: str, model_path: Path) -> bool:
        """Handle Google Drive download with confirmation page"""
        try:
            # First request to get the confirmation page
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            # Check if we got the confirmation page
            if "Virus scan warning" in response.text or "download anyway" in response.text.lower():
                self.logger.info("Google Drive confirmation page detected, handling...")
                
                # Extract form parameters from the confirmation page
                import re
                
                # Extract the form action URL
                action_match = re.search(r'action="([^"]*)"', response.text)
                if not action_match:
                    self.logger.error("Could not find form action in response")
                    return False
                
                action_url = action_match.group(1)
                self.logger.info(f"Found form action URL: {action_url}")
                
                # Extract form parameters
                id_match = re.search(r'name="id"\s+value="([^"]*)"', response.text)
                export_match = re.search(r'name="export"\s+value="([^"]*)"', response.text)
                confirm_match = re.search(r'name="confirm"\s+value="([^"]*)"', response.text)
                uuid_match = re.search(r'name="uuid"\s+value="([^"]*)"', response.text)
                
                if not all([id_match, export_match, confirm_match, uuid_match]):
                    self.logger.error("Could not extract all form parameters")
                    return False
                
                # Prepare the confirmation request
                confirm_data = {
                    'id': id_match.group(1),
                    'export': export_match.group(1),
                    'confirm': confirm_match.group(1),
                    'uuid': uuid_match.group(1)
                }
                
                self.logger.info("Making confirmation request...")
                
                # Make the confirmation request (GET request with parameters)
                confirm_response = requests.get(action_url, params=confirm_data, stream=True)
                confirm_response.raise_for_status()
                
                # Now download the actual file
                return self._download_file_stream(confirm_response, model_path)
            else:
                # Direct download without confirmation
                return self._download_file_stream(response, model_path)
                
        except Exception as e:
            self.logger.error(f"Failed to handle Google Drive download: {e}")
            return False
    
    def _download_file_stream(self, response: requests.Response, model_path: Path) -> bool:
        """Download file from response stream"""
        try:
            total_size = int(response.headers.get('content-length', 0))
            
            with open(model_path, 'wb') as f:
                downloaded = 0
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            progress = (downloaded / total_size) * 100
                            if downloaded % (1024 * 1024) == 0:  # Log every MB
                                self.logger.info(f"Downloaded {downloaded}/{total_size} bytes ({progress:.1f}%)")
            
            self.logger.info(f"Successfully downloaded {model_path.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to download file stream: {e}")
            return False

if __name__ == "__main__":
    downloader = ModelDownloader()
    # Example usage
    # model_path = downloader.download_model("<LINK_TO_FILES>/model.gguf")
    # downloader.verify_model(model_path)
