"""
ST-Link connection and verification module for STM32 programming system.

This module provides functionality to handle ST-Link connection and verification
using STM32Programmer_CLI.exe.
"""

import os
import subprocess
import time
import json
import logging
from typing import Optional, Tuple, Dict, Any
import serial

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class STLinkHandler:
    """Class to handle ST-Link connection and verification."""
    
    def __init__(self, stlink_config_file: str = None):
        """
        Initialize the ST-Link handler.
        
        Args:
            stlink_config_file (str): Path to ST-Link configuration file (optional)
        """
        self.stlink_config_file = stlink_config_file
        self.stlink_list = self._load_stlink_config() if stlink_config_file else {}
        self.max_retries = 3
        self.retry_delay = 2
        
    def _load_stlink_config(self) -> Dict[str, Any]:
        """
        Load ST-Link configuration from JSON file.
        
        Returns:
            Dict[str, Any]: ST-Link configuration dictionary
        """
        if not os.path.exists(self.stlink_config_file):
            logger.warning(f"ST-Link config file '{self.stlink_config_file}' not found")
            return {}
            
        try:
            with open(self.stlink_config_file, 'r') as f:
                config = json.load(f)
                logger.info(f"Loaded ST-Link configuration from {self.stlink_config_file}")
                return config
        except Exception as e:
            logger.error(f"Error loading ST-Link config: {e}")
            return {}
    
    def check_st_link_connection(self, stlink_sn: str) -> bool:
        """
        Check ST-Link connection using STM32Programmer_CLI.exe.
        
        Args:
            stlink_sn (str): ST-Link serial number
            
        Returns:
            bool: True if connection successful, False otherwise
        """
        cmd = ['STM32_Programmer_CLI.exe', '-l', 'stlink']
        
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Checking ST-Link connection (attempt {attempt + 1}/{self.max_retries})")
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                
                if result.returncode == 0:
                    logger.info("ST-Link connection successful")
                    return True
                else:
                    logger.warning(f"ST-Link connection failed: {result.stderr}")
                    
            except subprocess.TimeoutExpired:
                logger.error("ST-Link connection timeout")
            except Exception as e:
                logger.error(f"Error checking ST-Link connection: {e}")
            
            if attempt < self.max_retries - 1:
                logger.info(f"Retrying in {self.retry_delay} seconds...")
                time.sleep(self.retry_delay)
        
        logger.error("ST-Link connection failed after all retries")
        return False
    
    def verify_stm32_connection(self, stlink_sn: str) -> bool:
        """
        Verify STM32 microcontroller connection.
        
        Args:
            stlink_sn (str): ST-Link serial number
            
        Returns:
            bool: True if STM32 connection verified, False otherwise
        """
        cmd = ['STM32_Programmer_CLI.exe', '-c', 'port=SWD', f'sn={stlink_sn}', '-rdu']
        
        try:
            logger.info(f"Verifying STM32 connection with ST-Link {stlink_sn}")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                logger.info("STM32 connection verified successfully")
                return True
            else:
                logger.error(f"STM32 connection verification failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("STM32 connection verification timeout")
            return False
        except Exception as e:
            logger.error(f"Error verifying STM32 connection: {e}")
            return False
    
    def get_stlink_details(self, runner_name: str, stlink_name: str) -> Optional[Dict[str, Any]]:
        """
        Get ST-Link details from configuration.
        
        Args:
            runner_name (str): Runner name
            stlink_name (str): ST-Link name
            
        Returns:
            Optional[Dict[str, Any]]: ST-Link details or None if not found
        """
        key = f'{runner_name}-{stlink_name}'
        
        if key in self.stlink_list:
            details = self.stlink_list[key]
            logger.info(f"Found ST-Link details for {stlink_name}: {details}")
            return details
        else:
            logger.error(f"No ST-Link details found for key '{key}'")
            return None
    
    def open_serial_connection(self, port: str, baudrate: int = 115200) -> Optional[serial.Serial]:
        """
        Open serial connection for verification.
        
        Args:
            port (str): Serial port name
            baudrate (int): Baud rate for serial communication
            
        Returns:
            Optional[serial.Serial]: Serial connection object or None if failed
        """
        try:
            ser = serial.Serial(port, baudrate, timeout=1)
            logger.info(f"Serial connection opened on port {port}")
            return ser
        except serial.SerialException as e:
            logger.error(f"Error opening serial port {port}: {e}")
            return None
    
    def close_serial_connection(self, ser: serial.Serial) -> None:
        """
        Close serial connection.
        
        Args:
            ser (serial.Serial): Serial connection object
        """
        try:
            if ser and ser.is_open:
                ser.close()
                logger.info("Serial connection closed")
        except Exception as e:
            logger.error(f"Error closing serial connection: {e}")
    
    def initialize_stlink(self, runner_name: str, stlink_name: str) -> Tuple[Optional[serial.Serial], Optional[str]]:
        """
        Initialize ST-Link connection and return serial connection.
        
        Args:
            runner_name (str): Runner name
            stlink_name (str): ST-Link name
            
        Returns:
            Tuple[Optional[serial.Serial], Optional[str]]: Serial connection and ST-Link SN
        """
        # Get ST-Link details
        stlink_details = self.get_stlink_details(runner_name, stlink_name)
        if not stlink_details:
            return None, None
        
        stlink_port = stlink_details.get('port')
        stlink_sn = stlink_details.get('sn')
        
        if not stlink_sn:
            logger.error("ST-Link serial number not found in configuration")
            return None, None
        
        # Check ST-Link connection
        if not self.check_st_link_connection(stlink_sn):
            return None, None
        
        # Verify STM32 connection
        if not self.verify_stm32_connection(stlink_sn):
            return None, None
        
        # Open serial connection if port is available
        ser = None
        if stlink_port:
            ser = self.open_serial_connection(stlink_port)
        
        return ser, stlink_sn


def main():
    """Demonstrate the usage of the STLinkHandler class."""
    handler = STLinkHandler()
    
    # Example usage
    runner_name = os.getenv("RUNNER_NAME", "default")
    stlink_name = os.getenv("STLINK_NAME", "default")
    
    ser, stlink_sn = handler.initialize_stlink(runner_name, stlink_name)
    
    if ser and stlink_sn:
        print(f"ST-Link initialized successfully: {stlink_sn}")
        handler.close_serial_connection(ser)
    else:
        print("Failed to initialize ST-Link")


if __name__ == "__main__":
    main()
