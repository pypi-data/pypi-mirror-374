#!/usr/bin/env python3
"""
Resource Manager - Manages cleanup and resource monitoring
Optimized for CPU-only inference with minimal resource usage
"""

import os
import psutil
import time
import signal
import logging
import threading
import subprocess
from typing import Dict, Any, List, Optional
from pathlib import Path
import gc

class ResourceMonitor:
    def __init__(self):
        self.logger = self._setup_logger()
        self.monitoring = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.metrics = {
            "cpu_percent": 0.0,
            "memory_percent": 0.0,
            "memory_used_mb": 0.0,
            "disk_usage_percent": 0.0,
            "process_count": 0
        }
        
    def _setup_logger(self):
        logger = logging.getLogger('ResourceMonitor')
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger
    
    def get_current_metrics(self) -> Dict[str, Any]:
        """Get current system resource metrics"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=0.1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_used_mb = memory.used / (1024 * 1024)
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_usage_percent = (disk.used / disk.total) * 100
            
            # Process count
            process_count = len(psutil.pids())
            
            self.metrics = {
                "cpu_percent": cpu_percent,
                "memory_percent": memory_percent,
                "memory_used_mb": memory_used_mb,
                "disk_usage_percent": disk_usage_percent,
                "process_count": process_count,
                "timestamp": time.time()
            }
            
            return self.metrics
            
        except Exception as e:
            self.logger.error(f"Failed to get metrics: {e}")
            return self.metrics
    
    def start_monitoring(self, interval: float = 5.0):
        """Start continuous resource monitoring"""
        if self.monitoring:
            return
            
        self.monitoring = True
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop,
            args=(interval,),
            daemon=True
        )
        self.monitor_thread.start()
        self.logger.info("Resource monitoring started")
    
    def stop_monitoring(self):
        """Stop resource monitoring"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1.0)
        self.logger.info("Resource monitoring stopped")
    
    def _monitor_loop(self, interval: float):
        """Monitoring loop"""
        while self.monitoring:
            try:
                metrics = self.get_current_metrics()
                
                # Log warnings for high resource usage
                if metrics["cpu_percent"] > 80:
                    self.logger.warning(f"High CPU usage: {metrics['cpu_percent']:.1f}%")
                
                if metrics["memory_percent"] > 85:
                    self.logger.warning(f"High memory usage: {metrics['memory_percent']:.1f}%")
                
                if metrics["disk_usage_percent"] > 90:
                    self.logger.warning(f"High disk usage: {metrics['disk_usage_percent']:.1f}%")
                
                time.sleep(interval)
                
            except Exception as e:
                self.logger.error(f"Monitoring error: {e}")
                time.sleep(interval)

class ProcessManager:
    def __init__(self):
        self.logger = self._setup_logger()
        self.managed_processes: List[subprocess.Popen] = []
        
    def _setup_logger(self):
        logger = logging.getLogger('ProcessManager')
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger
    
    def add_process(self, process: subprocess.Popen):
        """Add a process to be managed"""
        self.managed_processes.append(process)
        self.logger.info(f"Added process {process.pid} to management")
    
    def kill_all_processes(self):
        """Kill all managed processes"""
        for process in self.managed_processes:
            try:
                if process.poll() is None:  # Process is still running
                    self.logger.info(f"Terminating process {process.pid}")
                    process.terminate()
                    
                    # Wait for graceful termination
                    try:
                        process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        self.logger.warning(f"Force killing process {process.pid}")
                        process.kill()
                        process.wait()
                        
            except Exception as e:
                self.logger.error(f"Error terminating process {process.pid}: {e}")
        
        self.managed_processes.clear()
        self.logger.info("All managed processes terminated")
    
    def cleanup_zombie_processes(self):
        """Clean up zombie processes"""
        try:
            # Remove completed processes from the list
            self.managed_processes = [
                p for p in self.managed_processes 
                if p.poll() is None
            ]
            
            # Kill any remaining zombie processes
            for proc in psutil.process_iter(['pid', 'name', 'status']):
                try:
                    if proc.info['status'] == psutil.STATUS_ZOMBIE:
                        self.logger.info(f"Cleaning up zombie process {proc.info['pid']}")
                        proc.kill()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
                    
        except Exception as e:
            self.logger.error(f"Error cleaning up zombie processes: {e}")

class MemoryManager:
    def __init__(self):
        self.logger = self._setup_logger()
        
    def _setup_logger(self):
        logger = logging.getLogger('MemoryManager')
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger
    
    def force_garbage_collection(self):
        """Force Python garbage collection"""
        try:
            collected = gc.collect()
            self.logger.info(f"Garbage collection freed {collected} objects")
        except Exception as e:
            self.logger.error(f"Garbage collection failed: {e}")
    
    def clear_python_cache(self):
        """Clear Python import cache"""
        try:
            # Clear sys.modules cache (be careful with this)
            import sys
            modules_to_remove = []
            for module_name in sys.modules:
                if module_name.startswith(('llama_cpp', 'torch', 'transformers')):
                    modules_to_remove.append(module_name)
            
            for module_name in modules_to_remove:
                del sys.modules[module_name]
            
            self.logger.info(f"Cleared {len(modules_to_remove)} modules from cache")
            
        except Exception as e:
            self.logger.error(f"Failed to clear Python cache: {e}")
    
    def get_memory_usage(self) -> Dict[str, float]:
        """Get current memory usage in MB"""
        try:
            process = psutil.Process()
            memory_info = process.memory_info()
            
            return {
                "rss_mb": memory_info.rss / (1024 * 1024),  # Resident Set Size
                "vms_mb": memory_info.vms / (1024 * 1024),  # Virtual Memory Size
                "percent": process.memory_percent()
            }
        except Exception as e:
            self.logger.error(f"Failed to get memory usage: {e}")
            return {"rss_mb": 0, "vms_mb": 0, "percent": 0}

class ResourceManager:
    """Main resource management class"""
    
    def __init__(self):
        self.monitor = ResourceMonitor()
        self.process_manager = ProcessManager()
        self.memory_manager = MemoryManager()
        self.logger = self._setup_logger()
        
    def _setup_logger(self):
        logger = logging.getLogger('ResourceManager')
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger
    
    def start_monitoring(self, interval: float = 5.0):
        """Start resource monitoring"""
        self.monitor.start_monitoring(interval)
    
    def stop_monitoring(self):
        """Stop resource monitoring"""
        self.monitor.stop_monitoring()
    
    def cleanup_all(self):
        """Perform complete cleanup"""
        self.logger.info("Starting complete cleanup...")
        
        # Stop monitoring
        self.stop_monitoring()
        
        # Kill all managed processes
        self.process_manager.kill_all_processes()
        
        # Clean up zombie processes
        self.process_manager.cleanup_zombie_processes()
        
        # Force garbage collection
        self.memory_manager.force_garbage_collection()
        
        # Clear Python cache
        self.memory_manager.clear_python_cache()
        
        # Final garbage collection
        self.memory_manager.force_garbage_collection()
        
        self.logger.info("Cleanup completed")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current resource status"""
        metrics = self.monitor.get_current_metrics()
        memory_usage = self.memory_manager.get_memory_usage()
        
        return {
            "system_metrics": metrics,
            "process_memory": memory_usage,
            "managed_processes": len(self.process_manager.managed_processes),
            "monitoring_active": self.monitor.monitoring
        }
    
    def add_process(self, process: subprocess.Popen):
        """Add a process to be managed"""
        self.process_manager.add_process(process)

if __name__ == "__main__":
    # Example usage
    manager = ResourceManager()
    
    # Start monitoring
    manager.start_monitoring(interval=2.0)
    
    try:
        # Simulate some work
        time.sleep(10)
        
        # Get status
        status = manager.get_status()
        print("Resource status:")
        print(f"CPU: {status['system_metrics']['cpu_percent']:.1f}%")
        print(f"Memory: {status['system_metrics']['memory_percent']:.1f}%")
        print(f"Process Memory: {status['process_memory']['rss_mb']:.1f} MB")
        
    finally:
        # Cleanup
        manager.cleanup_all()
