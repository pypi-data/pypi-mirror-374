"""
Voice announcer module for STM32 programming system.

This module provides text-to-speech functionality for status announcements.
"""

import logging
import subprocess
import platform
import os
from typing import Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VoiceAnnouncer:
    """Class to handle voice announcements using system TTS."""
    
    def __init__(self):
        """Initialize the voice announcer."""
        self.system = platform.system()
        self.available = self._check_tts_availability()
        
        if self.available:
            logger.info(f"Voice announcer initialized for {self.system}")
        else:
            logger.warning("Text-to-speech not available on this system")
    
    def _check_tts_availability(self) -> bool:
        """Check if text-to-speech is available on the current system."""
        try:
            if self.system == "Windows":
                # Check if SAPI is available (built into Windows)
                return True
            elif self.system == "Darwin":  # macOS
                # Check if say command is available
                result = subprocess.run(['which', 'say'], capture_output=True)
                return result.returncode == 0
            elif self.system == "Linux":
                # Check if espeak or festival is available
                for cmd in ['espeak', 'festival']:
                    result = subprocess.run(['which', cmd], capture_output=True)
                    if result.returncode == 0:
                        return True
                return False
            else:
                return False
        except Exception as e:
            logger.error(f"Error checking TTS availability: {e}")
            return False
    
    def speak(self, text: str, language: str = "ko") -> bool:
        """
        Convert text to speech and play it.
        
        Args:
            text (str): Text to speak
            language (str): Language code (ko for Korean, en for English)
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.available:
            logger.warning("Text-to-speech not available")
            return False
        
        try:
            if self.system == "Windows":
                return self._speak_windows(text, language)
            elif self.system == "Darwin":  # macOS
                return self._speak_macos(text, language)
            elif self.system == "Linux":
                return self._speak_linux(text, language)
            else:
                logger.error(f"Unsupported operating system: {self.system}")
                return False
        except Exception as e:
            logger.error(f"Error speaking text: {e}")
            return False
    
    def _speak_windows(self, text: str, language: str) -> bool:
        """Speak text on Windows using SAPI."""
        try:
            # Use PowerShell with SAPI
            if language == "ko":
                # Korean voice (if available)
                cmd = [
                    'powershell', '-Command',
                    f'Add-Type -AssemblyName System.Speech; '
                    f'$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer; '
                    f'$synth.SelectVoice("Microsoft Heami Desktop"); '
                    f'$synth.Speak("{text}")'
                ]
            else:
                # English voice
                cmd = [
                    'powershell', '-Command',
                    f'Add-Type -AssemblyName System.Speech; '
                    f'$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer; '
                    f'$synth.Speak("{text}")'
                ]
            
            logger.info(f"Speaking: {text}")
            result = subprocess.run(cmd, capture_output=True, timeout=10)
            
            if result.returncode == 0:
                logger.info("Voice announcement completed successfully")
                return True
            else:
                logger.error(f"Voice announcement failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("Voice announcement timeout")
            return False
        except Exception as e:
            logger.error(f"Error in Windows TTS: {e}")
            return False
    
    def _speak_macos(self, text: str, language: str) -> bool:
        """Speak text on macOS using say command."""
        try:
            if language == "ko":
                # Korean voice (if available)
                cmd = ['say', '-v', 'Yuna', text]
            else:
                # English voice
                cmd = ['say', text]
            
            logger.info(f"Speaking: {text}")
            result = subprocess.run(cmd, capture_output=True, timeout=10)
            
            if result.returncode == 0:
                logger.info("Voice announcement completed successfully")
                return True
            else:
                logger.error(f"Voice announcement failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("Voice announcement timeout")
            return False
        except Exception as e:
            logger.error(f"Error in macOS TTS: {e}")
            return False
    
    def _speak_linux(self, text: str, language: str) -> bool:
        """Speak text on Linux using espeak or festival."""
        try:
            # Try espeak first
            result = subprocess.run(['which', 'espeak'], capture_output=True)
            if result.returncode == 0:
                if language == "ko":
                    # Korean voice (if available)
                    cmd = ['espeak', '-v', 'ko', text]
                else:
                    # English voice
                    cmd = ['espeak', text]
            else:
                # Try festival
                result = subprocess.run(['which', 'festival'], capture_output=True)
                if result.returncode == 0:
                    cmd = ['festival', '--tts']
                    # Festival doesn't support Korean well, use English
                    text = "Board completed" if "완료" in text else text
                else:
                    logger.error("No TTS engine available on Linux")
                    return False
            
            logger.info(f"Speaking: {text}")
            result = subprocess.run(cmd, input=text, text=True, capture_output=True, timeout=10)
            
            if result.returncode == 0:
                logger.info("Voice announcement completed successfully")
                return True
            else:
                logger.error(f"Voice announcement failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("Voice announcement timeout")
            return False
        except Exception as e:
            logger.error(f"Error in Linux TTS: {e}")
            return False
    
    def announce_board_completed(self) -> bool:
        """Announce that the board is completed."""
        return self.speak("완료된 보드입니다. 새로운 보드를 넣어주세요", "ko")
    
    def announce_board_completed_with_serial(self, serial: str) -> bool:
        """
        Announce that the board is completed with specific serial number.
        
        Args:
            serial (str): 4-digit serial number
            
        Returns:
            bool: True if successful, False otherwise
        """
        message = f"완료된 보드입니다. {serial}번으로 프로그램 되었습니다."
        return self.speak(message, "ko")
    
    def announce_invalid_programming(self) -> bool:
        """Announce that the programming is invalid."""
        return self.speak("프로그램이 잘못 되었습니다.", "ko")
    
    def announce_programming_started(self) -> bool:
        """Announce that programming has started."""
        return self.speak("프로그래밍을 시작합니다.", "ko")
    
    def announce_programming_completed(self) -> bool:
        """Announce that programming has completed."""
        return self.speak("프로그램이 완료되었습니다.", "ko")
    
    def announce_error(self, error_message: str = "오류가 발생했습니다.") -> bool:
        """Announce an error."""
        return self.speak(error_message, "ko")
    
    def announce_all_firmware_completed(self) -> bool:
        """Announce that all firmware has been completed."""
        return self.speak("모든 펌웨어 작업을 완료했습니다.", "ko")
    
    def announce_programming_start(self, serial_number: str) -> bool:
        """Announce that programming is starting for a specific serial number."""
        # Extract last 4 digits from serial number
        last_4_digits = serial_number[-4:] if len(serial_number) >= 4 else serial_number
        message = f"{last_4_digits}번 프로그램을 시작합니다."
        return self.speak(message, "ko")
    
    def announce_batch_start(self, start_serial: str, end_serial: str, total_count: int) -> bool:
        """Announce the start of batch firmware programming with serial number range."""
        # Extract last 4 digits from start and end serial numbers
        start_digits = start_serial[-4:] if len(start_serial) >= 4 else start_serial
        end_digits = end_serial[-4:] if len(end_serial) >= 4 else end_serial
        message = f"시리얼 번호 {start_digits}번부터 {end_digits}번까지 총 {total_count}개의 펌웨어 작업을 시작하겠습니다."
        return self.speak(message, "ko")
    
    def announce_board_not_connected(self) -> bool:
        """Announce that the board is not connected."""
        return self.speak("보드가 연결이 되어 있지 않습니다.", "ko")
    
    def announce_custom(self, message: str, language: str = "ko") -> bool:
        """
        Announce a custom message.
        
        Args:
            message (str): Custom message to announce
            language (str): Language code (ko for Korean, en for English)
            
        Returns:
            bool: True if successful, False otherwise
        """
        return self.speak(message, language)


def main():
    """Test the voice announcer functionality."""
    announcer = VoiceAnnouncer()
    
    if announcer.available:
        print("Testing voice announcer...")
        
        # Test Korean announcement
        success = announcer.announce_board_completed()
        if success:
            print("Korean announcement successful")
        else:
            print("Korean announcement failed")
        
        # Test English announcement
        success = announcer.speak("Board completed", "en")
        if success:
            print("English announcement successful")
        else:
            print("English announcement failed")
    else:
        print("Voice announcer not available on this system")


if __name__ == "__main__":
    main()
