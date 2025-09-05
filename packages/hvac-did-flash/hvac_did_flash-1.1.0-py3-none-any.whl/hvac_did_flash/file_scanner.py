"""
Firmware file scanning module for STM32 programming system.

This module provides functionality to scan the 'upload_firmware' folder
for .bin files and extract unique serial numbers from filenames.
"""

import os
import re
import glob
from typing import List, Dict, Optional, Tuple
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def scan_firmware_files(firmware_dir: str = "upload_firmware", pattern: str = "*.bin") -> List[str]:
    """
    Scan the firmware directory for files matching the pattern.
    
    Args:
        firmware_dir (str): Directory containing firmware files
        pattern (str): File pattern to match
        
    Returns:
        List[str]: List of matching file paths
    """
    if not os.path.exists(firmware_dir):
        logger.warning(f"Firmware directory '{firmware_dir}' does not exist")
        return []
        
    file_pattern = os.path.join(firmware_dir, pattern)
    files = glob.glob(file_pattern)
    
    logger.info(f"Found {len(files)} files matching '{pattern}' in {firmware_dir}")
    return files


def extract_serial_number(filename: str) -> Optional[str]:
    """
    Extract serial number from filename using regex pattern.
    
    Args:
        filename (str): The filename to extract serial number from
        
    Returns:
        Optional[str]: Extracted serial number or None if not found
    """
    serial_pattern = re.compile(r'(\d{2}[A-Z]\d{6})')
    match = serial_pattern.search(filename)
    if match:
        serial_number = match.group(1)
        logger.debug(f"Extracted serial number '{serial_number}' from '{filename}'")
        return serial_number
    else:
        logger.warning(f"No serial number found in filename: {filename}")
        return None


class FirmwareFileScanner:
    """Class to handle firmware file scanning and serial number extraction."""
    
    def __init__(self, firmware_dir: str = "upload_firmware"):
        """
        Initialize the firmware file scanner.
        
        Args:
            firmware_dir (str): Directory containing firmware files
        """
        self.firmware_dir = firmware_dir
        self.serial_pattern = re.compile(r'(\d{2}[A-Z]\d{6})')
        
    def scan_firmware_files(self) -> List[str]:
        """
        Scan the firmware directory for .bin files.
        
        Returns:
            List[str]: List of .bin file paths
        """
        if not os.path.exists(self.firmware_dir):
            logger.warning(f"Firmware directory '{self.firmware_dir}' does not exist")
            return []
            
        pattern = os.path.join(self.firmware_dir, "*.bin")
        bin_files = glob.glob(pattern)
        
        logger.info(f"Found {len(bin_files)} .bin files in {self.firmware_dir}")
        return bin_files
    
    def extract_serial_number(self, filename: str) -> Optional[str]:
        """
        Extract serial number from filename using regex pattern.
        
        Args:
            filename (str): The filename to extract serial number from
            
        Returns:
            Optional[str]: Extracted serial number or None if not found
        """
        match = self.serial_pattern.search(filename)
        if match:
            serial_number = match.group(1)
            logger.debug(f"Extracted serial number '{serial_number}' from '{filename}'")
            return serial_number
        else:
            logger.warning(f"No serial number found in filename: {filename}")
            return None
    
    def verify_file_uniqueness(self, bin_files: List[str]) -> Dict[str, List[str]]:
        """
        Verify uniqueness of files based on serial numbers.
        
        Args:
            bin_files (List[str]): List of .bin file paths
            
        Returns:
            Dict[str, List[str]]: Dictionary mapping serial numbers to file paths
        """
        serial_to_files = {}
        duplicate_serials = []
        
        for file_path in bin_files:
            filename = os.path.basename(file_path)
            serial_number = self.extract_serial_number(filename)
            
            if serial_number:
                if serial_number in serial_to_files:
                    duplicate_serials.append(serial_number)
                    serial_to_files[serial_number].append(file_path)
                    logger.warning(f"Duplicate serial number '{serial_number}' found in files: {serial_to_files[serial_number]}")
                else:
                    serial_to_files[serial_number] = [file_path]
        
        if duplicate_serials:
            logger.error(f"Found duplicate serial numbers: {duplicate_serials}")
        else:
            logger.info("All serial numbers are unique")
            
        return serial_to_files
    
    def get_firmware_info(self) -> List[Dict[str, str]]:
        """
        Get comprehensive information about all firmware files.
        
        Returns:
            List[Dict[str, str]]: List of dictionaries containing file information
        """
        bin_files = self.scan_firmware_files()
        firmware_info = []
        
        for file_path in bin_files:
            filename = os.path.basename(file_path)
            serial_number = self.extract_serial_number(filename)
            
            info = {
                'file_path': file_path,
                'filename': filename,
                'serial_number': serial_number,
                'file_size': os.path.getsize(file_path) if os.path.exists(file_path) else 0
            }
            firmware_info.append(info)
            
        return firmware_info


def main():
    """Demonstrate the usage of the FirmwareFileScanner class."""
    scanner = FirmwareFileScanner()
    
    # Scan for firmware files
    bin_files = scanner.scan_firmware_files()
    print(f"Found {len(bin_files)} .bin files")
    
    # Get detailed information
    firmware_info = scanner.get_firmware_info()
    for info in firmware_info:
        print(f"File: {info['filename']}")
        print(f"  Serial: {info['serial_number']}")
        print(f"  Size: {info['file_size']} bytes")
        print()
    
    # Verify uniqueness
    serial_to_files = scanner.verify_file_uniqueness(bin_files)
    print(f"Unique serial numbers: {len(serial_to_files)}")


if __name__ == "__main__":
    main()
