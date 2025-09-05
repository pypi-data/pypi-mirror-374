"""
Serial port communication module for STM32 programming system.

This module provides functionality to handle serial port communication
for firmware verification.
"""

import serial
import time
import logging
from typing import Optional, List, Dict, Any
import threading
import queue

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SerialCommunicator:
    """Class to handle serial port communication for firmware verification."""
    
    def __init__(self, port: str, baudrate: int = 115200, timeout: float = 1.0):
        """
        Initialize the serial communicator.
        
        Args:
            port (str): Serial port name
            baudrate (int): Baud rate for serial communication
            timeout (float): Timeout for serial operations
        """
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial_connection = None
        self.is_connected = False
        self.read_thread = None
        self.read_queue = queue.Queue()
        self.stop_reading = False
        
    def open(self) -> bool:
        """
        Open serial port connection.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            self.serial_connection = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout
            )
            self.is_connected = True
            logger.info(f"Serial connection opened on port {self.port}")
            
            # Start reading thread
            self.stop_reading = False
            self.read_thread = threading.Thread(target=self._read_worker, daemon=True)
            self.read_thread.start()
            
            return True
            
        except serial.SerialException as e:
            logger.error(f"Error opening serial port {self.port}: {e}")
            self.is_connected = False
            return False
        except Exception as e:
            logger.error(f"Unexpected error opening serial port: {e}")
            self.is_connected = False
            return False
    
    def close(self) -> None:
        """
        Close serial port connection.
        """
        try:
            self.stop_reading = True
            
            if self.read_thread and self.read_thread.is_alive():
                self.read_thread.join(timeout=2.0)
            
            if self.serial_connection and self.serial_connection.is_open:
                self.serial_connection.close()
                logger.info("Serial connection closed")
            
            self.is_connected = False
            
        except Exception as e:
            logger.error(f"Error closing serial connection: {e}")
    
    def _read_worker(self) -> None:
        """
        Worker thread for reading serial data.
        """
        while not self.stop_reading and self.is_connected:
            try:
                if self.serial_connection and self.serial_connection.in_waiting > 0:
                    line = self.serial_connection.readline().decode('utf-8').strip()
                    if line:
                        self.read_queue.put(line)
                        logger.debug(f"Received: {line}")
                time.sleep(0.01)  # Small delay to prevent excessive CPU usage
                
            except Exception as e:
                logger.error(f"Error in read worker: {e}")
                break
    
    def read(self, timeout: Optional[float] = None) -> Optional[str]:
        """
        Read data from serial port.
        
        Args:
            timeout (Optional[float]): Timeout for reading operation
            
        Returns:
            Optional[str]: Received data or None if timeout
        """
        try:
            if timeout is None:
                timeout = self.timeout
            
            data = self.read_queue.get(timeout=timeout)
            return data
            
        except queue.Empty:
            return None
        except Exception as e:
            logger.error(f"Error reading from serial port: {e}")
            return None
    
    def read_all(self, timeout: float = 1.0) -> List[str]:
        """
        Read all available data from serial port.
        
        Args:
            timeout (float): Timeout for reading operation
            
        Returns:
            List[str]: List of received data lines
        """
        data_lines = []
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            data = self.read(timeout=0.1)
            if data:
                data_lines.append(data)
            else:
                break
        
        return data_lines
    
    def write(self, data: str) -> bool:
        """
        Write data to serial port.
        
        Args:
            data (str): Data to write
            
        Returns:
            bool: True if write successful, False otherwise
        """
        try:
            if not self.is_connected or not self.serial_connection:
                logger.error("Serial connection not established")
                return False
            
            self.serial_connection.write(data.encode('utf-8'))
            logger.debug(f"Sent: {data}")
            return True
            
        except Exception as e:
            logger.error(f"Error writing to serial port: {e}")
            return False
    
    def verify_firmware(self, expected_sha: str, timeout: float = 6.0) -> bool:
        """
        Verify firmware using serial communication.
        
        Args:
            expected_sha (str): Expected SHA value to verify
            timeout (float): Timeout for verification
            
        Returns:
            bool: True if verification successful, False otherwise
        """
        if not self.is_connected:
            logger.error("Serial connection not established")
            return False
        
        logger.info("Starting firmware verification via serial communication")
        sha_found = False
        start_time = time.time()
        
        try:
            while time.time() - start_time < timeout:
                data = self.read(timeout=0.1)
                if data:
                    logger.info(f"Received: {data}")
                    if expected_sha and expected_sha in data:
                        sha_found = True
                        logger.info(f"Expected SHA '{expected_sha}' found in output")
                        break
                        
        except Exception as e:
            logger.error(f"Error during firmware verification: {e}")
            return False
        
        if sha_found:
            logger.info(f"Firmware verification successful: {expected_sha}")
        else:
            logger.warning(f"Firmware verification failed: SHA '{expected_sha}' not found")
        
        return sha_found
    
    def get_connection_info(self) -> Dict[str, Any]:
        """
        Get serial connection information.
        
        Returns:
            Dict[str, Any]: Connection information dictionary
        """
        info = {
            'port': self.port,
            'baudrate': self.baudrate,
            'timeout': self.timeout,
            'is_connected': self.is_connected,
            'has_connection': self.serial_connection is not None
        }
        
        if self.serial_connection:
            info.update({
                'is_open': self.serial_connection.is_open,
                'in_waiting': self.serial_connection.in_waiting,
                'bytesize': self.serial_connection.bytesize,
                'parity': self.serial_connection.parity,
                'stopbits': self.serial_connection.stopbits
            })
        
        return info


def main():
    """Demonstrate the usage of the SerialCommunicator class."""
    # Example usage
    communicator = SerialCommunicator("COM3", 115200)
    
    if communicator.open():
        print("Serial connection established")
        
        # Get connection info
        info = communicator.get_connection_info()
        print(f"Connection info: {info}")
        
        # Example verification
        success = communicator.verify_firmware("2121caf9", timeout=5.0)
        print(f"Verification result: {success}")
        
        communicator.close()
    else:
        print("Failed to establish serial connection")


if __name__ == "__main__":
    main()
