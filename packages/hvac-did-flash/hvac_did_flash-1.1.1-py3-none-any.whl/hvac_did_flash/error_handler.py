"""
Error handling and retry mechanism module for STM32 programming system.

This module provides functionality to handle errors and implement retry logic
for failed operations with exponential backoff.
"""

import time
import logging
from functools import wraps
from typing import Callable, Any, Optional, Dict, List, Tuple
import random
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ErrorType(Enum):
    """Enumeration of error types."""
    ST_LINK_CONNECTION = "st_link_connection"
    PROGRAMMING = "programming"
    SERIAL_COMMUNICATION = "serial_communication"
    FILE_OPERATION = "file_operation"
    VERIFICATION = "verification"
    UNKNOWN = "unknown"


class RetryStrategy(Enum):
    """Enumeration of retry strategies."""
    EXPONENTIAL_BACKOFF = "exponential_backoff"
    LINEAR_BACKOFF = "linear_backoff"
    FIXED_DELAY = "fixed_delay"
    RANDOM_BACKOFF = "random_backoff"


def retry_with_backoff(max_retries: int = 3, initial_wait: float = 1.0, 
                      backoff_factor: float = 2.0, max_wait: float = 60.0,
                      strategy: RetryStrategy = RetryStrategy.EXPONENTIAL_BACKOFF,
                      exceptions: Tuple = (Exception,)):
    """
    Decorator for retrying functions with exponential backoff.
    
    Args:
        max_retries (int): Maximum number of retry attempts
        initial_wait (float): Initial wait time in seconds
        backoff_factor (float): Factor to multiply wait time by after each retry
        max_wait (float): Maximum wait time between retries
        strategy (RetryStrategy): Retry strategy to use
        exceptions (Tuple): Tuple of exceptions to catch and retry on
        
    Returns:
        Callable: Decorated function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt == max_retries:
                        logger.error(f"Function {func.__name__} failed after {max_retries} retries: {e}")
                        raise e
                    
                    wait_time = _calculate_wait_time(attempt, initial_wait, backoff_factor, 
                                                  max_wait, strategy)
                    
                    logger.warning(f"Function {func.__name__} failed (attempt {attempt + 1}/{max_retries + 1}): {e}")
                    logger.info(f"Retrying in {wait_time:.2f} seconds...")
                    
                    time.sleep(wait_time)
            
            # This should never be reached, but just in case
            raise last_exception
        
        return wrapper
    return decorator


def _calculate_wait_time(attempt: int, initial_wait: float, backoff_factor: float,
                        max_wait: float, strategy: RetryStrategy) -> float:
    """
    Calculate wait time based on retry strategy.
    
    Args:
        attempt (int): Current attempt number (0-based)
        initial_wait (float): Initial wait time
        backoff_factor (float): Backoff factor
        max_wait (float): Maximum wait time
        strategy (RetryStrategy): Retry strategy
        
    Returns:
        float: Wait time in seconds
    """
    if strategy == RetryStrategy.EXPONENTIAL_BACKOFF:
        wait_time = initial_wait * (backoff_factor ** attempt)
    elif strategy == RetryStrategy.LINEAR_BACKOFF:
        wait_time = initial_wait * (1 + attempt)
    elif strategy == RetryStrategy.FIXED_DELAY:
        wait_time = initial_wait
    elif strategy == RetryStrategy.RANDOM_BACKOFF:
        base_wait = initial_wait * (backoff_factor ** attempt)
        wait_time = base_wait + random.uniform(0, base_wait * 0.5)
    else:
        wait_time = initial_wait
    
    return min(wait_time, max_wait)


class ErrorHandler:
    """Class to handle different types of errors and recovery strategies."""
    
    def __init__(self):
        """Initialize the error handler."""
        self.error_counts = {}
        self.recovery_attempts = {}
    
    def handle_st_link_error(self, error: Exception, context: Optional[Dict[str, Any]] = None) -> bool:
        """
        Handle ST-Link specific errors.
        
        Args:
            error (Exception): The error that occurred
            context (Optional[Dict[str, Any]]): Additional context information
            
        Returns:
            bool: True if error was handled successfully, False otherwise
        """
        error_type = ErrorType.ST_LINK_CONNECTION
        self._increment_error_count(error_type)
        
        logger.error(f"ST-Link error occurred: {error}")
        
        try:
            # Common ST-Link error recovery strategies
            if "connection" in str(error).lower():
                logger.info("Attempting ST-Link connection recovery...")
                return self._recover_st_link_connection(context)
            elif "timeout" in str(error).lower():
                logger.info("Attempting ST-Link timeout recovery...")
                return self._recover_st_link_timeout(context)
            elif "device not found" in str(error).lower():
                logger.info("Attempting ST-Link device recovery...")
                return self._recover_st_link_device(context)
            else:
                logger.warning("Unknown ST-Link error type, attempting generic recovery...")
                return self._recover_st_link_generic(context)
                
        except Exception as recovery_error:
            logger.error(f"Error during ST-Link recovery: {recovery_error}")
            return False
    
    def handle_programming_error(self, error: Exception, context: Optional[Dict[str, Any]] = None) -> bool:
        """
        Handle programming-related errors.
        
        Args:
            error (Exception): The error that occurred
            context (Optional[Dict[str, Any]]): Additional context information
            
        Returns:
            bool: True if error was handled successfully, False otherwise
        """
        error_type = ErrorType.PROGRAMMING
        self._increment_error_count(error_type)
        
        logger.error(f"Programming error occurred: {error}")
        
        try:
            # Common programming error recovery strategies
            if "verification" in str(error).lower():
                logger.info("Attempting programming verification recovery...")
                return self._recover_programming_verification(context)
            elif "memory" in str(error).lower():
                logger.info("Attempting programming memory recovery...")
                return self._recover_programming_memory(context)
            elif "timeout" in str(error).lower():
                logger.info("Attempting programming timeout recovery...")
                return self._recover_programming_timeout(context)
            else:
                logger.warning("Unknown programming error type, attempting generic recovery...")
                return self._recover_programming_generic(context)
                
        except Exception as recovery_error:
            logger.error(f"Error during programming recovery: {recovery_error}")
            return False
    
    def handle_serial_communication_error(self, error: Exception, context: Optional[Dict[str, Any]] = None) -> bool:
        """
        Handle serial communication errors.
        
        Args:
            error (Exception): The error that occurred
            context (Optional[Dict[str, Any]]): Additional context information
            
        Returns:
            bool: True if error was handled successfully, False otherwise
        """
        error_type = ErrorType.SERIAL_COMMUNICATION
        self._increment_error_count(error_type)
        
        logger.error(f"Serial communication error occurred: {error}")
        
        try:
            # Common serial communication error recovery strategies
            if "port" in str(error).lower():
                logger.info("Attempting serial port recovery...")
                return self._recover_serial_port(context)
            elif "timeout" in str(error).lower():
                logger.info("Attempting serial timeout recovery...")
                return self._recover_serial_timeout(context)
            elif "permission" in str(error).lower():
                logger.info("Attempting serial permission recovery...")
                return self._recover_serial_permission(context)
            else:
                logger.warning("Unknown serial communication error type, attempting generic recovery...")
                return self._recover_serial_generic(context)
                
        except Exception as recovery_error:
            logger.error(f"Error during serial communication recovery: {recovery_error}")
            return False
    
    def _increment_error_count(self, error_type: ErrorType) -> None:
        """Increment error count for the given error type."""
        if error_type not in self.error_counts:
            self.error_counts[error_type] = 0
        self.error_counts[error_type] += 1
    
    def _increment_recovery_attempts(self, error_type: ErrorType) -> None:
        """Increment recovery attempts for the given error type."""
        if error_type not in self.recovery_attempts:
            self.recovery_attempts[error_type] = 0
        self.recovery_attempts[error_type] += 1
    
    # ST-Link recovery methods
    def _recover_st_link_connection(self, context: Optional[Dict[str, Any]]) -> bool:
        """Recover from ST-Link connection errors."""
        logger.info("Attempting ST-Link connection recovery...")
        time.sleep(2)  # Wait before retry
        return True  # Placeholder implementation
    
    def _recover_st_link_timeout(self, context: Optional[Dict[str, Any]]) -> bool:
        """Recover from ST-Link timeout errors."""
        logger.info("Attempting ST-Link timeout recovery...")
        time.sleep(5)  # Longer wait for timeout
        return True  # Placeholder implementation
    
    def _recover_st_link_device(self, context: Optional[Dict[str, Any]]) -> bool:
        """Recover from ST-Link device not found errors."""
        logger.info("Attempting ST-Link device recovery...")
        time.sleep(3)  # Wait for device to be ready
        return True  # Placeholder implementation
    
    def _recover_st_link_generic(self, context: Optional[Dict[str, Any]]) -> bool:
        """Generic ST-Link error recovery."""
        logger.info("Attempting generic ST-Link recovery...")
        time.sleep(2)
        return True  # Placeholder implementation
    
    # Programming recovery methods
    def _recover_programming_verification(self, context: Optional[Dict[str, Any]]) -> bool:
        """Recover from programming verification errors."""
        logger.info("Attempting programming verification recovery...")
        time.sleep(1)
        return True  # Placeholder implementation
    
    def _recover_programming_memory(self, context: Optional[Dict[str, Any]]) -> bool:
        """Recover from programming memory errors."""
        logger.info("Attempting programming memory recovery...")
        time.sleep(2)
        return True  # Placeholder implementation
    
    def _recover_programming_timeout(self, context: Optional[Dict[str, Any]]) -> bool:
        """Recover from programming timeout errors."""
        logger.info("Attempting programming timeout recovery...")
        time.sleep(3)
        return True  # Placeholder implementation
    
    def _recover_programming_generic(self, context: Optional[Dict[str, Any]]) -> bool:
        """Generic programming error recovery."""
        logger.info("Attempting generic programming recovery...")
        time.sleep(2)
        return True  # Placeholder implementation
    
    # Serial communication recovery methods
    def _recover_serial_port(self, context: Optional[Dict[str, Any]]) -> bool:
        """Recover from serial port errors."""
        logger.info("Attempting serial port recovery...")
        time.sleep(1)
        return True  # Placeholder implementation
    
    def _recover_serial_timeout(self, context: Optional[Dict[str, Any]]) -> bool:
        """Recover from serial timeout errors."""
        logger.info("Attempting serial timeout recovery...")
        time.sleep(2)
        return True  # Placeholder implementation
    
    def _recover_serial_permission(self, context: Optional[Dict[str, Any]]) -> bool:
        """Recover from serial permission errors."""
        logger.info("Attempting serial permission recovery...")
        time.sleep(1)
        return True  # Placeholder implementation
    
    def _recover_serial_generic(self, context: Optional[Dict[str, Any]]) -> bool:
        """Generic serial communication error recovery."""
        logger.info("Attempting generic serial communication recovery...")
        time.sleep(1)
        return True  # Placeholder implementation
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """
        Get error handling statistics.
        
        Returns:
            Dict[str, Any]: Error statistics
        """
        return {
            'error_counts': dict(self.error_counts),
            'recovery_attempts': dict(self.recovery_attempts),
            'total_errors': sum(self.error_counts.values()),
            'total_recovery_attempts': sum(self.recovery_attempts.values())
        }
    
    def reset_statistics(self) -> None:
        """Reset error handling statistics."""
        self.error_counts.clear()
        self.recovery_attempts.clear()
        logger.info("Error handling statistics reset")


class RetryManager:
    """Manager class for handling retry operations with different strategies."""
    
    def __init__(self, error_handler: Optional[ErrorHandler] = None):
        """
        Initialize the retry manager.
        
        Args:
            error_handler (Optional[ErrorHandler]): Error handler instance
        """
        self.error_handler = error_handler or ErrorHandler()
        self.retry_configs = {}
    
    def configure_retry(self, operation_name: str, max_retries: int = 3,
                       initial_wait: float = 1.0, backoff_factor: float = 2.0,
                       strategy: RetryStrategy = RetryStrategy.EXPONENTIAL_BACKOFF) -> None:
        """
        Configure retry parameters for a specific operation.
        
        Args:
            operation_name (str): Name of the operation
            max_retries (int): Maximum number of retries
            initial_wait (float): Initial wait time
            backoff_factor (float): Backoff factor
            strategy (RetryStrategy): Retry strategy
        """
        self.retry_configs[operation_name] = {
            'max_retries': max_retries,
            'initial_wait': initial_wait,
            'backoff_factor': backoff_factor,
            'strategy': strategy
        }
    
    def execute_with_retry(self, operation_name: str, func: Callable, 
                          *args: Any, **kwargs: Any) -> Any:
        """
        Execute a function with retry logic.
        
        Args:
            operation_name (str): Name of the operation
            func (Callable): Function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Any: Function result
        """
        config = self.retry_configs.get(operation_name, {
            'max_retries': 3,
            'initial_wait': 1.0,
            'backoff_factor': 2.0,
            'strategy': RetryStrategy.EXPONENTIAL_BACKOFF
        })
        
        decorator = retry_with_backoff(
            max_retries=config['max_retries'],
            initial_wait=config['initial_wait'],
            backoff_factor=config['backoff_factor'],
            strategy=config['strategy']
        )
        
        decorated_func = decorator(func)
        return decorated_func(*args, **kwargs)


def main():
    """Demonstrate the usage of the error handling and retry mechanism."""
    print("Error Handler and Retry Mechanism Demo")
    print("=" * 50)
    
    # Create error handler
    error_handler = ErrorHandler()
    
    # Test error handling
    test_error = Exception("Test ST-Link connection error")
    success = error_handler.handle_st_link_error(test_error)
    print(f"ST-Link error handling result: {success}")
    
    # Test retry decorator
    @retry_with_backoff(max_retries=3, initial_wait=0.1, backoff_factor=2.0)
    def failing_function(attempt: int = 0):
        if attempt < 2:
            raise Exception(f"Simulated failure (attempt {attempt + 1})")
        return "Success!"
    
    try:
        result = failing_function()
        print(f"Retry function result: {result}")
    except Exception as e:
        print(f"Retry function failed: {e}")
    
    # Test retry manager
    retry_manager = RetryManager(error_handler)
    retry_manager.configure_retry("test_operation", max_retries=2, initial_wait=0.1)
    
    def test_operation():
        raise Exception("Test operation failure")
    
    try:
        result = retry_manager.execute_with_retry("test_operation", test_operation)
        print(f"Retry manager result: {result}")
    except Exception as e:
        print(f"Retry manager failed: {e}")
    
    # Get statistics
    stats = error_handler.get_error_statistics()
    print(f"Error statistics: {stats}")


if __name__ == "__main__":
    main()
