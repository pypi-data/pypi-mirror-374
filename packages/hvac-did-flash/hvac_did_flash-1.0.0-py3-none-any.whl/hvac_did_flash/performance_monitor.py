"""
Performance Monitoring and Optimization Module

This module provides comprehensive performance monitoring functionality for the STM32 programming system.
It includes execution time measurement, memory usage tracking, CPU usage monitoring, and performance reporting.
"""

import time
import psutil
import logging
import json
from datetime import datetime
from typing import Callable, Any, Dict, List, Optional
from functools import wraps
from pathlib import Path


class PerformanceMonitor:
    """
    Class for monitoring and optimizing performance of the programming process.
    """
    
    def __init__(self, log_dir: str = "logs"):
        """
        Initialize the performance monitor.
        
        Args:
            log_dir (str): Directory to store performance logs
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Performance data storage
        self.execution_times = []
        self.memory_usage = []
        self.cpu_usage = []
        self.performance_log = []
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
        # Performance thresholds
        self.max_memory_usage = 1073741824  # 1GB
        self.max_cpu_usage = 80.0  # 80%
        self.max_execution_time = 300.0  # 5 minutes
        
        self.logger.info("Performance monitor initialized")
    
    @staticmethod
    def measure_execution_time(func: Callable) -> Callable:
        """
        Decorator to measure and log execution time of functions.
        
        Args:
            func: Function to measure
            
        Returns:
            Wrapped function with execution time measurement
        """
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                # Log execution time
                logging.getLogger(__name__).info(
                    f"Function {func.__name__} executed in {execution_time:.3f} seconds"
                )
                
                return result
                
            except Exception as e:
                execution_time = time.time() - start_time
                logging.getLogger(__name__).error(
                    f"Function {func.__name__} failed after {execution_time:.3f} seconds: {e}"
                )
                raise
        
        return wrapper
    
    @staticmethod
    def get_memory_usage() -> float:
        """
        Get current memory usage in bytes.
        
        Returns:
            Current memory usage in bytes
        """
        try:
            process = psutil.Process()
            memory_info = process.memory_info()
            return memory_info.rss  # Resident Set Size
        except Exception as e:
            logging.getLogger(__name__).error(f"Error getting memory usage: {e}")
            return 0.0
    
    @staticmethod
    def get_detailed_memory_info() -> Dict[str, Any]:
        """
        Get detailed memory information.
        
        Returns:
            Dictionary with detailed memory information
        """
        try:
            process = psutil.Process()
            memory_info = process.memory_info()
            memory_percent = process.memory_percent()
            
            return {
                'rss': memory_info.rss,  # Resident Set Size
                'vms': memory_info.vms,  # Virtual Memory Size
                'percent': memory_percent,
                'rss_mb': memory_info.rss / 1024 / 1024,
                'vms_mb': memory_info.vms / 1024 / 1024
            }
        except Exception as e:
            logging.getLogger(__name__).error(f"Error getting detailed memory info: {e}")
            return {
                'rss': 0,
                'vms': 0,
                'percent': 0,
                'rss_mb': 0,
                'vms_mb': 0
            }
    
    @staticmethod
    def get_cpu_usage() -> float:
        """
        Get current CPU usage percentage.
        
        Returns:
            Current CPU usage percentage
        """
        try:
            return psutil.cpu_percent(interval=0.1)
        except Exception as e:
            logging.getLogger(__name__).error(f"Error getting CPU usage: {e}")
            return 0.0
    
    @staticmethod
    def get_detailed_cpu_info() -> Dict[str, Any]:
        """
        Get detailed CPU information.
        
        Returns:
            Dictionary with detailed CPU information
        """
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()
            cpu_stats = psutil.cpu_stats()
            
            return {
                'percent': cpu_percent,
                'count': cpu_count,
                'frequency_mhz': cpu_freq.current if cpu_freq else 0,
                'frequency_max_mhz': cpu_freq.max if cpu_freq else 0,
                'ctx_switches': cpu_stats.ctx_switches,
                'interrupts': cpu_stats.interrupts,
                'soft_interrupts': cpu_stats.soft_interrupts,
                'syscalls': cpu_stats.syscalls
            }
        except Exception as e:
            logging.getLogger(__name__).error(f"Error getting detailed CPU info: {e}")
            return {
                'percent': 0,
                'count': 0,
                'frequency_mhz': 0,
                'frequency_max_mhz': 0,
                'ctx_switches': 0,
                'interrupts': 0,
                'soft_interrupts': 0,
                'syscalls': 0
            }
    
    def start_monitoring(self) -> None:
        """
        Start performance monitoring.
        """
        self.logger.info("Starting performance monitoring")
        self.start_time = datetime.now()
        
        # Record initial metrics
        self.record_metrics("start")
    
    def stop_monitoring(self) -> None:
        """
        Stop performance monitoring.
        """
        self.logger.info("Stopping performance monitoring")
        self.end_time = datetime.now()
        
        # Record final metrics
        self.record_metrics("stop")
    
    def record_metrics(self, event: str) -> None:
        """
        Record current performance metrics.
        
        Args:
            event: Event identifier for the metrics
        """
        timestamp = datetime.now()
        
        metrics = {
            'timestamp': timestamp.isoformat(),
            'event': event,
            'memory_usage': self.get_memory_usage(),
            'cpu_usage': self.get_cpu_usage(),
            'execution_time': time.time() if hasattr(self, 'start_time') else 0.0
        }
        
        self.performance_log.append(metrics)
        
        # Check thresholds
        self._check_thresholds(metrics)
    
    def _check_thresholds(self, metrics: Dict[str, Any]) -> None:
        """
        Check if performance metrics exceed thresholds.
        
        Args:
            metrics: Current performance metrics
        """
        if metrics['memory_usage'] > self.max_memory_usage:
            self.logger.warning(
                f"Memory usage ({metrics['memory_usage'] / 1024 / 1024:.1f} MB) "
                f"exceeds threshold ({self.max_memory_usage / 1024 / 1024:.1f} MB)"
            )
        
        if metrics['cpu_usage'] > self.max_cpu_usage:
            self.logger.warning(
                f"CPU usage ({metrics['cpu_usage']:.1f}%) "
                f"exceeds threshold ({self.max_cpu_usage:.1f}%)"
            )
    
    def generate_performance_report(self, output_file: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate a comprehensive performance report.
        
        Args:
            output_file: Optional file path to save the report
            
        Returns:
            Dictionary containing performance report data
        """
        if not self.performance_log:
            self.logger.warning("No performance data available for report generation")
            return {}
        
        # Calculate statistics
        memory_usage_values = [m['memory_usage'] for m in self.performance_log]
        cpu_usage_values = [m['cpu_usage'] for m in self.performance_log]
        
        # Get detailed system information
        detailed_memory = self.get_detailed_memory_info()
        detailed_cpu = self.get_detailed_cpu_info()
        
        report = {
            'generated_at': datetime.now().isoformat(),
            'monitoring_duration': str(self.end_time - self.start_time) if hasattr(self, 'end_time') else 'Unknown',
            'total_events': len(self.performance_log),
            'system_info': {
                'cpu_cores': detailed_cpu['count'],
                'cpu_frequency_mhz': detailed_cpu['frequency_mhz'],
                'memory_total_mb': psutil.virtual_memory().total / 1024 / 1024,
                'memory_available_mb': psutil.virtual_memory().available / 1024 / 1024
            },
            'memory_usage': {
                'average_mb': sum(memory_usage_values) / len(memory_usage_values) / 1024 / 1024,
                'maximum_mb': max(memory_usage_values) / 1024 / 1024,
                'minimum_mb': min(memory_usage_values) / 1024 / 1024,
                'current_mb': memory_usage_values[-1] / 1024 / 1024 if memory_usage_values else 0,
                'average_bytes': sum(memory_usage_values) / len(memory_usage_values),
                'maximum_bytes': max(memory_usage_values),
                'minimum_bytes': min(memory_usage_values),
                'current_bytes': memory_usage_values[-1] if memory_usage_values else 0
            },
            'cpu_usage': {
                'average_percent': sum(cpu_usage_values) / len(cpu_usage_values),
                'maximum_percent': max(cpu_usage_values),
                'minimum_percent': min(cpu_usage_values),
                'current_percent': cpu_usage_values[-1] if cpu_usage_values else 0
            },
            'thresholds': {
                'max_memory_usage_mb': self.max_memory_usage / 1024 / 1024,
                'max_cpu_usage_percent': self.max_cpu_usage,
                'max_execution_time_seconds': self.max_execution_time
            },
            'performance_analysis': {
                'memory_threshold_exceeded': any(m > self.max_memory_usage for m in memory_usage_values),
                'cpu_threshold_exceeded': any(c > self.max_cpu_usage for c in cpu_usage_values),
                'memory_optimization_suggestions': self.optimize_memory_usage(),
                'cpu_optimization_suggestions': self.optimize_cpu_usage()
            },
            'events': self.performance_log
        }
        
        # Save report to file if specified
        if output_file:
            output_path = Path(output_file)
            output_path.parent.mkdir(exist_ok=True)
            
            with open(output_path, 'w') as f:
                json.dump(report, f, indent=2)
            
            self.logger.info(f"Performance report saved to {output_path}")
        
        return report
    
    def optimize_memory_usage(self) -> List[str]:
        """
        Analyze and suggest memory optimization strategies.
        
        Returns:
            List of optimization suggestions
        """
        suggestions = []
        
        if not self.performance_log:
            return suggestions
        
        memory_usage_values = [m['memory_usage'] for m in self.performance_log]
        avg_memory = sum(memory_usage_values) / len(memory_usage_values)
        max_memory = max(memory_usage_values)
        
        if avg_memory > self.max_memory_usage * 0.8:
            suggestions.append("Consider implementing memory pooling for large objects")
            suggestions.append("Review file handling to ensure proper cleanup")
        
        if max_memory > self.max_memory_usage:
            suggestions.append("Memory usage exceeded threshold - consider batch processing")
            suggestions.append("Implement garbage collection calls at critical points")
        
        return suggestions
    
    def optimize_cpu_usage(self) -> List[str]:
        """
        Analyze and suggest CPU optimization strategies.
        
        Returns:
            List of optimization suggestions
        """
        suggestions = []
        
        if not self.performance_log:
            return suggestions
        
        cpu_usage_values = [m['cpu_usage'] for m in self.performance_log]
        avg_cpu = sum(cpu_usage_values) / len(cpu_usage_values)
        max_cpu = max(cpu_usage_values)
        
        if avg_cpu > self.max_cpu_usage * 0.8:
            suggestions.append("Consider implementing parallel processing for batch operations")
            suggestions.append("Review I/O operations for potential async optimization")
        
        if max_cpu > self.max_cpu_usage:
            suggestions.append("CPU usage exceeded threshold - consider rate limiting")
            suggestions.append("Implement sleep intervals between intensive operations")
        
        return suggestions
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """
        Get a quick performance summary.
        
        Returns:
            Dictionary with performance summary
        """
        if not self.performance_log:
            return {'status': 'No data available'}
        
        memory_usage_values = [m['memory_usage'] for m in self.performance_log]
        cpu_usage_values = [m['cpu_usage'] for m in self.performance_log]
        
        return {
            'status': 'Monitoring active',
            'total_events': len(self.performance_log),
            'avg_memory_mb': sum(memory_usage_values) / len(memory_usage_values) / 1024 / 1024,
            'max_memory_mb': max(memory_usage_values) / 1024 / 1024,
            'avg_cpu_percent': sum(cpu_usage_values) / len(cpu_usage_values),
            'max_cpu_percent': max(cpu_usage_values),
            'memory_threshold_exceeded': any(m > self.max_memory_usage for m in memory_usage_values),
            'cpu_threshold_exceeded': any(c > self.max_cpu_usage for c in cpu_usage_values)
        }


# Global performance monitor instance
_performance_monitor = None


def get_performance_monitor() -> PerformanceMonitor:
    """
    Get the global performance monitor instance.
    
    Returns:
        PerformanceMonitor instance
    """
    global _performance_monitor
    if _performance_monitor is None:
        _performance_monitor = PerformanceMonitor()
    return _performance_monitor


def performance_monitor_decorator(func: Callable) -> Callable:
    """
    Decorator to automatically monitor function performance.
    
    Args:
        func: Function to monitor
        
    Returns:
        Wrapped function with performance monitoring
    """
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        monitor = get_performance_monitor()
        
        # Record metrics before function execution
        monitor.record_metrics(f"before_{func.__name__}")
        
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            # Record metrics after successful execution
            monitor.record_metrics(f"after_{func.__name__}")
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            
            # Record metrics after failed execution
            monitor.record_metrics(f"error_{func.__name__}")
            
            raise
    
    return wrapper


def main():
    """
    Demonstration of the performance monitoring system.
    """
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("Performance Monitoring System Demo")
    print("=" * 40)
    
    # Create performance monitor
    monitor = PerformanceMonitor()
    
    # Start monitoring
    monitor.start_monitoring()
    
    # Simulate some operations
    @performance_monitor_decorator
    def simulate_work():
        """Simulate some work."""
        time.sleep(1)
        return "Work completed"
    
    # Perform some operations
    for i in range(3):
        print(f"Performing operation {i + 1}...")
        result = simulate_work()
        print(f"Result: {result}")
        
        # Record metrics
        monitor.record_metrics(f"operation_{i + 1}")
    
    # Stop monitoring
    monitor.stop_monitoring()
    
    # Generate performance report
    report = monitor.generate_performance_report("performance_report.json")
    
    # Display summary
    summary = monitor.get_performance_summary()
    print("\nPerformance Summary:")
    print(f"Total events: {summary['total_events']}")
    print(f"Average memory usage: {summary['avg_memory_mb']:.2f} MB")
    print(f"Maximum memory usage: {summary['max_memory_mb']:.2f} MB")
    print(f"Average CPU usage: {summary['avg_cpu_percent']:.2f}%")
    print(f"Maximum CPU usage: {summary['max_cpu_percent']:.2f}%")
    
    # Get optimization suggestions
    memory_suggestions = monitor.optimize_memory_usage()
    cpu_suggestions = monitor.optimize_cpu_usage()
    
    if memory_suggestions:
        print("\nMemory optimization suggestions:")
        for suggestion in memory_suggestions:
            print(f"  - {suggestion}")
    
    if cpu_suggestions:
        print("\nCPU optimization suggestions:")
        for suggestion in cpu_suggestions:
            print(f"  - {suggestion}")


if __name__ == "__main__":
    main()
