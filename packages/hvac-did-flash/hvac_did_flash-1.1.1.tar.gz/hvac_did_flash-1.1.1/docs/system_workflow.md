# STM32 Firmware Programming System - 전체 동작 과정

## 📋 시스템 개요

이 시스템은 STM32 마이크로컨트롤러에 펌웨어를 프로그래밍하는 자동화된 솔루션입니다. `upload_firmware` 폴더의 `.bin` 파일들을 스캔하여 고유한 시리얼 번호를 추출하고, STM32Programmer_CLI.exe를 사용하여 프로그래밍한 후, 성공적으로 완료된 파일의 확장자를 `.xxx`로 변경합니다.

## 🔄 전체 시스템 워크플로우

```mermaid
graph TD
    A[시스템 시작] --> B[설정 로드]
    B --> C[성능 모니터링 시작]
    C --> D[펌웨어 파일 스캔]
    D --> E{파일 발견?}
    E -->|No| F[에러 로그]
    E -->|Yes| G[시리얼 번호 추출]
    G --> H[ST-Link 연결 확인]
    H --> I{연결 성공?}
    I -->|No| J[재시도 로직]
    J --> H
    I -->|Yes| K[펌웨어 무결성 검증]
    K --> L{검증 성공?}
    L -->|No| M[에러 처리]
    L -->|Yes| N[STM32 프로그래밍]
    N --> O{프로그래밍 성공?}
    O -->|No| P[에러 복구]
    P --> J
    O -->|Yes| Q[시리얼 통신 검증]
    Q --> R{검증 성공?}
    R -->|No| S[경고 로그]
    R -->|Yes| T[파일 확장자 변경 .bin → .xxx]
    T --> U[성공 통계 업데이트]
    U --> V{모든 파일 처리 완료?}
    V -->|No| W[다음 파일 처리]
    W --> G
    V -->|Yes| X[성능 모니터링 종료]
    X --> Y[성능 리포트 생성]
    Y --> Z[시스템 종료]
    
    style A fill:#e1f5fe
    style Z fill:#c8e6c9
    style M fill:#ffcdd2
    style P fill:#ffcdd2
    style S fill:#fff3e0
```

## 🏗️ 시스템 아키텍처

```mermaid
graph TB
    subgraph "메인 애플리케이션"
        A[main_simple.py] --> B[config.py]
        A --> C[performance_monitor.py]
    end
    
    subgraph "핵심 모듈들"
        D[file_scanner.py] --> E[st_link_handler.py]
        E --> F[firmware_programmer.py]
        F --> G[serial_communicator.py]
        G --> H[file_handler.py]
    end
    
    subgraph "지원 모듈들"
        I[firmware_verifier.py] --> J[error_handler.py]
        J --> K[logger.py]
    end
    
    subgraph "외부 도구들"
        L[STM32Programmer_CLI.exe] --> M[ST-Link]
        M --> N[STM32 마이크로컨트롤러]
    end
    
    A --> D
    A --> E
    A --> F
    A --> G
    A --> H
    A --> I
    A --> J
    A --> K
    
    F --> L
    G --> N
    
    style A fill:#e3f2fd
    style L fill:#f3e5f5
    style N fill:#e8f5e8
```

## 📁 파일 처리 과정

```mermaid
flowchart LR
    subgraph "입력 파일"
        A[upload_firmware/*.bin]
    end
    
    subgraph "처리 과정"
        B[파일 스캔] --> C[시리얼 번호 추출]
        C --> D[프로그래밍]
        D --> E[검증]
        E --> F[확장자 변경]
    end
    
    subgraph "출력 파일"
        G[upload_firmware/*.xxx]
    end
    
    A --> B
    F --> G
    
    style A fill:#e1f5fe
    style G fill:#c8e6c9
```

## 🔧 설정 관리 시스템

```mermaid
graph LR
    A[config.ini] --> B[config.py]
    C[명령행 인수] --> B
    B --> D[기본값]
    B --> E[사용자 설정]
    B --> F[명령행 오버라이드]
    
    D --> G[최종 설정]
    E --> G
    F --> G
    
    G --> H[애플리케이션]
    
    style A fill:#e8f5e8
    style C fill:#fff3e0
    style G fill:#e3f2fd
```

## ⚡ 성능 모니터링 시스템

```mermaid
graph TD
    A[성능 모니터링 시작] --> B[메모리 사용량 측정]
    B --> C[CPU 사용량 측정]
    C --> D[실행 시간 측정]
    D --> E{임계값 초과?}
    E -->|Yes| F[경고 로그]
    E -->|No| G[정상 로그]
    F --> H[최적화 제안]
    G --> I[성능 리포트 생성]
    H --> I
    I --> J[JSON 파일 저장]
    
    style A fill:#e1f5fe
    style F fill:#fff3e0
    style I fill:#c8e6c9
```

## 🔄 에러 처리 및 복구 메커니즘

```mermaid
graph TD
    A[에러 발생] --> B{에러 타입 분류}
    
    B -->|ST-Link 에러| C[ST-Link 재연결]
    B -->|프로그래밍 에러| D[프로그래밍 재시도]
    B -->|시리얼 에러| E[시리얼 포트 재설정]
    B -->|파일 에러| F[파일 작업 재시도]
    
    C --> G{재시도 횟수 확인}
    D --> G
    E --> G
    F --> G
    
    G -->|최대 횟수 미만| H[지수 백오프 대기]
    G -->|최대 횟수 도달| I[에러 로그 및 중단]
    
    H --> J[재시도]
    J --> B
    
    style A fill:#ffcdd2
    style I fill:#ffcdd2
    style J fill:#c8e6c9
```

## 🎯 실행 모드별 워크플로우

### 드라이 런 모드
```mermaid
graph LR
    A[드라이 런 시작] --> B[파일 스캔 시뮬레이션]
    B --> C[하드웨어 연결 시뮬레이션]
    C --> D[프로그래밍 시뮬레이션]
    D --> E[검증 시뮬레이션]
    E --> F[성능 리포트 생성]
    F --> G[드라이 런 완료]
    
    style A fill:#e1f5fe
    style G fill:#c8e6c9
```

### 배치 처리 모드
```mermaid
graph TD
    A[배치 처리 시작] --> B[모든 파일 스캔]
    B --> C[파일 목록 생성]
    C --> D[첫 번째 파일 처리]
    D --> E{처리 성공?}
    E -->|Yes| F[다음 파일로]
    E -->|No| G[에러 로그]
    F --> H{모든 파일 완료?}
    H -->|No| D
    H -->|Yes| I[배치 처리 완료]
    G --> H
    
    style A fill:#e1f5fe
    style I fill:#c8e6c9
    style G fill:#ffcdd2
```

### 단일 파일 처리 모드
```mermaid
graph LR
    A[단일 파일 지정] --> B[파일 존재 확인]
    B --> C[시리얼 번호 추출]
    C --> D[ST-Link 연결]
    D --> E[프로그래밍 실행]
    E --> F[검증 실행]
    F --> G[확장자 변경]
    G --> H[완료]
    
    style A fill:#e1f5fe
    style H fill:#c8e6c9
```

## 📊 로깅 및 모니터링

```mermaid
graph TD
    A[로그 이벤트] --> B{로그 레벨}
    B -->|DEBUG| C[상세 디버그 정보]
    B -->|INFO| D[일반 정보]
    B -->|WARNING| E[경고 메시지]
    B -->|ERROR| F[에러 메시지]
    B -->|CRITICAL| G[치명적 에러]
    
    C --> H[콘솔 출력]
    D --> H
    E --> H
    F --> H
    G --> H
    
    H --> I[파일 로그]
    I --> J[로그 회전]
    
    style A fill:#e1f5fe
    style G fill:#ffcdd2
    style J fill:#c8e6c9
```

## 🔧 명령행 인터페이스

```mermaid
graph TD
    A[명령행 파싱] --> B{실행 모드 선택}
    
    B -->|--dry-run| C[드라이 런 모드]
    B -->|--batch| D[배치 처리 모드]
    B -->|--single-file| E[단일 파일 모드]
    B -->|--help| F[도움말 표시]
    
    C --> G[시뮬레이션 실행]
    D --> H[배치 처리 실행]
    E --> I[단일 파일 처리]
    F --> J[도움말 출력]
    
    G --> K[결과 출력]
    H --> K
    I --> K
    J --> K
    
    style A fill:#e1f5fe
    style K fill:#c8e6c9
```

## 📈 성공률 및 통계

```mermaid
graph LR
    A[처리 완료] --> B[통계 계산]
    B --> C[총 파일 수]
    B --> D[성공한 파일 수]
    B --> E[실패한 파일 수]
    B --> F[성공률 계산]
    
    C --> G[성능 리포트]
    D --> G
    E --> G
    F --> G
    
    G --> H[JSON 파일 저장]
    H --> I[콘솔 출력]
    
    style A fill:#e1f5fe
    style G fill:#c8e6c9
```

## 🚀 실행 예시

### 기본 실행
```bash
# 드라이 런 (테스트)
python main_simple.py --dry-run --batch

# 실제 실행
python main_simple.py --config config.ini --batch --verify

# 단일 파일 처리
python main_simple.py --single-file "firmware.bin" --verify
```

### 고급 옵션
```bash
# 상세 로깅
python main_simple.py --log-level DEBUG --dry-run --batch

# 커스텀 설정
python main_simple.py \
  --firmware-dir custom_firmware \
  --programming-speed 8000 \
  --connect-mode underReset \
  --batch
```

## 📋 시스템 요구사항

- **Python 3.8+**
- **STM32Programmer_CLI.exe**
- **ST-Link 하드웨어**
- **STM32 마이크로컨트롤러**
- **시리얼 통신 포트**

## 🔍 모니터링 포인트

1. **파일 스캔**: 펌웨어 파일 발견 및 시리얼 번호 추출
2. **하드웨어 연결**: ST-Link 연결 상태 확인
3. **프로그래밍**: STM32 프로그래밍 진행 상황
4. **검증**: 시리얼 통신을 통한 펌웨어 검증
5. **파일 관리**: 확장자 변경 및 백업
6. **성능**: 메모리, CPU 사용량, 실행 시간
7. **에러 처리**: 재시도 및 복구 메커니즘

이 다이어그램들은 시스템의 전체적인 동작 과정을 시각적으로 보여주며, 각 단계에서 발생할 수 있는 상황과 처리 방법을 명확하게 설명합니다.
