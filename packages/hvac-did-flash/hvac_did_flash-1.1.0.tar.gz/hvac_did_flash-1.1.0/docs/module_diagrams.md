# STM32 Firmware Programming System - 모듈별 상세 다이어그램

## 📁 file_scanner.py 모듈

```mermaid
graph TD
    A[scan_firmware_files] --> B[디렉토리 스캔]
    B --> C[*.bin 파일 필터링]
    C --> D[파일 목록 반환]
    
    E[extract_serial_number] --> F[정규식 패턴 매칭]
    F --> G{매칭 성공?}
    G -->|Yes| H[시리얼 번호 추출]
    G -->|No| I[None 반환]
    
    J[verify_file_uniqueness] --> K[시리얼 번호 그룹화]
    K --> L{중복 발견?}
    L -->|Yes| M[중복 파일 목록 반환]
    L -->|No| N[빈 목록 반환]
    
    style A fill:#e1f5fe
    style H fill:#c8e6c9
    style M fill:#fff3e0
```

## 🔌 st_link_handler.py 모듈

```mermaid
graph TD
    A[STLinkHandler 초기화] --> B[설정 파일 로드]
    B --> C[STM32Programmer_CLI 경로 확인]
    C --> D[ST-Link 연결 테스트]
    
    E[check_st_link_connection] --> F[STM32Programmer_CLI 실행]
    F --> G{연결 성공?}
    G -->|Yes| H[연결 정보 반환]
    G -->|No| I[재시도 로직]
    I --> J[지수 백오프]
    J --> F
    
    K[verify_stm32_connection] --> L[마이크로컨트롤러 상태 확인]
    L --> M{연결 확인?}
    M -->|Yes| N[연결 성공]
    M -->|No| O[연결 실패]
    
    style A fill:#e1f5fe
    style H fill:#c8e6c9
    style N fill:#c8e6c9
    style O fill:#ffcdd2
```

## 💾 firmware_programmer.py 모듈

```mermaid
graph TD
    A[FirmwareProgrammer 초기화] --> B[프로그래머 CLI 확인]
    B --> C[통계 초기화]
    
    D[program_firmware] --> E[파일 존재 확인]
    E --> F[프로그래밍 명령 구성]
    F --> G[STM32Programmer_CLI 실행]
    G --> H{프로그래밍 성공?}
    H -->|Yes| I[성공 통계 업데이트]
    H -->|No| J[실패 통계 업데이트]
    J --> K[에러 로그]
    
    L[get_programming_statistics] --> M[통계 정보 반환]
    
    style A fill:#e1f5fe
    style I fill:#c8e6c9
    style K fill:#ffcdd2
```

## 📡 serial_communicator.py 모듈

```mermaid
graph TD
    A[SerialCommunicator 초기화] --> B[포트 설정]
    B --> C[시리얼 포트 구성]
    
    D[open] --> E[포트 열기 시도]
    E --> F{열기 성공?}
    F -->|Yes| G[연결 성공]
    F -->|No| H[연결 실패]
    
    I[write] --> J[데이터 전송]
    J --> K{전송 성공?}
    K -->|Yes| L[전송 완료]
    K -->|No| M[전송 실패]
    
    N[read] --> O[데이터 읽기]
    O --> P{읽기 성공?}
    P -->|Yes| Q[데이터 반환]
    P -->|No| R[읽기 실패]
    
    S[verify_firmware] --> T[펌웨어 검증 명령 전송]
    T --> U[응답 대기]
    U --> V{검증 성공?}
    V -->|Yes| W[검증 성공]
    V -->|No| X[검증 실패]
    
    style A fill:#e1f5fe
    style G fill:#c8e6c9
    style L fill:#c8e6c9
    style Q fill:#c8e6c9
    style W fill:#c8e6c9
    style H fill:#ffcdd2
    style M fill:#ffcdd2
    style R fill:#ffcdd2
    style X fill:#ffcdd2
```

## 📝 file_handler.py 모듈

```mermaid
graph TD
    A[FileHandler 초기화] --> B[파일 시스템 접근 확인]
    
    C[change_file_extension] --> D[원본 파일 존재 확인]
    D --> E[새 파일명 생성]
    E --> F[파일 이름 변경]
    F --> G{변경 성공?}
    G -->|Yes| H[변경 완료]
    G -->|No| I[변경 실패]
    
    J[check_xxx_file_exists] --> K[.xxx 파일 존재 확인]
    K --> L{파일 존재?}
    L -->|Yes| M[존재함]
    L -->|No| N[존재하지 않음]
    
    style A fill:#e1f5fe
    style H fill:#c8e6c9
    style M fill:#c8e6c9
    style I fill:#ffcdd2
    style N fill:#fff3e0
```

## 🔍 firmware_verifier.py 모듈

```mermaid
graph TD
    A[FirmwareVerifier 초기화] --> B[체크섬 데이터베이스 로드]
    
    C[calculate_checksum] --> D[SHA256 해시 계산]
    D --> E[체크섬 반환]
    
    F[verify_checksum] --> G[예상 체크섬 로드]
    G --> H[체크섬 비교]
    H --> I{일치?}
    I -->|Yes| J[검증 성공]
    I -->|No| K[검증 실패]
    
    L[verify_digital_signature] --> M[디지털 서명 확인]
    M --> N{서명 유효?}
    N -->|Yes| O[서명 검증 성공]
    N -->|No| P[서명 검증 실패]
    
    style A fill:#e1f5fe
    style E fill:#c8e6c9
    style J fill:#c8e6c9
    style O fill:#c8e6c9
    style K fill:#ffcdd2
    style P fill:#ffcdd2
```

## ⚠️ error_handler.py 모듈

```mermaid
graph TD
    A[ErrorHandler 초기화] --> B[에러 통계 초기화]
    
    C[retry_with_backoff] --> D[함수 실행]
    D --> E{실행 성공?}
    E -->|Yes| F[성공 반환]
    E -->|No| G[재시도 횟수 확인]
    G --> H{최대 횟수?}
    H -->|No| I[백오프 대기]
    I --> J[재시도]
    J --> D
    H -->|Yes| K[최종 실패]
    
    L[handle_stlink_error] --> M[ST-Link 특정 에러 처리]
    M --> N[연결 재설정]
    
    O[handle_programming_error] --> P[프로그래밍 에러 처리]
    P --> Q[프로그래밍 재시도]
    
    R[handle_serial_error] --> S[시리얼 에러 처리]
    S --> T[포트 재설정]
    
    style A fill:#e1f5fe
    style F fill:#c8e6c9
    style K fill:#ffcdd2
    style N fill:#fff3e0
    style Q fill:#fff3e0
    style T fill:#fff3e0
```

## 📊 logger.py 모듈

```mermaid
graph TD
    A[ProgrammingLogger 초기화] --> B[로거 설정]
    B --> C[파일 핸들러 설정]
    C --> D[콘솔 핸들러 설정]
    
    E[info] --> F[INFO 레벨 로그]
    F --> G[콘솔 출력]
    G --> H[파일 저장]
    
    I[warning] --> J[WARNING 레벨 로그]
    J --> K[콘솔 출력]
    K --> L[파일 저장]
    
    M[error] --> N[ERROR 레벨 로그]
    N --> O[콘솔 출력]
    O --> P[파일 저장]
    
    Q[log_statistics] --> R[통계 정보 로깅]
    R --> S[성공/실패 카운트]
    S --> T[실행 시간]
    T --> U[성공률 계산]
    
    style A fill:#e1f5fe
    style H fill:#c8e6c9
    style L fill:#fff3e0
    style P fill:#ffcdd2
    style U fill:#c8e6c9
```

## ⚙️ config.py 모듈

```mermaid
graph TD
    A[Config 초기화] --> B[기본값 설정]
    B --> C[설정 파일 로드]
    C --> D[명령행 인수 파싱]
    D --> E[최종 설정 구성]
    
    F[load_from_file] --> G[INI 파일 읽기]
    G --> H{파일 존재?}
    H -->|Yes| I[설정 로드]
    H -->|No| J[기본값 사용]
    
    K[save_to_file] --> L[디렉토리 생성]
    L --> M[INI 파일 저장]
    
    N[get] --> O[섹션과 키로 값 조회]
    O --> P{값 존재?}
    P -->|Yes| Q[값 반환]
    P -->|No| R[기본값 반환]
    
    style A fill:#e1f5fe
    style I fill:#c8e6c9
    style M fill:#c8e6c9
    style Q fill:#c8e6c9
    style J fill:#fff3e0
    style R fill:#fff3e0
```

## 📈 performance_monitor.py 모듈

```mermaid
graph TD
    A[PerformanceMonitor 초기화] --> B[성능 데이터 저장소]
    B --> C[임계값 설정]
    
    D[measure_execution_time] --> E[함수 실행 시작]
    E --> F[시작 시간 기록]
    F --> G[함수 실행]
    G --> H[종료 시간 기록]
    H --> I[실행 시간 계산]
    I --> J[로그 기록]
    
    K[get_memory_usage] --> L[현재 메모리 사용량 조회]
    L --> M[RSS 메모리 반환]
    
    N[get_cpu_usage] --> O[현재 CPU 사용량 조회]
    O --> P[CPU 퍼센트 반환]
    
    Q[start_monitoring] --> R[모니터링 시작]
    R --> S[시작 이벤트 기록]
    
    T[stop_monitoring] --> U[모니터링 종료]
    U --> V[종료 이벤트 기록]
    V --> W[성능 리포트 생성]
    W --> X[JSON 파일 저장]
    
    style A fill:#e1f5fe
    style J fill:#c8e6c9
    style M fill:#c8e6c9
    style P fill:#c8e6c9
    style S fill:#c8e6c9
    style X fill:#c8e6c9
```

## 🔄 데이터 흐름 다이어그램

```mermaid
graph LR
    subgraph "입력 데이터"
        A[펌웨어 파일] --> B[설정 파일]
        B --> C[명령행 인수]
    end
    
    subgraph "처리 단계"
        D[파일 스캔] --> E[시리얼 번호 추출]
        E --> F[하드웨어 연결]
        F --> G[프로그래밍]
        G --> H[검증]
        H --> I[파일 변경]
    end
    
    subgraph "출력 데이터"
        J[성능 리포트] --> K[로그 파일]
        K --> L[통계 정보]
        I --> M[변경된 파일]
    end
    
    A --> D
    B --> D
    C --> D
    G --> J
    H --> K
    I --> L
    
    style A fill:#e1f5fe
    style B fill:#e1f5fe
    style C fill:#e1f5fe
    style J fill:#c8e6c9
    style K fill:#c8e6c9
    style L fill:#c8e6c9
    style M fill:#c8e6c9
```

## 🔗 모듈 간 의존성

```mermaid
graph TD
    A[main_simple.py] --> B[config.py]
    A --> C[performance_monitor.py]
    A --> D[file_scanner.py]
    A --> E[st_link_handler.py]
    A --> F[firmware_programmer.py]
    A --> G[serial_communicator.py]
    A --> H[file_handler.py]
    A --> I[firmware_verifier.py]
    A --> J[error_handler.py]
    A --> K[logger.py]
    
    F --> L[STM32Programmer_CLI.exe]
    G --> M[시리얼 포트]
    E --> N[ST-Link 하드웨어]
    
    style A fill:#e3f2fd
    style L fill:#f3e5f5
    style M fill:#f3e5f5
    style N fill:#f3e5f5
```

## 🎯 실행 시퀀스 다이어그램

```mermaid
sequenceDiagram
    participant User as 사용자
    participant Main as main_simple.py
    participant Config as config.py
    participant Scanner as file_scanner.py
    participant STLink as st_link_handler.py
    participant Programmer as firmware_programmer.py
    participant Serial as serial_communicator.py
    participant Handler as file_handler.py
    participant Monitor as performance_monitor.py
    
    User->>Main: 실행 명령
    Main->>Config: 설정 로드
    Config-->>Main: 설정 반환
    Main->>Monitor: 모니터링 시작
    Main->>Scanner: 파일 스캔
    Scanner-->>Main: 파일 목록
    Main->>STLink: 연결 확인
    STLink-->>Main: 연결 상태
    Main->>Programmer: 프로그래밍 실행
    Programmer-->>Main: 프로그래밍 결과
    Main->>Serial: 검증 실행
    Serial-->>Main: 검증 결과
    Main->>Handler: 파일 확장자 변경
    Handler-->>Main: 변경 결과
    Main->>Monitor: 모니터링 종료
    Monitor-->>Main: 성능 리포트
    Main-->>User: 실행 완료
```

이 다이어그램들은 각 모듈의 내부 동작과 모듈 간의 상호작용을 상세하게 보여줍니다. 각 모듈의 역할과 책임이 명확하게 구분되어 있으며, 전체 시스템의 복잡성을 이해하는 데 도움이 됩니다.
