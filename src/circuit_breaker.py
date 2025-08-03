"""Circuit breaker pattern implementation for fault tolerance"""
import time
import logging
from typing import Callable, Any, Optional, TypeVar, Generic
from functools import wraps
from enum import Enum
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

T = TypeVar('T')


class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"  # Normal operation
    OPEN = "open"      # Failing, block calls
    HALF_OPEN = "half_open"  # Testing if service recovered


class CircuitBreaker(Generic[T]):
    """
    Circuit breaker to prevent cascading failures
    
    The circuit breaker has three states:
    - CLOSED: Normal operation, requests pass through
    - OPEN: Service is failing, requests are blocked
    - HALF_OPEN: Testing if service has recovered
    """
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        expected_exception: type[Exception] = Exception
    ) -> None:
        """
        Initialize circuit breaker
        
        Args:
            failure_threshold: Number of failures before opening circuit
            recovery_timeout: Seconds to wait before attempting recovery
            expected_exception: Exception type to catch
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        
        self.failure_count: int = 0
        self.last_failure_time: Optional[datetime] = None
        self.state: CircuitState = CircuitState.CLOSED
    
    def call(self, func: Callable[..., T], *args: Any, **kwargs: Any) -> T:
        """
        Call function through circuit breaker
        
        Args:
            func: Function to call
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Function result
            
        Raises:
            Exception: If circuit is open or function fails
        """
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
                logger.info("Circuit breaker entering HALF_OPEN state")
            else:
                raise Exception(
                    f"Circuit breaker is OPEN. Service unavailable. "
                    f"Retry after {self._time_until_retry()} seconds"
                )
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exception as e:
            self._on_failure()
            raise
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset"""
        if self.last_failure_time is None:
            return False
        
        return datetime.now() >= (
            self.last_failure_time + timedelta(seconds=self.recovery_timeout)
        )
    
    def _time_until_retry(self) -> int:
        """Calculate seconds until retry is allowed"""
        if self.last_failure_time is None:
            return 0
        
        retry_time = (
            self.last_failure_time + timedelta(seconds=self.recovery_timeout)
        )
        remaining = (retry_time - datetime.now()).total_seconds()
        return max(0, int(remaining))
    
    def _on_success(self) -> None:
        """Handle successful call"""
        if self.state == CircuitState.HALF_OPEN:
            logger.info("Circuit breaker closing after successful test")
        
        self.failure_count = 0
        self.state = CircuitState.CLOSED
    
    def _on_failure(self) -> None:
        """Handle failed call"""
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            logger.warning(
                f"Circuit breaker opened after {self.failure_count} failures"
            )
        elif self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.OPEN
            logger.warning("Circuit breaker reopened after test failure")


def circuit_breaker(
    failure_threshold: int = 5,
    recovery_timeout: int = 60,
    expected_exception: type[Exception] = Exception
) -> Callable:
    """
    Decorator to apply circuit breaker pattern
    
    Args:
        failure_threshold: Number of failures before opening circuit
        recovery_timeout: Seconds to wait before attempting recovery
        expected_exception: Exception type to catch
        
    Returns:
        Decorated function with circuit breaker
    """
    breaker: CircuitBreaker[Any] = CircuitBreaker(
        failure_threshold=failure_threshold,
        recovery_timeout=recovery_timeout,
        expected_exception=expected_exception
    )
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            return breaker.call(func, *args, **kwargs)
        
        # Expose breaker for monitoring
        wrapper.circuit_breaker = breaker  # type: ignore
        return wrapper
    
    return decorator


class SmartCircuitBreaker(CircuitBreaker[T]):
    """
    Enhanced circuit breaker with adaptive behavior
    """
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        expected_exception: type[Exception] = Exception,
        success_threshold: int = 3
    ) -> None:
        super().__init__(failure_threshold, recovery_timeout, expected_exception)
        self.success_threshold = success_threshold
        self.success_count: int = 0
        self.consecutive_failures: int = 0
    
    def _on_success(self) -> None:
        """Handle successful call with gradual recovery"""
        self.consecutive_failures = 0
        
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.success_threshold:
                logger.info(
                    f"Circuit breaker closing after {self.success_count} "
                    f"successful tests"
                )
                self.state = CircuitState.CLOSED
                self.failure_count = 0
                self.success_count = 0
        else:
            self.failure_count = max(0, self.failure_count - 1)
    
    def _on_failure(self) -> None:
        """Handle failed call with consecutive failure tracking"""
        self.consecutive_failures += 1
        self.success_count = 0
        
        super()._on_failure()
        
        # Open immediately on consecutive failures in HALF_OPEN
        if (self.state == CircuitState.HALF_OPEN and 
            self.consecutive_failures >= 2):
            self.state = CircuitState.OPEN
            logger.warning(
                "Circuit breaker opened due to consecutive failures in "
                "HALF_OPEN state"
            )