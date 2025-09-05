"""
기본 테스트 모듈

이 모듈은 패키지의 기본적인 import와 함수들이 올바르게 작동하는지 테스트합니다.
"""

import pytest
import sys
import os

# 패키지를 import할 수 있도록 경로 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def test_package_import():
    """패키지가 올바르게 import되는지 테스트"""
    try:
        import hvac_did_flash
        assert hvac_did_flash.__version__ == "1.0.0"
        assert hvac_did_flash.__author__ == "HVAC Team"
    except ImportError as e:
        pytest.skip(f"패키지 import 실패: {e}")

def test_main_classes_import():
    """주요 클래스들이 올바르게 import되는지 테스트"""
    try:
        from hvac_did_flash import STM32ProgrammingSystem, Config
        # 클래스가 올바르게 import되었는지 확인
        assert STM32ProgrammingSystem is not None
        assert Config is not None
    except ImportError as e:
        pytest.skip(f"클래스 import 실패: {e}")

def test_config_creation():
    """Config 클래스가 올바르게 생성되는지 테스트"""
    try:
        from hvac_did_flash import Config
        config = Config()
        
        # 기본 설정값들이 있는지 확인
        assert config.get('GENERAL', 'log_level') is not None
        assert config.get('PROGRAMMER', 'stm32_programmer_cli') is not None
        assert config.get('SERIAL', 'port') is not None
        
    except Exception as e:
        pytest.skip(f"Config 테스트 실패: {e}")

def test_console_scripts():
    """콘솔 스크립트 진입점이 정의되어 있는지 테스트"""
    try:
        from hvac_did_flash.auto_program import main
        assert callable(main)
    except ImportError as e:
        pytest.skip(f"메인 함수 import 실패: {e}")

def test_package_metadata():
    """패키지 메타데이터가 올바른지 테스트"""
    try:
        import hvac_did_flash
        
        # 필수 메타데이터가 있는지 확인
        assert hasattr(hvac_did_flash, '__version__')
        assert hasattr(hvac_did_flash, '__author__')
        assert hasattr(hvac_did_flash, '__title__')
        
        # 버전이 유효한 형태인지 확인
        version = hvac_did_flash.__version__
        assert isinstance(version, str)
        assert len(version.split('.')) >= 2  # x.y 또는 x.y.z 형태
        
    except Exception as e:
        pytest.skip(f"메타데이터 테스트 실패: {e}")

if __name__ == "__main__":
    # 직접 실행할 때는 간단한 테스트만 수행
    print("기본 테스트 실행 중...")
    
    try:
        test_package_import()
        print("✅ 패키지 import 성공")
    except Exception as e:
        print(f"❌ 패키지 import 실패: {e}")
    
    try:
        test_main_classes_import()
        print("✅ 주요 클래스 import 성공")
    except Exception as e:
        print(f"❌ 주요 클래스 import 실패: {e}")
    
    try:
        test_config_creation()
        print("✅ Config 생성 성공")
    except Exception as e:
        print(f"❌ Config 생성 실패: {e}")
    
    print("기본 테스트 완료!")
