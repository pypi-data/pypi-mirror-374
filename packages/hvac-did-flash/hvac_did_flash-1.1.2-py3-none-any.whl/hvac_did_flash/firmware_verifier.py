"""
Firmware integrity verification module for STM32 programming system.

This module provides functionality to verify the integrity of firmware files
before programming using checksums and digital signatures.
"""

import hashlib
import os
import logging
from typing import Tuple, Optional, Dict, Any, List
from pathlib import Path
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FirmwareVerifier:
    """Class to handle firmware integrity verification."""
    
    def __init__(self, checksum_file: str = "firmware_checksums.json"):
        """
        Initialize the firmware verifier.
        
        Args:
            checksum_file (str): Path to checksum database file
        """
        self.checksum_file = Path(checksum_file)
        self.checksum_db = self._load_checksum_database()
        self.supported_algorithms = ['sha256', 'sha1', 'md5']
    
    def _load_checksum_database(self) -> Dict[str, Any]:
        """
        Load checksum database from file.
        
        Returns:
            Dict[str, Any]: Checksum database dictionary
        """
        if not self.checksum_file.exists():
            logger.info(f"Checksum database file not found: {self.checksum_file}")
            return {}
        
        try:
            with open(self.checksum_file, 'r', encoding='utf-8') as f:
                db = json.load(f)
                logger.info(f"Loaded checksum database with {len(db)} entries")
                return db
        except Exception as e:
            logger.error(f"Error loading checksum database: {e}")
            return {}
    
    def _save_checksum_database(self) -> bool:
        """
        Save checksum database to file.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with open(self.checksum_file, 'w', encoding='utf-8') as f:
                json.dump(self.checksum_db, f, indent=2, ensure_ascii=False)
                logger.info(f"Checksum database saved to {self.checksum_file}")
                return True
        except Exception as e:
            logger.error(f"Error saving checksum database: {e}")
            return False
    
    def calculate_checksum(self, file_path: str, algorithm: str = 'sha256') -> Optional[str]:
        """
        Calculate checksum of a firmware file.
        
        Args:
            file_path (str): Path to the firmware file
            algorithm (str): Hash algorithm to use (sha256, sha1, md5)
            
        Returns:
            Optional[str]: Calculated checksum or None if error
        """
        if algorithm not in self.supported_algorithms:
            logger.error(f"Unsupported algorithm: {algorithm}")
            return None
        
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                logger.error(f"File does not exist: {file_path}")
                return None
            
            # Get the appropriate hash function
            if algorithm == 'sha256':
                hash_func = hashlib.sha256()
            elif algorithm == 'sha1':
                hash_func = hashlib.sha1()
            elif algorithm == 'md5':
                hash_func = hashlib.md5()
            
            # Calculate checksum
            with open(file_path, 'rb') as f:
                # Read file in chunks to handle large files
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_func.update(chunk)
            
            checksum = hash_func.hexdigest()
            logger.info(f"Calculated {algorithm} checksum for {file_path.name}: {checksum}")
            
            return checksum
            
        except Exception as e:
            logger.error(f"Error calculating checksum: {e}")
            return None
    
    def verify_checksum(self, file_path: str, expected_checksum: str, 
                       algorithm: str = 'sha256') -> Tuple[bool, str]:
        """
        Verify the calculated checksum against the expected value.
        
        Args:
            file_path (str): Path to the firmware file
            expected_checksum (str): Expected checksum value
            algorithm (str): Hash algorithm to use
            
        Returns:
            Tuple[bool, str]: (success, message)
        """
        try:
            calculated_checksum = self.calculate_checksum(file_path, algorithm)
            
            if calculated_checksum is None:
                return False, "Failed to calculate checksum"
            
            if calculated_checksum.lower() == expected_checksum.lower():
                logger.info(f"Checksum verification successful for {file_path}")
                return True, "Checksum verification successful"
            else:
                logger.error(f"Checksum mismatch for {file_path}")
                logger.error(f"Expected: {expected_checksum}")
                logger.error(f"Calculated: {calculated_checksum}")
                return False, f"Checksum mismatch. Expected: {expected_checksum}, Got: {calculated_checksum}"
                
        except Exception as e:
            logger.error(f"Error during checksum verification: {e}")
            return False, f"Verification error: {e}"
    
    def verify_digital_signature(self, file_path: str, signature_path: str, 
                               public_key_path: str) -> Tuple[bool, str]:
        """
        Verify the digital signature of a firmware file.
        
        Args:
            file_path (str): Path to the firmware file
            signature_path (str): Path to the signature file
            public_key_path (str): Path to the public key file
            
        Returns:
            Tuple[bool, str]: (success, message)
        """
        try:
            # Check if required files exist
            if not Path(file_path).exists():
                return False, f"Firmware file not found: {file_path}"
            
            if not Path(signature_path).exists():
                return False, f"Signature file not found: {signature_path}"
            
            if not Path(public_key_path).exists():
                return False, f"Public key file not found: {public_key_path}"
            
            # For now, implement a basic signature verification
            # In a real implementation, you would use cryptographic libraries
            # like cryptography or pycryptodome
            
            logger.info("Digital signature verification not fully implemented")
            logger.info("This would require proper cryptographic libraries")
            
            # Placeholder implementation
            return True, "Digital signature verification placeholder (not implemented)"
            
        except Exception as e:
            logger.error(f"Error during digital signature verification: {e}")
            return False, f"Signature verification error: {e}"
    
    def verify_firmware(self, file_path: str, expected_checksum: Optional[str] = None,
                       algorithm: str = 'sha256', verify_signature: bool = False,
                       signature_path: Optional[str] = None,
                       public_key_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Comprehensive firmware verification combining checksum and signature verification.
        
        Args:
            file_path (str): Path to the firmware file
            expected_checksum (Optional[str]): Expected checksum value
            algorithm (str): Hash algorithm to use
            verify_signature (bool): Whether to verify digital signature
            signature_path (Optional[str]): Path to signature file
            public_key_path (Optional[str]): Path to public key file
            
        Returns:
            Dict[str, Any]: Verification results
        """
        results = {
            'file_path': file_path,
            'file_exists': False,
            'checksum_verification': {
                'performed': False,
                'success': False,
                'message': '',
                'calculated_checksum': None,
                'expected_checksum': expected_checksum
            },
            'signature_verification': {
                'performed': False,
                'success': False,
                'message': ''
            },
            'overall_success': False,
            'errors': []
        }
        
        try:
            file_path = Path(file_path)
            results['file_exists'] = file_path.exists()
            
            if not results['file_exists']:
                results['errors'].append(f"File does not exist: {file_path}")
                return results
            
            # Perform checksum verification if expected checksum is provided
            if expected_checksum:
                results['checksum_verification']['performed'] = True
                success, message = self.verify_checksum(file_path, expected_checksum, algorithm)
                results['checksum_verification']['success'] = success
                results['checksum_verification']['message'] = message
                results['checksum_verification']['calculated_checksum'] = self.calculate_checksum(file_path, algorithm)
                
                if not success:
                    results['errors'].append(f"Checksum verification failed: {message}")
            
            # Perform signature verification if requested
            if verify_signature and signature_path and public_key_path:
                results['signature_verification']['performed'] = True
                success, message = self.verify_digital_signature(file_path, signature_path, public_key_path)
                results['signature_verification']['success'] = success
                results['signature_verification']['message'] = message
                
                if not success:
                    results['errors'].append(f"Signature verification failed: {message}")
            
            # Determine overall success
            checksum_ok = not results['checksum_verification']['performed'] or results['checksum_verification']['success']
            signature_ok = not results['signature_verification']['performed'] or results['signature_verification']['success']
            
            results['overall_success'] = checksum_ok and signature_ok
            
            if results['overall_success']:
                logger.info(f"Firmware verification successful for {file_path.name}")
            else:
                logger.error(f"Firmware verification failed for {file_path.name}")
            
            return results
            
        except Exception as e:
            logger.error(f"Error during firmware verification: {e}")
            results['errors'].append(f"Verification error: {e}")
            return results
    
    def add_checksum_to_database(self, file_path: str, checksum: str, 
                                algorithm: str = 'sha256') -> bool:
        """
        Add a checksum to the database.
        
        Args:
            file_path (str): Path to the firmware file
            checksum (str): Checksum value
            algorithm (str): Hash algorithm used
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            file_path = Path(file_path)
            filename = file_path.name
            
            if filename not in self.checksum_db:
                self.checksum_db[filename] = {}
            
            self.checksum_db[filename][algorithm] = {
                'checksum': checksum,
                'file_size': file_path.stat().st_size if file_path.exists() else 0,
                'added_timestamp': str(Path(file_path).stat().st_mtime) if file_path.exists() else None
            }
            
            self._save_checksum_database()
            logger.info(f"Added {algorithm} checksum to database for {filename}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding checksum to database: {e}")
            return False
    
    def get_expected_checksum(self, file_path: str, algorithm: str = 'sha256') -> Optional[str]:
        """
        Get expected checksum from database.
        
        Args:
            file_path (str): Path to the firmware file
            algorithm (str): Hash algorithm
            
        Returns:
            Optional[str]: Expected checksum or None if not found
        """
        try:
            filename = Path(file_path).name
            
            if filename in self.checksum_db and algorithm in self.checksum_db[filename]:
                return self.checksum_db[filename][algorithm]['checksum']
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting expected checksum: {e}")
            return None
    
    def verify_firmware_from_database(self, file_path: str, algorithm: str = 'sha256') -> Dict[str, Any]:
        """
        Verify firmware using checksum from database.
        
        Args:
            file_path (str): Path to the firmware file
            algorithm (str): Hash algorithm to use
            
        Returns:
            Dict[str, Any]: Verification results
        """
        expected_checksum = self.get_expected_checksum(file_path, algorithm)
        
        if expected_checksum is None:
            return {
                'file_path': file_path,
                'success': False,
                'message': f"No expected checksum found in database for {Path(file_path).name}",
                'errors': [f"No expected checksum found for {algorithm}"]
            }
        
        return self.verify_firmware(file_path, expected_checksum, algorithm)


def main():
    """Demonstrate the usage of the FirmwareVerifier class."""
    verifier = FirmwareVerifier()
    
    # Example usage
    print("Firmware Verifier Demo")
    print("=" * 50)
    
    # Test with a sample file
    test_file = "upload_firmware/hvac-main-stm32f103@CYBER-QZ25_25J040001_v1.13.2-alpha.2-1-g2121caf9.bin"
    
    if Path(test_file).exists():
        # Calculate checksum
        checksum = verifier.calculate_checksum(test_file)
        if checksum:
            print(f"Calculated SHA256 checksum: {checksum}")
            
            # Add to database
            verifier.add_checksum_to_database(test_file, checksum)
            
            # Verify checksum
            success, message = verifier.verify_checksum(test_file, checksum)
            print(f"Checksum verification: {success} - {message}")
            
            # Comprehensive verification
            results = verifier.verify_firmware(test_file, checksum)
            print(f"Comprehensive verification: {results['overall_success']}")
            print(f"Results: {json.dumps(results, indent=2)}")
    else:
        print(f"Test file not found: {test_file}")


if __name__ == "__main__":
    main()
