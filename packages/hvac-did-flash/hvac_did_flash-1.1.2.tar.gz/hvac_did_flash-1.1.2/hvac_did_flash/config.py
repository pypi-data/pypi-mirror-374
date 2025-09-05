"""
Configuration Management Module

This module provides configuration management functionality for the STM32 programming system.
It handles reading configuration from files, setting defaults, and parsing command-line arguments.
"""

import configparser
import argparse
import os
from typing import Dict, Any, Optional
import logging


class Config:
    """
    Configuration management class for the STM32 programming system.
    
    This class handles loading configuration from files, setting default values,
    and providing access to configuration options throughout the application.
    """
    
    def __init__(self, config_file_path: Optional[str] = None):
        """
        Initialize the configuration manager.
        
        Args:
            config_file_path: Optional path to configuration file
        """
        self.config = configparser.ConfigParser()
        self.config_file_path = config_file_path or "stm32_programmer.conf"
        self.logger = logging.getLogger(__name__)
        
        # Initialize with defaults
        self.set_defaults()
        
        # Load from file if it exists
        if os.path.exists(self.config_file_path):
            self.load_from_file(self.config_file_path)
            self.logger.info(f"Configuration loaded from {self.config_file_path}")
    
    def set_defaults(self) -> None:
        """
        Set default configuration values.
        
        This method defines all the default configuration settings
        for the STM32 programming system.
        """
        # General settings
        self.config['GENERAL'] = {
            'firmware_directory': 'upload_firmware',
            'log_level': 'INFO',
            'log_file': 'stm32_programmer.log',
            'max_log_size': '10485760',  # 10MB
            'log_backup_count': '5'
        }
        
        # STM32 Programmer settings
        self.config['PROGRAMMER'] = {
            'stm32_programmer_cli': 'STM32_Programmer_CLI.exe',
            'programming_timeout': '300',  # 5 minutes
            'verify_after_programming': 'true',
            'mass_erase_before_programming': 'false',
            'reset_after_programming': 'true',
            'connect_mode': 'underReset',  # underReset, hotPlug, normal
            'programming_speed': '4000',  # kHz
            'erase_mode': 'sector',  # sector, mass
            'verify_mode': 'checksum',  # checksum, readback
            'stlink_sn': '',  # ST-Link serial number (empty for auto-detect)
            'offset': '0x08000000'  # Flash programming offset
        }
        
        # Serial communication settings
        self.config['SERIAL'] = {
            'port': 'COM1',
            'baudrate': '115200',
            'timeout': '5.0',
            'verification_timeout': '30.0',
            'retry_attempts': '3',
            'data_bits': '8',
            'stop_bits': '1',
            'parity': 'none',
            'flow_control': 'none'
        }
        
        # File handling settings
        self.config['FILES'] = {
            'processed_extension': 'xxx',
            'backup_processed_files': 'true',
            'backup_directory': 'backup',
            'checksum_file': 'firmware_checksums.json',
            'temp_directory': 'temp',
            'log_directory': 'logs',
            'firmware_pattern': '*.bin',
            'max_file_size': '104857600'  # 100MB
        }
        
        # Flash check settings
        self.config['FLASH_CHECK'] = {
            'check_address': '0x08000000',
            'expected_value': '0x12345678',
            'max_retry_attempts': '10',
            'retry_delay': '2'
        }
        
        # Voice announcement settings
        self.config['VOICE_ANNOUNCEMENT'] = {
            'enable_voice': 'true',
            'language': 'ko',
            'announce_board_completed': 'true',
            'announce_programming_start': 'false',
            'announce_programming_complete': 'true',
            'announce_errors': 'true'
        }
        
        # Performance monitoring settings
        self.config['PERFORMANCE'] = {
            'enable_monitoring': 'true',
            'report_interval': '60',  # seconds
            'max_memory_usage': '1073741824',  # 1GB
            'max_cpu_usage': '80'  # percentage
        }
        
        # Error handling settings
        self.config['ERROR_HANDLING'] = {
            'max_retry_attempts': '3',
            'retry_delay': '5.0',  # seconds
            'exponential_backoff': 'true',
            'max_backoff_delay': '60.0'  # seconds
        }
    
    def load_from_file(self, file_path: str) -> None:
        """
        Load configuration from a file.
        
        Args:
            file_path: Path to the configuration file
            
        Raises:
            FileNotFoundError: If the configuration file doesn't exist
            configparser.Error: If the configuration file is malformed
        """
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Configuration file not found: {file_path}")
            
            self.config.read(file_path)
            self.config_file_path = file_path
            self.logger.info(f"Configuration loaded from {file_path}")
            
        except configparser.Error as e:
            self.logger.error(f"Error parsing configuration file {file_path}: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Error loading configuration file {file_path}: {e}")
            raise
    
    def save_to_file(self, file_path: Optional[str] = None) -> None:
        """
        Save configuration to a file.
        
        Args:
            file_path: Optional path to save the configuration file.
                      If None, uses the current config_file_path.
                      
        Raises:
            IOError: If unable to write to the file
        """
        save_path = file_path or self.config_file_path
        
        try:
            # Create directory if it doesn't exist
            dir_path = os.path.dirname(save_path)
            if dir_path:  # Only create directory if there's a directory path
                os.makedirs(dir_path, exist_ok=True)
            
            with open(save_path, 'w') as configfile:
                self.config.write(configfile)
            
            self.logger.info(f"Configuration saved to {save_path}")
            
        except IOError as e:
            self.logger.error(f"Error saving configuration to {save_path}: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error saving configuration to {save_path}: {e}")
            raise
    
    def get_config(self) -> Dict[str, Any]:
        """
        Return configuration as a dictionary.
        
        Returns:
            Dictionary containing all configuration values
        """
        config_dict = {}
        for section in self.config.sections():
            config_dict[section] = dict(self.config[section])
        return config_dict
    
    def get(self, section: str, option: str, fallback: Any = None) -> str:
        """
        Get a configuration value.
        
        Args:
            section: Configuration section name
            option: Configuration option name
            fallback: Fallback value if option doesn't exist
            
        Returns:
            Configuration value as string
        """
        return self.config.get(section, option, fallback=fallback)
    
    def getint(self, section: str, option: str, fallback: int = 0) -> int:
        """
        Get a configuration value as integer.
        
        Args:
            section: Configuration section name
            option: Configuration option name
            fallback: Fallback value if option doesn't exist
            
        Returns:
            Configuration value as integer
        """
        return self.config.getint(section, option, fallback=fallback)
    
    def getfloat(self, section: str, option: str, fallback: float = 0.0) -> float:
        """
        Get a configuration value as float.
        
        Args:
            section: Configuration section name
            option: Configuration option name
            fallback: Fallback value if option doesn't exist
            
        Returns:
            Configuration value as float
        """
        return self.config.getfloat(section, option, fallback=fallback)
    
    def getboolean(self, section: str, option: str, fallback: bool = False) -> bool:
        """
        Get a configuration value as boolean.
        
        Args:
            section: Configuration section name
            option: Configuration option name
            fallback: Fallback value if option doesn't exist
            
        Returns:
            Configuration value as boolean
        """
        return self.config.getboolean(section, option, fallback=fallback)
    
    def set(self, section: str, option: str, value: str) -> None:
        """
        Set a configuration value.
        
        Args:
            section: Configuration section name
            option: Configuration option name
            value: Value to set
        """
        if section not in self.config:
            self.config.add_section(section)
        self.config.set(section, option, str(value))
    
    def update_from_args(self, args: argparse.Namespace) -> None:
        """
        Update configuration from command-line arguments.
        
        Args:
            args: Parsed command-line arguments
        """
        # Map command-line arguments to configuration settings
        arg_mappings = {
            'firmware_dir': ('GENERAL', 'firmware_directory'),
            'log_level': ('GENERAL', 'log_level'),
            'log_file': ('GENERAL', 'log_file'),
            'programmer_cli': ('PROGRAMMER', 'stm32_programmer_cli'),
            'timeout': ('PROGRAMMER', 'programming_timeout'),
            'verify': ('PROGRAMMER', 'verify_after_programming'),
            'mass_erase': ('PROGRAMMER', 'mass_erase_before_programming'),
            'connect_mode': ('PROGRAMMER', 'connect_mode'),
            'programming_speed': ('PROGRAMMER', 'programming_speed'),
            'erase_mode': ('PROGRAMMER', 'erase_mode'),
            'verify_mode': ('PROGRAMMER', 'verify_mode'),
            'stlink_sn': ('PROGRAMMER', 'stlink_sn'),
            'baudrate': ('SERIAL', 'baudrate'),
            'serial_timeout': ('SERIAL', 'timeout'),
            'data_bits': ('SERIAL', 'data_bits'),
            'stop_bits': ('SERIAL', 'stop_bits'),
            'parity': ('SERIAL', 'parity'),
            'flow_control': ('SERIAL', 'flow_control'),
            'max_retries': ('ERROR_HANDLING', 'max_retry_attempts'),
            'retry_delay': ('ERROR_HANDLING', 'retry_delay'),
            'firmware_pattern': ('FILES', 'firmware_pattern'),
            'max_file_size': ('FILES', 'max_file_size')
        }
        
        for arg_name, (section, option) in arg_mappings.items():
            if hasattr(args, arg_name) and getattr(args, arg_name) is not None:
                self.set(section, option, str(getattr(args, arg_name)))
                self.logger.debug(f"Updated {section}.{option} from command line: {getattr(args, arg_name)}")


def parse_command_line_args() -> argparse.Namespace:
    """
    Parse command-line arguments for configuration overrides.
    
    Returns:
        Parsed command-line arguments
    """
    parser = argparse.ArgumentParser(
        description="STM32 Firmware Programming System",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # General options
    parser.add_argument(
        '--config', 
        type=str,
        help='Path to configuration file'
    )
    parser.add_argument(
        '--firmware-dir',
        type=str,
        help='Directory containing firmware files'
    )
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        help='Logging level'
    )
    parser.add_argument(
        '--log-file',
        type=str,
        help='Path to log file'
    )
    
    # Programmer options
    parser.add_argument(
        '--programmer-cli',
        type=str,
        help='Path to STM32Programmer_CLI.exe'
    )
    parser.add_argument(
        '--timeout',
        type=int,
        help='Programming timeout in seconds'
    )
    parser.add_argument(
        '--verify',
        action='store_true',
        help='Verify firmware after programming'
    )
    parser.add_argument(
        '--no-verify',
        dest='verify',
        action='store_false',
        help='Do not verify firmware after programming'
    )
    parser.add_argument(
        '--mass-erase',
        action='store_true',
        help='Perform mass erase before programming'
    )
    parser.add_argument(
        '--connect-mode',
        choices=['underReset', 'hotPlug', 'normal'],
        help='STM32 connection mode'
    )
    parser.add_argument(
        '--programming-speed',
        type=int,
        help='Programming speed in kHz'
    )
    parser.add_argument(
        '--erase-mode',
        choices=['sector', 'mass'],
        help='Erase mode for programming'
    )
    parser.add_argument(
        '--verify-mode',
        choices=['checksum', 'readback'],
        help='Verification mode after programming'
    )
    parser.add_argument(
        '--stlink-sn',
        type=str,
        help='ST-Link serial number (empty for auto-detect)'
    )
    
    # Serial communication options
    parser.add_argument(
        '--baudrate',
        type=int,
        help='Serial communication baudrate'
    )
    parser.add_argument(
        '--serial-timeout',
        type=float,
        help='Serial communication timeout in seconds'
    )
    parser.add_argument(
        '--data-bits',
        type=int,
        choices=[5, 6, 7, 8],
        help='Serial data bits'
    )
    parser.add_argument(
        '--stop-bits',
        type=int,
        choices=[1, 2],
        help='Serial stop bits'
    )
    parser.add_argument(
        '--parity',
        choices=['none', 'even', 'odd'],
        help='Serial parity'
    )
    parser.add_argument(
        '--flow-control',
        choices=['none', 'hardware', 'software'],
        help='Serial flow control'
    )
    
    # Error handling options
    parser.add_argument(
        '--max-retries',
        type=int,
        help='Maximum number of retry attempts'
    )
    parser.add_argument(
        '--retry-delay',
        type=float,
        help='Delay between retry attempts in seconds'
    )
    
    # Action options
    parser.add_argument(
        '--batch',
        action='store_true',
        help='Process all firmware files in batch mode'
    )
    parser.add_argument(
        '--single-file',
        type=str,
        help='Process only the specified firmware file'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Perform a dry run without actual programming'
    )
    parser.add_argument(
        '--firmware-pattern',
        type=str,
        help='Pattern for firmware files (e.g., *.bin)'
    )
    parser.add_argument(
        '--max-file-size',
        type=int,
        help='Maximum file size in bytes'
    )
    
    return parser.parse_args()


def main():
    """
    Demonstration of the configuration management system.
    """
    # Set up basic logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("STM32 Programming System Configuration Management Demo")
    print("=" * 60)
    
    # Parse command-line arguments
    args = parse_command_line_args()
    
    # Create configuration instance
    config_file = args.config if args.config else None
    config = Config(config_file)
    
    # Update configuration from command-line arguments
    config.update_from_args(args)
    
    # Display current configuration
    print("\nCurrent Configuration:")
    print("-" * 30)
    config_dict = config.get_config()
    for section, options in config_dict.items():
        print(f"\n[{section}]")
        for option, value in options.items():
            print(f"{option} = {value}")
    
    # Save configuration if requested
    if hasattr(args, 'save_config') and args.save_config:
        config.save_to_file()
        print(f"\nConfiguration saved to {config.config_file_path}")
    
    # Demonstrate getting specific configuration values
    print("\nConfiguration Access Examples:")
    print("-" * 35)
    print(f"Firmware directory: {config.get('GENERAL', 'firmware_directory')}")
    print(f"Programming timeout: {config.getint('PROGRAMMER', 'programming_timeout')} seconds")
    print(f"Verify after programming: {config.getboolean('PROGRAMMER', 'verify_after_programming')}")
    print(f"Serial baudrate: {config.getint('SERIAL', 'baudrate')}")
    print(f"Max retry attempts: {config.getint('ERROR_HANDLING', 'max_retry_attempts')}")


if __name__ == "__main__":
    main()
