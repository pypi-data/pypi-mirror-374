"""
Flash memory checker module for STM32 programming system.

This module provides functionality to check flash memory values before programming
using STM32Programmer_CLI.exe.
"""

import subprocess
import time
import logging
from typing import Optional, Tuple
import struct
from .voice_announcer import VoiceAnnouncer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FlashChecker:
    """Class to handle flash memory value checking."""
    
    def __init__(self, programmer_cli: str = "STM32Programmer_CLI.exe", voice_announcer: Optional[VoiceAnnouncer] = None):
        """
        Initialize the flash checker.
        
        Args:
            programmer_cli (str): Path to STM32Programmer_CLI.exe
            voice_announcer (Optional[VoiceAnnouncer]): Voice announcer instance for status announcements
        """
        self.programmer_cli = programmer_cli
        self.max_retries = 10
        self.retry_delay = 2
        self.voice_announcer = voice_announcer
        # Read serial address from config.ini if available
        self.serial_address = "0x080232c4"  # Default from config.ini
        try:
            import configparser
            config = configparser.ConfigParser()
            if config.read('config.ini'):
                self.serial_address = config.get('FLASH_CHECK', 'serial_address', fallback="0x080232c4")
        except Exception:
            pass
        
    def read_flash_value(self, stlink_sn: str, address: str) -> Optional[int]:
        """
        Read 4-byte value from flash memory at specified address.
        
        Args:
            stlink_sn (str): ST-Link serial number
            address (str): Flash address in hex format (e.g., "0x08000000")
            
        Returns:
            Optional[int]: 4-byte value as integer, or None if failed
        """
        try:
            # Build command to read 4 bytes from flash with hardware reset
            cmd = [
                self.programmer_cli,
                '-c', 'port=SWD',
                f'sn={stlink_sn}',
                'reset=HWrst',  # Hardware reset before reading
                '-r', address, '4', 'temp_flash_read.bin'
            ]
            
            logger.info(f"Reading flash value at address {address}")
            logger.info(f"Command: {' '.join(cmd)}")
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                # Read the binary file and extract 4-byte value
                try:
                    with open('temp_flash_read.bin', 'rb') as f:
                        data = f.read(4)
                        if len(data) == 4:
                            # Convert little-endian 4-byte value to integer
                            value = struct.unpack('<I', data)[0]
                            logger.info(f"Read value from {address}: 0x{value:08X}")
                            return value
                        else:
                            logger.error(f"Invalid data length: {len(data)} bytes")
                            return None
                except Exception as e:
                    logger.error(f"Error reading binary file: {e}")
                    return None
            else:
                logger.error(f"Failed to read flash value: {result.stderr}")
                
                # Announce board not connected if voice announcer is available
                if self.voice_announcer:
                    logger.info("Announcing board not connected...")
                    self.voice_announcer.announce_board_not_connected()
                
                return None
                
        except subprocess.TimeoutExpired:
            logger.error("Flash read operation timeout")
            return None
        except Exception as e:
            logger.error(f"Error reading flash value: {e}")
            return None
        finally:
            # Clean up temporary file
            try:
                import os
                if os.path.exists('temp_flash_read.bin'):
                    os.remove('temp_flash_read.bin')
            except Exception:
                pass
    
    def check_flash_value(self, stlink_sn: str, address: str, expected_value: int, 
                         max_retries: int = 10, retry_delay: int = 2) -> Tuple[bool, Optional[int]]:
        """
        Check if flash value matches expected value, retry until different value is read.
        
        Args:
            stlink_sn (str): ST-Link serial number
            address (str): Flash address in hex format
            expected_value (int): Expected 4-byte value
            max_retries (int): Maximum number of retry attempts
            retry_delay (int): Delay between retries in seconds
            
        Returns:
            Tuple[bool, Optional[int]]: (should_program, last_read_value)
                - should_program: True if programming is needed (value doesn't match)
                - last_read_value: Last value read from flash
        """
        logger.info(f"Checking flash value at {address}")
        logger.info(f"Expected value: 0x{expected_value:08X}")
        logger.info(f"Max retries: {max_retries}, Retry delay: {retry_delay}s")
        
        for attempt in range(max_retries):
            logger.info(f"Attempt {attempt + 1}/{max_retries}")
            
            # Read current value from flash
            current_value = self.read_flash_value(stlink_sn, address)
            
            if current_value is None:
                logger.warning(f"Failed to read flash value on attempt {attempt + 1}")
                if attempt < max_retries - 1:
                    logger.info(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                continue
            
            logger.info(f"Current value: 0x{current_value:08X}")
            
            # Check if value matches expected value
            if current_value == expected_value:
                logger.info("Flash value matches expected value - board already programmed")
                
                # Read serial number from serial_address
                serial_number = self.read_serial_ascii(stlink_sn)
                
                if serial_number is None:
                    logger.error("Failed to read serial number - treating as invalid programming")
                    if self.voice_announcer:
                        self.voice_announcer.announce_invalid_programming()
                    return False, None  # Stop programming due to invalid serial
                
                # Validate serial number (must be 0001-9999)
                if not self.validate_serial(serial_number):
                    logger.error(f"Invalid serial number: {serial_number}")
                    if self.voice_announcer:
                        self.voice_announcer.announce_invalid_programming()
                    return False, None  # Stop programming due to invalid serial
                
                # Serial is valid, announce board completion with serial number
                logger.info(f"Board completed with serial number: {serial_number}")
                if self.voice_announcer:
                    self.voice_announcer.announce_board_completed_with_serial(serial_number)
                
                # Wait and read again to see if value changes
                if attempt < max_retries - 1:
                    logger.info(f"Waiting {retry_delay} seconds before next check...")
                    time.sleep(retry_delay)
                    
                    # Read again to check for change
                    next_value = self.read_flash_value(stlink_sn, address)
                    if next_value is not None and next_value != current_value:
                        logger.info(f"Value changed from 0x{current_value:08X} to 0x{next_value:08X} - programming needed")
                        return True, next_value
                    else:
                        logger.info("Value did not change - continuing to check...")
                        continue
                else:
                    logger.info("Max retries reached - no programming needed")
                    return False, current_value
            else:
                logger.info("Flash value differs from expected value - programming needed")
                return True, current_value
        
        logger.error("Failed to read flash value after all retries")
        return False, None
    
    def read_serial_ascii(self, stlink_sn: str) -> Optional[str]:
        """
        Read 4-byte ASCII serial number from flash memory at serial_address.
        
        Args:
            stlink_sn (str): ST-Link serial number
            
        Returns:
            Optional[str]: 4-digit ASCII serial number, or None if failed
        """
        try:
            # Build command to read 4 bytes from serial address
            cmd = [
                self.programmer_cli,
                '-c', 'port=SWD',
                f'sn={stlink_sn}',
                'reset=HWrst',  # Hardware reset before reading
                '-r', self.serial_address, '4', 'temp_serial_read.bin'
            ]
            
            logger.info(f"Reading serial number at address {self.serial_address}")
            logger.info(f"Command: {' '.join(cmd)}")
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                # Read the binary file and extract 4-byte ASCII value
                try:
                    with open('temp_serial_read.bin', 'rb') as f:
                        data = f.read(4)
                        if len(data) == 4:
                            # Convert bytes to ASCII string
                            try:
                                serial_str = data.decode('ascii')
                                logger.info(f"Read serial from {self.serial_address}: {serial_str}")
                                return serial_str
                            except UnicodeDecodeError:
                                logger.error(f"Invalid ASCII data: {data.hex()}")
                                return None
                        else:
                            logger.error(f"Invalid data length: {len(data)} bytes")
                            return None
                except Exception as e:
                    logger.error(f"Error reading serial binary file: {e}")
                    return None
            else:
                logger.error(f"Failed to read serial value: {result.stderr}")
                return None
                
        except subprocess.TimeoutExpired:
            logger.error("Serial read operation timeout")
            return None
        except Exception as e:
            logger.error(f"Error reading serial value: {e}")
            return None
        finally:
            # Clean up temporary file
            try:
                import os
                if os.path.exists('temp_serial_read.bin'):
                    os.remove('temp_serial_read.bin')
            except Exception:
                pass
    
    def validate_serial(self, serial_str: str) -> bool:
        """
        Validate that serial number is between 0001 and 9999.
        
        Args:
            serial_str (str): Serial number string to validate
            
        Returns:
            bool: True if serial is valid (0001-9999), False otherwise
        """
        try:
            # Check if it's exactly 4 digits
            if len(serial_str) != 4 or not serial_str.isdigit():
                logger.warning(f"Invalid serial format: {serial_str}")
                return False
            
            serial_num = int(serial_str)
            # Valid range is 0001 to 9999 (0000 is invalid)
            is_valid = 1 <= serial_num <= 9999
            
            if not is_valid:
                logger.warning(f"Serial number out of valid range (0001-9999): {serial_str}")
            
            return is_valid
        except Exception as e:
            logger.error(f"Error validating serial: {e}")
            return False
    
    def verify_flash_programming(self, stlink_sn: str, address: str, expected_value: int) -> bool:
        """
        Verify that flash programming was successful by reading the value.
        
        Args:
            stlink_sn (str): ST-Link serial number
            address (str): Flash address in hex format
            expected_value (int): Expected 4-byte value after programming
            
        Returns:
            bool: True if verification successful, False otherwise
        """
        logger.info("Verifying flash programming...")
        
        # Wait a moment for programming to complete
        time.sleep(1)
        
        # Read the value
        current_value = self.read_flash_value(stlink_sn, address)
        
        if current_value is None:
            logger.error("Failed to read flash value for verification")
            return False
        
        if current_value == expected_value:
            logger.info("Flash programming verification successful")
            return True
        else:
            logger.error(f"Flash programming verification failed")
            logger.error(f"Expected: 0x{expected_value:08X}, Got: 0x{current_value:08X}")
            return False


def main():
    """Demonstrate the usage of the FlashChecker class."""
    from .voice_announcer import VoiceAnnouncer
    
    # Initialize voice announcer for testing
    voice_announcer = VoiceAnnouncer()
    checker = FlashChecker(voice_announcer=voice_announcer)
    
    # Test with simulated expected value match
    print("Testing with expected value match scenario...")
    stlink_sn = "066AFF303550503043035447"
    address = "0x08020000"
    expected_value = 0x20030000
    
    # Simulate the scenario where expected value is found
    print(f"Simulating flash read: 0x{expected_value:08X}")
    print("Expected value matches - should announce '완료된 보드입니다.'")
    
    # Test the voice announcement directly
    if voice_announcer.available:
        success = voice_announcer.announce_board_completed()
        if success:
            print("Voice announcement test successful!")
        else:
            print("Voice announcement test failed!")
    else:
        print("Voice announcer not available")
    
    # Test with different value
    print("\nTesting with different value scenario...")
    different_value = 0x12345678
    print(f"Simulating flash read: 0x{different_value:08X}")
    print("Expected value differs - should proceed with programming")


if __name__ == "__main__":
    main()
