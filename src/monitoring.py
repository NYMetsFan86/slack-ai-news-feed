"""Memory and performance monitoring utilities"""
import os
import psutil
import logging
import gc
from typing import Dict, Any, Optional, Callable
from functools import wraps
from datetime import datetime

logger = logging.getLogger(__name__)


class MemoryMonitor:
    """Monitor memory usage and prevent OOM errors"""
    
    def __init__(self, threshold_percent: float = 80.0) -> None:
        """
        Initialize memory monitor
        
        Args:
            threshold_percent: Memory usage threshold percentage
        """
        self.threshold_percent = threshold_percent
        self.process = psutil.Process(os.getpid())
        self.start_memory = self.get_memory_info()
        logger.info(f"Memory monitor initialized. Start memory: {self.start_memory['rss_mb']:.1f} MB")
    
    def get_memory_info(self) -> Dict[str, Any]:
        """Get current memory usage information"""
        memory_info = self.process.memory_info()
        memory_percent = self.process.memory_percent()
        
        return {
            "rss_mb": memory_info.rss / 1024 / 1024,  # Resident Set Size in MB
            "vms_mb": memory_info.vms / 1024 / 1024,  # Virtual Memory Size in MB
            "percent": memory_percent,
            "available_mb": psutil.virtual_memory().available / 1024 / 1024,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def check_memory_usage(self) -> bool:
        """
        Check if memory usage is within safe limits
        
        Returns:
            True if memory usage is safe, False if approaching limit
        """
        memory_info = self.get_memory_info()
        
        if memory_info["percent"] > self.threshold_percent:
            logger.warning(
                f"High memory usage detected: {memory_info['percent']:.1f}% "
                f"(RSS: {memory_info['rss_mb']:.1f} MB)"
            )
            return False
        
        return True
    
    def log_memory_stats(self, label: str = "") -> None:
        """Log current memory statistics"""
        memory_info = self.get_memory_info()
        memory_delta = memory_info["rss_mb"] - self.start_memory["rss_mb"]
        
        logger.info(
            f"Memory stats {label}: RSS={memory_info['rss_mb']:.1f}MB "
            f"(+{memory_delta:.1f}MB), {memory_info['percent']:.1f}% used, "
            f"Available={memory_info['available_mb']:.1f}MB"
        )
    
    def force_garbage_collection(self) -> None:
        """Force garbage collection to free memory"""
        before = self.get_memory_info()
        gc.collect()
        after = self.get_memory_info()
        
        freed = before["rss_mb"] - after["rss_mb"]
        if freed > 0:
            logger.info(f"Garbage collection freed {freed:.1f} MB")


def monitor_memory(threshold_percent: float = 80.0) -> Callable:
    """
    Decorator to monitor memory usage during function execution
    
    Args:
        threshold_percent: Memory usage threshold percentage
        
    Returns:
        Decorated function with memory monitoring
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            monitor = MemoryMonitor(threshold_percent)
            
            # Log memory before execution
            monitor.log_memory_stats(f"before {func.__name__}")
            
            try:
                # Check if we have enough memory to proceed
                if not monitor.check_memory_usage():
                    monitor.force_garbage_collection()
                    if not monitor.check_memory_usage():
                        logger.error(
                            f"Memory usage too high to execute {func.__name__}"
                        )
                        raise MemoryError(
                            "Insufficient memory to continue processing"
                        )
                
                # Execute function
                result = func(*args, **kwargs)
                
                # Log memory after execution
                monitor.log_memory_stats(f"after {func.__name__}")
                
                return result
                
            except MemoryError:
                # Try to recover from memory errors
                logger.error("Memory error occurred, attempting cleanup")
                monitor.force_garbage_collection()
                raise
                
        return wrapper
    return decorator


class ResourceGuard:
    """Context manager for resource-intensive operations"""
    
    def __init__(
        self,
        operation_name: str,
        memory_threshold: float = 85.0,
        cleanup_on_exit: bool = True
    ) -> None:
        """
        Initialize resource guard
        
        Args:
            operation_name: Name of the operation for logging
            memory_threshold: Memory usage threshold percentage
            cleanup_on_exit: Whether to force GC on exit
        """
        self.operation_name = operation_name
        self.memory_threshold = memory_threshold
        self.cleanup_on_exit = cleanup_on_exit
        self.monitor = MemoryMonitor(memory_threshold)
        self.start_time: Optional[float] = None
    
    def __enter__(self) -> "ResourceGuard":
        """Enter resource-guarded context"""
        import time
        self.start_time = time.time()
        
        logger.info(f"Starting resource-intensive operation: {self.operation_name}")
        self.monitor.log_memory_stats("at start")
        
        # Check if we have enough memory
        if not self.monitor.check_memory_usage():
            self.monitor.force_garbage_collection()
            if not self.monitor.check_memory_usage():
                raise MemoryError(
                    f"Insufficient memory to start {self.operation_name}"
                )
        
        return self
    
    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit resource-guarded context"""
        import time
        elapsed = time.time() - (self.start_time or 0)
        
        self.monitor.log_memory_stats("at end")
        logger.info(
            f"Completed {self.operation_name} in {elapsed:.2f}s"
        )
        
        if self.cleanup_on_exit:
            self.monitor.force_garbage_collection()


# Try to import psutil, provide fallback if not available
try:
    import psutil
except ImportError:
    logger.warning("psutil not available, memory monitoring disabled")
    
    # Provide no-op implementations
    class MemoryMonitor:  # type: ignore
        def __init__(self, threshold_percent: float = 80.0) -> None:
            pass
        
        def get_memory_info(self) -> Dict[str, Any]:
            return {
                "rss_mb": 0,
                "vms_mb": 0,
                "percent": 0,
                "available_mb": 0,
                "timestamp": datetime.utcnow().isoformat()
            }
        
        def check_memory_usage(self) -> bool:
            return True
        
        def log_memory_stats(self, label: str = "") -> None:
            pass
        
        def force_garbage_collection(self) -> None:
            gc.collect()
    
    def monitor_memory(threshold_percent: float = 80.0) -> Callable:
        """No-op decorator when psutil not available"""
        def decorator(func: Callable) -> Callable:
            return func
        return decorator
    
    class ResourceGuard:  # type: ignore
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            pass
        
        def __enter__(self) -> "ResourceGuard":
            return self
        
        def __exit__(self, *args: Any) -> None:
            pass