"""
Logging and monitoring module for STM32 programming system.

This module provides comprehensive logging functionality for the programming process
and error handling.
"""

import logging
import os
import time
from datetime import datetime
from typing import Dict, Any, Optional
import json
from pathlib import Path


class ProgrammingLogger:
    """Class for comprehensive logging and monitoring of the programming process."""
    
    def __init__(self, log_dir: str = "logs", log_level: int = logging.INFO):
        """
        Initialize the programming logger.
        
        Args:
            log_dir (str): Directory to store log files
            log_level (int): Logging level
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Statistics tracking
        self.stats = {
            'total_files': 0,
            'successful_programming': 0,
            'failed_programming': 0,
            'start_time': None,
            'end_time': None,
            'errors': []
        }
        
        # Setup logging
        self._setup_logging(log_level)
        
    def _setup_logging(self, log_level: int) -> None:
        """
        Setup logging configuration.
        
        Args:
            log_level (int): Logging level
        """
        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        simple_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        
        # File handler for detailed logs
        log_file = self.log_dir / f"programming_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(detailed_formatter)
        
        # Console handler for important messages
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(simple_formatter)
        
        # Setup root logger
        self.logger = logging.getLogger('STM32Programming')
        self.logger.setLevel(log_level)
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        # Prevent duplicate logs
        self.logger.propagate = False
        
        self.logger.info(f"Logging initialized. Log file: {log_file}")
    
    def info(self, message: str) -> None:
        """
        Log info message.
        
        Args:
            message (str): Message to log
        """
        self.logger.info(message)
    
    def warning(self, message: str) -> None:
        """
        Log warning message.
        
        Args:
            message (str): Message to log
        """
        self.logger.warning(message)
    
    def error(self, message: str) -> None:
        """
        Log error message.
        
        Args:
            message (str): Message to log
        """
        self.logger.error(message)
        self.stats['errors'].append({
            'timestamp': datetime.now().isoformat(),
            'message': message
        })
    
    def critical(self, message: str) -> None:
        """
        Log critical message.
        
        Args:
            message (str): Message to log
        """
        self.logger.critical(message)
        self.stats['errors'].append({
            'timestamp': datetime.now().isoformat(),
            'message': f"CRITICAL: {message}"
        })
    
    def debug(self, message: str) -> None:
        """
        Log debug message.
        
        Args:
            message (str): Message to log
        """
        self.logger.debug(message)
    
    def log_programming_start(self, filename: str, serial_number: str) -> None:
        """
        Log the start of programming operation.
        
        Args:
            filename (str): Firmware filename
            serial_number (str): Serial number
        """
        self.stats['total_files'] += 1
        if self.stats['start_time'] is None:
            self.stats['start_time'] = datetime.now().isoformat()
        
        self.info(f"Starting programming: {filename} (Serial: {serial_number})")
    
    def log_programming_success(self, filename: str, serial_number: str, duration: float) -> None:
        """
        Log successful programming operation.
        
        Args:
            filename (str): Firmware filename
            serial_number (str): Serial number
            duration (float): Programming duration in seconds
        """
        self.stats['successful_programming'] += 1
        self.info(f"Programming successful: {filename} (Serial: {serial_number}) - Duration: {duration:.2f}s")
    
    def log_programming_failure(self, filename: str, serial_number: str, error: str) -> None:
        """
        Log failed programming operation.
        
        Args:
            filename (str): Firmware filename
            serial_number (str): Serial number
            error (str): Error message
        """
        self.stats['failed_programming'] += 1
        self.error(f"Programming failed: {filename} (Serial: {serial_number}) - Error: {error}")
    
    def log_statistics(self) -> None:
        """
        Log programming statistics.
        """
        self.stats['end_time'] = datetime.now().isoformat()
        
        total = self.stats['total_files']
        successful = self.stats['successful_programming']
        failed = self.stats['failed_programming']
        
        if total > 0:
            success_rate = (successful / total) * 100
            self.info(f"Programming Statistics:")
            self.info(f"  Total files: {total}")
            self.info(f"  Successful: {successful}")
            self.info(f"  Failed: {failed}")
            self.info(f"  Success rate: {success_rate:.1f}%")
            
            if self.stats['start_time'] and self.stats['end_time']:
                start = datetime.fromisoformat(self.stats['start_time'])
                end = datetime.fromisoformat(self.stats['end_time'])
                duration = (end - start).total_seconds()
                self.info(f"  Total duration: {duration:.2f}s")
                if successful > 0:
                    avg_time = duration / successful
                    self.info(f"  Average time per file: {avg_time:.2f}s")
        
        # Save statistics to file
        self._save_statistics()
    
    def _save_statistics(self) -> None:
        """
        Save statistics to JSON file.
        """
        try:
            stats_file = self.log_dir / f"statistics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(stats_file, 'w', encoding='utf-8') as f:
                json.dump(self.stats, f, indent=2, ensure_ascii=False)
            self.info(f"Statistics saved to: {stats_file}")
        except Exception as e:
            self.error(f"Failed to save statistics: {e}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get current statistics.
        
        Returns:
            Dict[str, Any]: Current statistics dictionary
        """
        return self.stats.copy()
    
    def reset_statistics(self) -> None:
        """
        Reset statistics.
        """
        self.stats = {
            'total_files': 0,
            'successful_programming': 0,
            'failed_programming': 0,
            'start_time': None,
            'end_time': None,
            'errors': []
        }
        self.info("Statistics reset")


def main():
    """Demonstrate the usage of the ProgrammingLogger class."""
    logger = ProgrammingLogger()
    
    # Example usage
    logger.info("Starting STM32 programming system")
    logger.log_programming_start("test_firmware.bin", "25J040001")
    
    # Simulate some operations
    time.sleep(1)
    logger.log_programming_success("test_firmware.bin", "25J040001", 1.5)
    
    logger.log_programming_start("test_firmware2.bin", "25J040002")
    logger.log_programming_failure("test_firmware2.bin", "25J040002", "Connection timeout")
    
    # Log statistics
    logger.log_statistics()
    
    # Get statistics
    stats = logger.get_statistics()
    print(f"Final statistics: {stats}")


if __name__ == "__main__":
    main()
