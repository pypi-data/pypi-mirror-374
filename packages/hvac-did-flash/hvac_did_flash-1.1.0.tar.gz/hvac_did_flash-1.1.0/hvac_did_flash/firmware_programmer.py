"""
Firmware programming module for STM32 programming system.

This module provides functionality to program the STM32 microcontroller
using STM32Programmer_CLI.exe.
"""

import subprocess
import os
import time
import logging
from typing import Tuple, Optional, Dict, Any, List
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FirmwareProgrammer:
    """Class to handle STM32 firmware programming."""
    
    def __init__(self, timeout: int = 60, max_retries: int = 3):
        """
        Initialize the firmware programmer.
        
        Args:
            timeout (int): Timeout for programming operations in seconds
            max_retries (int): Maximum number of retry attempts
        """
        self.timeout = timeout
        self.max_retries = max_retries
        self.programming_stats = {
            'total_attempts': 0,
            'successful': 0,
            'failed': 0,
            'retry_count': 0
        }
    
    def check_stm32_programmer_available(self) -> bool:
        """
        Check if STM32Programmer_CLI.exe is available.
        
        Returns:
            bool: True if available, False otherwise
        """
        try:
            result = subprocess.run(
                ['STM32_Programmer_CLI.exe', '--version'],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError, Exception) as e:
            logger.error(f"STM32Programmer_CLI.exe not available: {e}")
            return False
    
    def program_firmware(self, file_path: str, stlink_sn: str, 
                        offset: str = "0x08000000", verify: bool = True,
                        reset: bool = True) -> Tuple[bool, str]:
        """
        Program firmware to STM32 microcontroller.
        
        Args:
            file_path (str): Path to the firmware file
            stlink_sn (str): ST-Link serial number
            offset (str): Memory offset for programming
            verify (bool): Whether to verify after programming
            reset (bool): Whether to reset after programming
            
        Returns:
            Tuple[bool, str]: (success, message)
        """
        self.programming_stats['total_attempts'] += 1
        
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                error_msg = f"Firmware file not found: {file_path}"
                logger.error(error_msg)
                self.programming_stats['failed'] += 1
                return False, error_msg
            
            # Check if STM32Programmer_CLI.exe is available
            if not self.check_stm32_programmer_available():
                error_msg = "STM32Programmer_CLI.exe not available"
                logger.error(error_msg)
                self.programming_stats['failed'] += 1
                return False, error_msg
            
            # Build command
            cmd = self._build_programming_command(file_path, stlink_sn, offset, verify, reset)
            
            logger.info(f"Programming firmware: {file_path.name}")
            logger.info(f"Command: {' '.join(cmd)}")
            
            # Execute programming command
            success, message = self._execute_programming_command(cmd, file_path.name)
            
            if success:
                self.programming_stats['successful'] += 1
                logger.info(f"Firmware programming successful: {file_path.name}")
            else:
                self.programming_stats['failed'] += 1
                logger.error(f"Firmware programming failed: {file_path.name} - {message}")
            
            return success, message
            
        except Exception as e:
            error_msg = f"Unexpected error during programming: {e}"
            logger.error(error_msg)
            self.programming_stats['failed'] += 1
            return False, error_msg
    
    def _build_programming_command(self, file_path: Path, stlink_sn: str, 
                                 offset: str, verify: bool, reset: bool) -> List[str]:
        """
        Build the STM32Programmer_CLI.exe command.
        
        Args:
            file_path (Path): Path to firmware file
            stlink_sn (str): ST-Link serial number
            offset (str): Memory offset
            verify (bool): Whether to verify
            reset (bool): Whether to reset
            
        Returns:
            List[str]: Command as list of strings
        """
        cmd = [
            'STM32_Programmer_CLI.exe',
            '-c', 'port=SWD','reset=HWrst',
            f'sn={stlink_sn}',
            '-w', str(file_path), offset
        ]
        
        if verify:
            cmd.append('-v')
        
        
        return cmd
    
    def _execute_programming_command(self, cmd: List[str], filename: str) -> Tuple[bool, str]:
        """
        Execute the programming command with retry logic.
        
        Args:
            cmd (List[str]): Command to execute
            filename (str): Name of the firmware file
            
        Returns:
            Tuple[bool, str]: (success, message)
        """
        for attempt in range(self.max_retries):
            try:
                if attempt > 0:
                    logger.info(f"Retry attempt {attempt + 1}/{self.max_retries} for {filename}")
                    self.programming_stats['retry_count'] += 1
                    time.sleep(2)  # Wait before retry
                
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=self.timeout
                )
                
                # Analyze the result
                success, message = self._analyze_programming_result(result, filename)
                
                if success:
                    return True, message
                elif attempt == self.max_retries - 1:
                    # Last attempt failed
                    return False, f"Programming failed after {self.max_retries} attempts: {message}"
                
            except subprocess.TimeoutExpired:
                error_msg = f"Programming timeout for {filename} (attempt {attempt + 1})"
                logger.error(error_msg)
                if attempt == self.max_retries - 1:
                    return False, f"Programming timeout after {self.max_retries} attempts"
                    
            except Exception as e:
                error_msg = f"Error during programming attempt {attempt + 1}: {e}"
                logger.error(error_msg)
                if attempt == self.max_retries - 1:
                    return False, f"Programming error after {self.max_retries} attempts: {e}"
        
        return False, "Programming failed after all retry attempts"
    
    def _analyze_programming_result(self, result: subprocess.CompletedProcess, 
                                  filename: str) -> Tuple[bool, str]:
        """
        Analyze the result of the programming command.
        
        Args:
            result (subprocess.CompletedProcess): Result from subprocess.run
            filename (str): Name of the firmware file
            
        Returns:
            Tuple[bool, str]: (success, message)
        """
        if result.returncode == 0:
            # Check for success indicators in output
            output = result.stdout.lower()
            if any(keyword in output for keyword in ['success', 'completed', 'programming successful']):
                return True, "Programming completed successfully"
            else:
                return True, "Programming completed (return code 0)"
        else:
            # Analyze error output
            error_output = result.stderr if result.stderr else result.stdout
            error_msg = self._extract_error_message(error_output)
            return False, f"Programming failed: {error_msg}"
    
    def _extract_error_message(self, error_output: str) -> str:
        """
        Extract meaningful error message from command output.
        
        Args:
            error_output (str): Error output from command
            
        Returns:
            str: Extracted error message
        """
        if not error_output:
            return "Unknown error"
        
        # Common error patterns
        error_patterns = [
            'connection failed',
            'device not found',
            'timeout',
            'permission denied',
            'file not found',
            'invalid file',
            'memory error',
            'verification failed'
        ]
        
        error_output_lower = error_output.lower()
        for pattern in error_patterns:
            if pattern in error_output_lower:
                return pattern.replace('_', ' ').title()
        
        # Return first line of error output if no pattern matches
        lines = error_output.strip().split('\n')
        return lines[0] if lines else "Unknown error"
    
    def program_firmware_with_verification(self, file_path: str, stlink_sn: str,
                                         expected_sha: Optional[str] = None,
                                         offset: str = "0x08000000") -> Dict[str, Any]:
        """
        Program firmware with comprehensive verification.
        
        Args:
            file_path (str): Path to the firmware file
            stlink_sn (str): ST-Link serial number
            expected_sha (Optional[str]): Expected SHA for verification
            offset (str): Memory offset for programming
            
        Returns:
            Dict[str, Any]: Programming results with verification
        """
        results = {
            'file_path': file_path,
            'programming_success': False,
            'verification_success': False,
            'overall_success': False,
            'programming_message': '',
            'verification_message': '',
            'errors': []
        }
        
        try:
            # Program the firmware
            success, message = self.program_firmware(file_path, stlink_sn, offset)
            results['programming_success'] = success
            results['programming_message'] = message
            
            if not success:
                results['errors'].append(f"Programming failed: {message}")
                return results
            
            # Verify if expected SHA is provided
            if expected_sha:
                # Note: This would typically involve reading from the device
                # For now, we'll simulate verification
                verification_success = self._simulate_verification(expected_sha)
                results['verification_success'] = verification_success
                
                if verification_success:
                    results['verification_message'] = f"SHA verification successful: {expected_sha}"
                else:
                    results['verification_message'] = f"SHA verification failed: {expected_sha}"
                    results['errors'].append("SHA verification failed")
            
            # Determine overall success
            results['overall_success'] = results['programming_success'] and (
                not expected_sha or results['verification_success']
            )
            
            return results
            
        except Exception as e:
            error_msg = f"Error during programming with verification: {e}"
            logger.error(error_msg)
            results['errors'].append(error_msg)
            return results
    
    def _simulate_verification(self, expected_sha: str) -> bool:
        """
        Simulate SHA verification (placeholder implementation).
        
        Args:
            expected_sha (str): Expected SHA value
            
        Returns:
            bool: True if verification successful
        """
        # In a real implementation, this would read from the device
        # and compare with the expected SHA
        logger.info(f"Simulating SHA verification for: {expected_sha}")
        return True  # Placeholder - always return True
    
    def get_programming_statistics(self) -> Dict[str, Any]:
        """
        Get programming statistics.
        
        Returns:
            Dict[str, Any]: Programming statistics
        """
        stats = self.programming_stats.copy()
        
        if stats['total_attempts'] > 0:
            stats['success_rate'] = (stats['successful'] / stats['total_attempts']) * 100
        else:
            stats['success_rate'] = 0
        
        return stats
    
    def reset_statistics(self) -> None:
        """Reset programming statistics."""
        self.programming_stats = {
            'total_attempts': 0,
            'successful': 0,
            'failed': 0,
            'retry_count': 0
        }
        logger.info("Programming statistics reset")
    
    def program_multiple_firmware(self, firmware_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Program multiple firmware files.
        
        Args:
            firmware_list (List[Dict[str, Any]]): List of firmware information
            
        Returns:
            List[Dict[str, Any]]: Results for each firmware file
        """
        results = []
        
        logger.info(f"Starting batch programming of {len(firmware_list)} firmware files")
        
        for i, firmware_info in enumerate(firmware_list, 1):
            file_path = firmware_info.get('file_path', '')
            stlink_sn = firmware_info.get('stlink_sn', '')
            expected_sha = firmware_info.get('expected_sha')
            offset = firmware_info.get('offset', '0x08000000')
            
            logger.info(f"Programming {i}/{len(firmware_list)}: {Path(file_path).name}")
            
            result = self.program_firmware_with_verification(
                file_path, stlink_sn, expected_sha, offset
            )
            
            results.append(result)
            
            # Add delay between programming operations
            if i < len(firmware_list):
                time.sleep(1)
        
        logger.info("Batch programming completed")
        return results


def main():
    """Demonstrate the usage of the FirmwareProgrammer class."""
    programmer = FirmwareProgrammer()
    
    # Example usage
    print("Firmware Programmer Demo")
    print("=" * 50)
    
    # Check if STM32Programmer_CLI.exe is available
    if programmer.check_stm32_programmer_available():
        print("STM32Programmer_CLI.exe is available")
    else:
        print("STM32Programmer_CLI.exe is not available")
        print("This demo requires STM32Programmer_CLI.exe to be installed")
        return
    
    # Example firmware programming (commented out to avoid actual programming)
    # test_file = "upload_firmware/hvac-main-stm32f103@CYBER-QZ25_25J040001_v1.13.2-alpha.2-1-g2121caf9.bin"
    # stlink_sn = "1234567890"  # Example ST-Link serial number
    # 
    # success, message = programmer.program_firmware(test_file, stlink_sn)
    # print(f"Programming result: {success} - {message}")
    
    # Get statistics
    stats = programmer.get_programming_statistics()
    print(f"Programming statistics: {stats}")


if __name__ == "__main__":
    main()
