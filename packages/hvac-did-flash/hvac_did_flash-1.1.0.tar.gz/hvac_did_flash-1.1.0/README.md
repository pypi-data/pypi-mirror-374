# HVAC DID Flash

STM32 펌웨어 프로그래밍 시스템 - HVAC 장치를 위한 DID 플래시 지원

자동화된 STM32 펌웨어 프로그래밍 시스템으로, HVAC 애플리케이션에 특화된 DID(Data Identifier) 플래시 지원을 제공합니다.

## 주요 기능

- **자동화된 STM32 펌웨어 프로그래밍**: ST-Link를 통한 완전 자동화된 프로그래밍
- **지능형 플래시 검증**: 프로그래밍 전후 플래시 메모리 검증
- **시리얼 통신 검증**: UART를 통한 펌웨어 동작 확인
- **음성 안내**: 프로그래밍 진행 상황을 음성으로 안내
- **배치 처리**: 여러 펌웨어 파일의 일괄 처리
- **성능 모니터링**: 상세한 성능 분석 및 리포팅
- **오류 복구**: 강력한 오류 처리 및 자동 재시도

## 시리얼 번호 관리

- did_serial.csv 파일에 기록된 serial number는 "이전 출력된 번호"입니다.
- 예를 들어, csv에 0000이 기록되어 있으면, 다음 수행 시 0001이 자동으로 생성되어 사용됩니다.

## 설치

### PyPI에서 설치 (권장)

```bash
pip install hvac-did-flash
```

### 소스에서 설치

```bash
git clone https://github.com/your-org/hvac-did-flash.git
cd hvac-did-flash
pip install -e .
```

### 개발자 설치

```bash
git clone https://github.com/your-org/hvac-did-flash.git
cd hvac-did-flash
pip install -e ".[dev]"
```

### 2. Slack 설정 (선택사항)

Slack으로 펌웨어를 자동 업로드하려면 다음 단계를 따르세요:

#### 2.1 Slack App 생성

1. https://api.slack.com/apps 로 이동
2. "Create New App" → "From scratch" 클릭
3. App 이름 입력 (예: "HVAC Firmware Upload Bot")
4. 워크스페이스 선택

#### 2.2 권한 설정

1. 좌측 메뉴에서 "OAuth & Permissions" 클릭
2. "Scopes" 섹션으로 스크롤
3. "Bot Token Scopes"에서 "Add an OAuth Scope" 클릭
4. 다음 권한을 추가:
   - `files:write` - 파일 업로드 (필수)
   - `chat:write` - 메시지 전송 (선택사항)
5. 권한 추가 후 페이지 상단의 노란색 배너에서 "reinstall your app" 클릭
6. 워크스페이스에 재설치 승인

#### 2.3 App 설치

1. "OAuth & Permissions" 페이지 상단의 "Install to Workspace" 클릭
2. 권한 승인
3. "Bot User OAuth Token" 복사 (xoxb-로 시작)

#### 2.4 채널에 Bot 추가

1. Slack에서 파일을 업로드할 채널로 이동
2. 채널에서 `/invite @[Bot 이름]` 입력

#### 2.5 환경 변수 설정

1. `.env.example` 파일을 `.env`로 복사
2. 다음 값을 설정:

```env
SLACK_BOT_TOKEN=xoxb-your-bot-token-here
SLACK_CHANNEL_ID=C1234567890
```

**채널 ID 찾는 방법:**
- Slack 웹/데스크톱에서 채널 우클릭 → "View channel details"
- 하단의 Channel ID 복사

## 사용법

### 명령줄 인터페이스

```bash
# 기본 사용법 - 배치 모드로 모든 펌웨어 파일 처리
hvac-flash --batch

# 단일 파일 처리
hvac-flash --single-file firmware.bin

# 설정 파일 지정
hvac-flash --config config.ini --batch

# 드라이런 모드 (실제 프로그래밍 없이 테스트)
hvac-flash --dry-run

# ST-Link 시리얼 번호 지정
hvac-flash --batch --stlink-sn 123456789
```

### Python API 사용

```python
from hvac_did_flash import STM32ProgrammingSystem, Config

# 설정 로드
config = Config()

# 프로그래밍 시스템 초기화
system = STM32ProgrammingSystem(config)

# 배치 처리
firmware_files = system.scan_firmware_directory()
stats = system.process_batch_files(firmware_files)

print(f"처리 완료: {stats['successful']}/{stats['total']} 성공")
```

### 고급 사용법

```bash
# 검증 활성화
hvac-flash --batch --verify

# 검증 비활성화
hvac-flash --batch --no-verify

# 특정 ST-Link 시리얼 번호 사용
hvac-flash --batch --stlink-sn 066DFF383638424E43172239

# 사용자 정의 설정으로 실행
hvac-flash --config my_config.ini --batch
```

## 명령줄 인수

- `repeat` (선택사항): 빌드 반복 횟수 (기본값: 1)
- `start_serial` (선택사항): 시작 시리얼 번호 또는 "auto" (기본값: auto)
- `model` (선택사항): 모델명 (기본값: QZ25)
- `--slack`: Slack으로 ZIP 파일 업로드

## 출력 파일

- 개별 펌웨어 파일: `firmware/hvac-main-stm32f103@CYBER-QZ25_{serial}_{tag}.bin`
- 압축 파일: `{model}_{start_serial}_{count}.zip`

## 문제 해결

### Slack 업로드 오류

1. **missing_scope**: 
   - 오류 메시지: `'error': 'missing_scope', 'needed': 'files:write'`
   - 해결 방법:
     1. https://api.slack.com/apps 에서 앱 선택
     2. "OAuth & Permissions" → "Scopes" → "Bot Token Scopes"
     3. `files:write` 권한 추가
     4. 페이지 상단에서 "reinstall your app" 클릭
     5. 재설치 완료 후 다시 시도

2. **invalid_auth**: SLACK_BOT_TOKEN이 올바른지 확인
3. **channel_not_found**: SLACK_CHANNEL_ID가 올바른지 확인
4. **not_in_channel**: Bot을 채널에 초대 (`/invite @bot-name`)
5. **file_too_large**: Slack 파일 크기 제한 (1GB) 확인

### 환경 변수 문제

- `.env` 파일이 프로젝트 루트에 있는지 확인
- `.env` 파일이 `.gitignore`에 포함되어 있는지 확인 (보안)

## 주의사항

- Slack Bot Token을 절대 코드에 직접 입력하지 마세요
- `.env` 파일을 Git에 커밋하지 마세요
- 대용량 파일 업로드 시 네트워크 상태 확인


