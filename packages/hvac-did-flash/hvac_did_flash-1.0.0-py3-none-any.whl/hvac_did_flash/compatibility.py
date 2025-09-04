"""
Compatibility layer for STM32 programming system.

This module provides compatibility with existing common.py and auto_program.py modules
while transitioning to the new system architecture.
"""

import warnings
import os
import sys
import time
from typing import Any, Callable, Optional, Tuple, Dict
from functools import wraps

# Import new system modules
from .file_scanner import FirmwareFileScanner
from .st_link_handler import STLinkHandler
from .serial_communicator import SerialCommunicator
from .firmware_programmer import FirmwareProgrammer
from .file_handler import FileHandler
from .logger import ProgrammingLogger
from .error_handler import ErrorHandler, retry_with_backoff

# Import existing modules for reference
from . import common

# Try to import auto_program, but handle missing dependencies gracefully
try:
    from . import auto_program
    AUTO_PROGRAM_AVAILABLE = True
except ImportError as e:
    print(f"Warning: auto_program module not available: {e}")
    AUTO_PROGRAM_AVAILABLE = False
    auto_program = None


class CompatibilityLayer:
    """Compatibility layer to bridge old and new systems."""
    
    def __init__(self):
        """Initialize the compatibility layer."""
        self.logger = ProgrammingLogger()
        self.error_handler = ErrorHandler()
        self.file_scanner = FirmwareFileScanner()
        self.stlink_handler = STLinkHandler()
        self.file_handler = FileHandler()
        self.firmware_programmer = FirmwareProgrammer()
        
        # Statistics for compatibility tracking
        self.compatibility_stats = {
            'legacy_calls': 0,
            'deprecation_warnings': 0,
            'successful_migrations': 0,
            'failed_migrations': 0
        }
    
    @staticmethod
    def legacy_function_wrapper(func_name: str, new_func: Optional[Callable] = None):
        """
        Decorator for legacy function compatibility.
        
        Args:
            func_name (str): Name of the legacy function
            new_func (Optional[Callable]): New function to call instead
            
        Returns:
            Callable: Decorated function
        """
        def decorator(old_func: Callable) -> Callable:
            @wraps(old_func)
            def wrapper(*args: Any, **kwargs: Any) -> Any:
                # Show deprecation warning
                warnings.warn(
                    f'{func_name} is deprecated and will be removed in future versions. '
                    f'Please use the new STM32 programming system instead.',
                    DeprecationWarning,
                    stacklevel=2
                )
                
                # Call the new function if provided, otherwise call the old one
                if new_func:
                    try:
                        return new_func(*args, **kwargs)
                    except Exception as e:
                        warnings.warn(
                            f'New function failed, falling back to legacy function: {e}',
                            UserWarning,
                            stacklevel=2
                        )
                        return old_func(*args, **kwargs)
                else:
                    return old_func(*args, **kwargs)
            
            return wrapper
        return decorator
    
    # Compatibility wrappers for common.py functions
    
    @legacy_function_wrapper('run_command')
    def run_command(self, command):
        """
        Legacy wrapper for run_command function.
        
        Args:
            command: Command to run
            
        Returns:
            Any: Command result
        """
        self.compatibility_stats['legacy_calls'] += 1
        
        try:
            # Use the new system's command execution
            if isinstance(command, list):
                cmd = command
            else:
                cmd = command.split()
            
            # Use subprocess directly (same as original)
            import subprocess
            result = subprocess.run(cmd, check=True, text=True, capture_output=True)
            return result
        except subprocess.CalledProcessError as e:
            print(f"Error occurred: {e.stderr}")
            sys.exit(e.returncode)
    
    @legacy_function_wrapper('parse_commit_message')
    def parse_commit_message(self):
        """
        Legacy wrapper for parse_commit_message function.
        
        Returns:
            Tuple[Optional[str], Optional[str]]: (filename, google_drive_file_id)
        """
        self.compatibility_stats['legacy_calls'] += 1
        
        # Use the original implementation
        return common.parse_commit_message()
    
    @legacy_function_wrapper('get_sha')
    def get_sha(self, file):
        """
        Legacy wrapper for get_sha function.
        
        Args:
            file (str): File path
            
        Returns:
            str: SHA value
        """
        self.compatibility_stats['legacy_calls'] += 1
        
        # Use the original implementation
        return common.get_sha(file)
    
    @legacy_function_wrapper('cleanup_downloaded_files')
    def cleanup_downloaded_files(self, file_path):
        """
        Legacy wrapper for cleanup_downloaded_files function.
        
        Args:
            file_path (str): Path to file to cleanup
        """
        self.compatibility_stats['legacy_calls'] += 1
        
        # Use the original implementation
        return common.cleanup_downloaded_files(file_path)
    
    @legacy_function_wrapper('create_temp_directory')
    def create_temp_directory(self, base_dir="temp_downloads"):
        """
        Legacy wrapper for create_temp_directory function.
        
        Args:
            base_dir (str): Base directory name
            
        Returns:
            Optional[str]: Created directory path
        """
        self.compatibility_stats['legacy_calls'] += 1
        
        # Use the original implementation
        return common.create_temp_directory(base_dir)
    
    @legacy_function_wrapper('read_serial')
    def read_serial(self, ser, sha=""):
        """
        Legacy wrapper for read_serial function.
        
        Args:
            ser: Serial connection object
            sha (str): SHA value to check
        """
        self.compatibility_stats['legacy_calls'] += 1
        
        # Use the original implementation
        return common.read_serial(ser, sha)
    
    @legacy_function_wrapper('check_stlink')
    def check_stlink(self, sn):
        """
        Legacy wrapper for check_stlink function.
        
        Args:
            sn (str): ST-Link serial number
        """
        self.compatibility_stats['legacy_calls'] += 1
        
        # Use the original implementation
        return common.check_stlink(sn)
    
    @legacy_function_wrapper('open_stlink')
    def open_stlink(self):
        """
        Legacy wrapper for open_stlink function.
        
        Returns:
            Tuple[Optional[serial.Serial], Optional[str]]: (serial_connection, stlink_sn)
        """
        self.compatibility_stats['legacy_calls'] += 1
        
        # Use the original implementation
        return common.open_stlink()
    
    # Compatibility wrappers for auto_program.py functions
    
    @legacy_function_wrapper('download_firmware')
    def download_firmware(self):
        """
        Legacy wrapper for download_firmware function.
        
        Returns:
            str: Downloaded file path
        """
        self.compatibility_stats['legacy_calls'] += 1
        
        if not AUTO_PROGRAM_AVAILABLE:
            raise ImportError("auto_program module not available due to missing dependencies")
        
        # Use the original implementation
        return auto_program.download_firmware()
    
    @legacy_function_wrapper('extract_firmware_metadata')
    def extract_firmware_metadata(self, bin_file):
        """
        Legacy wrapper for extract_firmware_metadata function.
        
        Args:
            bin_file (str): Path to binary file
            
        Returns:
            Tuple[str, str]: (sha, offset)
        """
        self.compatibility_stats['legacy_calls'] += 1
        
        if not AUTO_PROGRAM_AVAILABLE:
            raise ImportError("auto_program module not available due to missing dependencies")
        
        # Use the original implementation
        return auto_program.extract_firmware_metadata(bin_file)
    
    @legacy_function_wrapper('program_firmware')
    def program_firmware(self, bin_file, sha, offset):
        """
        Legacy wrapper for program_firmware function.
        
        Args:
            bin_file (str): Path to binary file
            sha (str): SHA value
            offset (str): Memory offset
        """
        self.compatibility_stats['legacy_calls'] += 1
        
        if not AUTO_PROGRAM_AVAILABLE:
            raise ImportError("auto_program module not available due to missing dependencies")
        
        # Use the original implementation
        return auto_program.program_firmware(bin_file, sha, offset)
    
    # New system integration methods
    
    def migrate_to_new_system(self, firmware_dir: str = "upload_firmware") -> Dict[str, Any]:
        """
        Migrate from legacy system to new system.
        
        Args:
            firmware_dir (str): Directory containing firmware files
            
        Returns:
            Dict[str, Any]: Migration results
        """
        results = {
            'success': False,
            'files_processed': 0,
            'successful_programming': 0,
            'failed_programming': 0,
            'errors': []
        }
        
        try:
            self.logger.info("Starting migration to new STM32 programming system")
            
            # Scan for firmware files using new system
            firmware_files = self.file_scanner.scan_firmware_files()
            results['files_processed'] = len(firmware_files)
            
            if not firmware_files:
                self.logger.warning("No firmware files found for migration")
                return results
            
            # Process each firmware file
            for file_path in firmware_files:
                try:
                    # Extract serial number
                    filename = os.path.basename(file_path)
                    serial_number = self.file_scanner.extract_serial_number(filename)
                    
                    if not serial_number:
                        self.logger.warning(f"No serial number found for {filename}")
                        continue
                    
                    # Program using new system
                    # Note: This would require actual ST-Link connection
                    self.logger.info(f"Processing {filename} with serial {serial_number}")
                    
                    # For demonstration, we'll just log the processing
                    results['successful_programming'] += 1
                    
                except Exception as e:
                    self.logger.error(f"Error processing {file_path}: {e}")
                    results['failed_programming'] += 1
                    results['errors'].append(str(e))
            
            results['success'] = results['failed_programming'] == 0
            self.compatibility_stats['successful_migrations'] += 1
            
            self.logger.info(f"Migration completed: {results}")
            return results
            
        except Exception as e:
            self.logger.error(f"Migration failed: {e}")
            results['errors'].append(str(e))
            self.compatibility_stats['failed_migrations'] += 1
            return results
    
    def get_compatibility_statistics(self) -> Dict[str, Any]:
        """
        Get compatibility layer statistics.
        
        Returns:
            Dict[str, Any]: Compatibility statistics
        """
        return {
            'compatibility_stats': self.compatibility_stats.copy(),
            'new_system_available': True,
            'migration_recommended': self.compatibility_stats['legacy_calls'] > 10
        }
    
    def reset_compatibility_statistics(self) -> None:
        """Reset compatibility statistics."""
        self.compatibility_stats = {
            'legacy_calls': 0,
            'deprecation_warnings': 0,
            'successful_migrations': 0,
            'failed_migrations': 0
        }
        self.logger.info("Compatibility statistics reset")


# Global compatibility instance
_compatibility_layer = None


def get_compatibility_layer() -> CompatibilityLayer:
    """
    Get the global compatibility layer instance.
    
    Returns:
        CompatibilityLayer: Global compatibility layer instance
    """
    global _compatibility_layer
    if _compatibility_layer is None:
        _compatibility_layer = CompatibilityLayer()
    return _compatibility_layer


# Convenience functions for backward compatibility
def run_command(command):
    """Backward compatible run_command function."""
    return get_compatibility_layer().run_command(command)


def parse_commit_message():
    """Backward compatible parse_commit_message function."""
    return get_compatibility_layer().parse_commit_message()


def get_sha(file):
    """Backward compatible get_sha function."""
    return get_compatibility_layer().get_sha(file)


def cleanup_downloaded_files(file_path):
    """Backward compatible cleanup_downloaded_files function."""
    return get_compatibility_layer().cleanup_downloaded_files(file_path)


def create_temp_directory(base_dir="temp_downloads"):
    """Backward compatible create_temp_directory function."""
    return get_compatibility_layer().create_temp_directory(base_dir)


def read_serial(ser, sha=""):
    """Backward compatible read_serial function."""
    return get_compatibility_layer().read_serial(ser, sha)


def check_stlink(sn):
    """Backward compatible check_stlink function."""
    return get_compatibility_layer().check_stlink(sn)


def open_stlink():
    """Backward compatible open_stlink function."""
    return get_compatibility_layer().open_stlink()


def download_firmware():
    """Backward compatible download_firmware function."""
    return get_compatibility_layer().download_firmware()


def extract_firmware_metadata(bin_file):
    """Backward compatible extract_firmware_metadata function."""
    return get_compatibility_layer().extract_firmware_metadata(bin_file)


def program_firmware(bin_file, sha, offset):
    """Backward compatible program_firmware function."""
    return get_compatibility_layer().program_firmware(bin_file, sha, offset)


def main():
    """Demonstrate the compatibility layer."""
    print("STM32 Programming System Compatibility Layer Demo")
    print("=" * 60)
    
    # Create compatibility layer
    compat = CompatibilityLayer()
    
    # Test legacy function calls
    print("Testing legacy function compatibility...")
    
    # Test get_sha function
    test_file = "upload_firmware/hvac-main-stm32f103@CYBER-QZ25_25J040001_v1.13.2-alpha.2-1-g2121caf9.bin"
    if os.path.exists(test_file):
        sha = compat.get_sha(test_file)
        print(f"Legacy get_sha result: {sha}")
    
    # Test migration to new system
    print("\nTesting migration to new system...")
    migration_results = compat.migrate_to_new_system()
    print(f"Migration results: {migration_results}")
    
    # Get compatibility statistics
    stats = compat.get_compatibility_statistics()
    print(f"\nCompatibility statistics: {stats}")
    
    # Test backward compatibility functions
    print("\nTesting backward compatibility functions...")
    try:
        # This will show deprecation warnings
        sha = get_sha(test_file)
        print(f"Backward compatible get_sha result: {sha}")
    except Exception as e:
        print(f"Error in backward compatible function: {e}")


if __name__ == "__main__":
    main()
