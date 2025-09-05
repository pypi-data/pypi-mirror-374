"""
HVAC DID Flash - STM32 Firmware Programming System

A comprehensive firmware programming system for STM32 devices specifically designed
for HVAC applications with DID (Data Identifier) flash support.

This package provides:
- Automated STM32 firmware programming
- ST-Link connection management
- Serial communication and verification
- Flash checking and verification
- Voice announcements
- Performance monitoring
- Error handling and recovery
- Batch processing capabilities

Main Components:
- STM32ProgrammingSystem: Main programming system
- Config: Configuration management
- Various handlers and communicators for specialized tasks

Example usage:
    from hvac_did_flash import STM32ProgrammingSystem, Config
    
    config = Config()
    system = STM32ProgrammingSystem(config)
    # Use system.run() or individual methods
"""

__version__ = "1.0.0"
__author__ = "HVAC Team"
__email__ = "team@example.com"
__license__ = "MIT"

# Import main classes for easy access
from .auto_program import STM32ProgrammingSystem, main
from .config import Config
from .st_link_handler import STLinkHandler
from .firmware_programmer import FirmwareProgrammer
from .serial_communicator import SerialCommunicator
from .flash_checker import FlashChecker
from .voice_announcer import VoiceAnnouncer
from .performance_monitor import PerformanceMonitor
from .error_handler import ErrorHandler
from .logger import ProgrammingLogger

# Define what gets imported with "from hvac_did_flash import *"
__all__ = [
    "STM32ProgrammingSystem",
    "Config",
    "STLinkHandler", 
    "FirmwareProgrammer",
    "SerialCommunicator",
    "FlashChecker",
    "VoiceAnnouncer",
    "PerformanceMonitor",
    "ErrorHandler",
    "ProgrammingLogger",
    "main",
]

# Package metadata
__title__ = "hvac-did-flash"
__description__ = "STM32 Firmware Programming System for HVAC devices with DID flash support"
__url__ = "https://github.com/your-org/hvac-did-flash"
