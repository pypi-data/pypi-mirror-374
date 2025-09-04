"""
File handling module for STM32 programming system.

This module provides functionality to change file extensions from .bin to .xxx
after successful programming and handle file operations.
"""

import os
import shutil
import logging
from typing import Optional, List, Dict, Any
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FileHandler:
    """Class to handle file operations for the STM32 programming system."""
    
    def __init__(self, firmware_dir: str = "upload_firmware"):
        """
        Initialize the file handler.
        
        Args:
            firmware_dir (str): Directory containing firmware files
        """
        self.firmware_dir = Path(firmware_dir)
        self.backup_dir = self.firmware_dir / "backup"
        self.processed_dir = self.firmware_dir / "processed"
        
        # Create directories if they don't exist
        self.backup_dir.mkdir(exist_ok=True)
        self.processed_dir.mkdir(exist_ok=True)
    
    def change_file_extension(self, file_path: str, new_extension: str = "xxx") -> bool:
        """
        Change file extension from .bin to specified extension.
        
        Args:
            file_path (str): Path to the file to rename
            new_extension (str): New file extension (default: "xxx")
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                logger.error(f"File does not exist: {file_path}")
                return False
            
            if not file_path.suffix.lower() == '.bin':
                logger.warning(f"File is not a .bin file: {file_path}")
                return False
            
            # Create new filename with new extension
            new_file_path = file_path.with_suffix(f'.{new_extension}')
            
            # Check if target file already exists
            if new_file_path.exists():
                logger.warning(f"Target file already exists: {new_file_path}")
                return False
            
            # Rename the file
            file_path.rename(new_file_path)
            logger.info(f"File extension changed: {file_path.name} -> {new_file_path.name}")
            
            return True
            
        except PermissionError as e:
            logger.error(f"Permission denied when changing file extension: {e}")
            return False
        except OSError as e:
            logger.error(f"OS error when changing file extension: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error when changing file extension: {e}")
            return False
    
    def check_xxx_file_exists(self, file_path: str) -> bool:
        """
        Check if a file with .xxx extension already exists.
        
        Args:
            file_path (str): Path to the original .bin file
            
        Returns:
            bool: True if .xxx file exists, False otherwise
        """
        try:
            file_path = Path(file_path)
            xxx_file_path = file_path.with_suffix('.xxx')
            return xxx_file_path.exists()
            
        except Exception as e:
            logger.error(f"Error checking for .xxx file: {e}")
            return False
    
    def backup_file(self, file_path: str) -> bool:
        """
        Create a backup of the file before processing.
        
        Args:
            file_path (str): Path to the file to backup
            
        Returns:
            bool: True if backup successful, False otherwise
        """
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                logger.error(f"File does not exist for backup: {file_path}")
                return False
            
            # Create backup filename with timestamp
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"{file_path.stem}_{timestamp}{file_path.suffix}"
            backup_path = self.backup_dir / backup_filename
            
            # Copy file to backup directory
            shutil.copy2(file_path, backup_path)
            logger.info(f"File backed up: {file_path.name} -> {backup_path.name}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error creating backup: {e}")
            return False
    
    def move_to_processed(self, file_path: str) -> bool:
        """
        Move file to processed directory.
        
        Args:
            file_path (str): Path to the file to move
            
        Returns:
            bool: True if move successful, False otherwise
        """
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                logger.error(f"File does not exist for moving: {file_path}")
                return False
            
            # Create destination path
            dest_path = self.processed_dir / file_path.name
            
            # Check if destination already exists
            if dest_path.exists():
                logger.warning(f"File already exists in processed directory: {dest_path}")
                return False
            
            # Move file
            shutil.move(str(file_path), str(dest_path))
            logger.info(f"File moved to processed: {file_path.name}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error moving file to processed directory: {e}")
            return False
    
    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """
        Get comprehensive information about a file.
        
        Args:
            file_path (str): Path to the file
            
        Returns:
            Dict[str, Any]: File information dictionary
        """
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                return {'exists': False, 'error': 'File does not exist'}
            
            stat = file_path.stat()
            
            info = {
                'exists': True,
                'name': file_path.name,
                'stem': file_path.stem,
                'suffix': file_path.suffix,
                'size': stat.st_size,
                'created': stat.st_ctime,
                'modified': stat.st_mtime,
                'is_file': file_path.is_file(),
                'is_dir': file_path.is_dir(),
                'parent': str(file_path.parent),
                'absolute_path': str(file_path.absolute())
            }
            
            return info
            
        except Exception as e:
            return {'exists': False, 'error': str(e)}
    
    def list_files_by_extension(self, extension: str) -> List[str]:
        """
        List all files with specified extension in firmware directory.
        
        Args:
            extension (str): File extension to search for (without dot)
            
        Returns:
            List[str]: List of file paths
        """
        try:
            files = []
            pattern = f"*.{extension}"
            
            for file_path in self.firmware_dir.glob(pattern):
                if file_path.is_file():
                    files.append(str(file_path))
            
            logger.info(f"Found {len(files)} files with extension .{extension}")
            return files
            
        except Exception as e:
            logger.error(f"Error listing files by extension: {e}")
            return []
    
    def cleanup_old_files(self, days_old: int = 30) -> int:
        """
        Clean up old files from backup and processed directories.
        
        Args:
            days_old (int): Number of days old files to clean up
            
        Returns:
            int: Number of files cleaned up
        """
        try:
            import time
            from datetime import datetime, timedelta
            
            cutoff_time = time.time() - (days_old * 24 * 60 * 60)
            cleaned_count = 0
            
            # Clean backup directory
            for file_path in self.backup_dir.iterdir():
                if file_path.is_file() and file_path.stat().st_mtime < cutoff_time:
                    file_path.unlink()
                    cleaned_count += 1
                    logger.info(f"Cleaned up old backup file: {file_path.name}")
            
            # Clean processed directory
            for file_path in self.processed_dir.iterdir():
                if file_path.is_file() and file_path.stat().st_mtime < cutoff_time:
                    file_path.unlink()
                    cleaned_count += 1
                    logger.info(f"Cleaned up old processed file: {file_path.name}")
            
            logger.info(f"Cleaned up {cleaned_count} old files")
            return cleaned_count
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
            return 0
    
    def get_directory_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the firmware directory.
        
        Returns:
            Dict[str, Any]: Directory statistics
        """
        try:
            stats = {
                'firmware_dir': str(self.firmware_dir),
                'backup_dir': str(self.backup_dir),
                'processed_dir': str(self.processed_dir),
                'total_files': 0,
                'bin_files': 0,
                'xxx_files': 0,
                'backup_files': 0,
                'processed_files': 0,
                'total_size': 0
            }
            
            # Count files in firmware directory
            for file_path in self.firmware_dir.iterdir():
                if file_path.is_file():
                    stats['total_files'] += 1
                    stats['total_size'] += file_path.stat().st_size
                    
                    if file_path.suffix.lower() == '.bin':
                        stats['bin_files'] += 1
                    elif file_path.suffix.lower() == '.xxx':
                        stats['xxx_files'] += 1
            
            # Count backup files
            for file_path in self.backup_dir.iterdir():
                if file_path.is_file():
                    stats['backup_files'] += 1
            
            # Count processed files
            for file_path in self.processed_dir.iterdir():
                if file_path.is_file():
                    stats['processed_files'] += 1
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting directory stats: {e}")
            return {}


def main():
    """Demonstrate the usage of the FileHandler class."""
    handler = FileHandler()
    
    # Example usage
    print("File Handler Demo")
    print("=" * 50)
    
    # Get directory statistics
    stats = handler.get_directory_stats()
    print(f"Directory Statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print()
    
    # List .bin files
    bin_files = handler.list_files_by_extension("bin")
    print(f"Found {len(bin_files)} .bin files")
    
    if bin_files:
        # Get info for first file
        file_info = handler.get_file_info(bin_files[0])
        print(f"First file info: {file_info}")
        
        # Check if .xxx version exists
        xxx_exists = handler.check_xxx_file_exists(bin_files[0])
        print(f".xxx version exists: {xxx_exists}")
        
        # Example: Change extension (commented out to avoid actual file changes)
        # success = handler.change_file_extension(bin_files[0])
        # print(f"Extension change successful: {success}")


if __name__ == "__main__":
    main()
