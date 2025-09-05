# STM32 Firmware Programming System - 문서

이 디렉토리는 STM32 펌웨어 프로그래밍 시스템의 전체 문서를 포함합니다.

## 📚 문서 목록

### 📋 시스템 개요 및 워크플로우
- **[system_workflow.md](system_workflow.md)** - 전체 시스템 동작 과정과 Mermaid 다이어그램
  - 전체 시스템 워크플로우
  - 시스템 아키텍처
  - 파일 처리 과정
  - 설정 관리 시스템
  - 성능 모니터링 시스템
  - 에러 처리 및 복구 메커니즘
  - 실행 모드별 워크플로우
  - 로깅 및 모니터링
  - 명령행 인터페이스
  - 성공률 및 통계

### 🔧 모듈별 상세 다이어그램
- **[module_diagrams.md](module_diagrams.md)** - 각 모듈의 내부 동작과 상호작용
  - file_scanner.py 모듈
  - st_link_handler.py 모듈
  - firmware_programmer.py 모듈
  - serial_communicator.py 모듈
  - file_handler.py 모듈
  - firmware_verifier.py 모듈
  - error_handler.py 모듈
  - logger.py 모듈
  - config.py 모듈
  - performance_monitor.py 모듈
  - 데이터 흐름 다이어그램
  - 모듈 간 의존성
  - 실행 시퀀스 다이어그램

### 📋 요구사항 문서
- **[prd.txt](../.taskmaster/docs/prd.txt)** - 제품 요구사항 문서 (Task Master에서 생성)

## 🎯 문서 사용법

### 개발자용
1. **system_workflow.md** - 전체 시스템 구조와 동작 원리 이해
2. **module_diagrams.md** - 특정 모듈의 구현 세부사항 확인
3. **prd.txt** - 원본 요구사항 참조

### 사용자용
1. **system_workflow.md**의 "실행 예시" 섹션 - 실제 사용 방법
2. **system_workflow.md**의 "시스템 요구사항" 섹션 - 설치 및 설정

### 관리자용
1. **system_workflow.md**의 "모니터링 포인트" 섹션 - 시스템 운영 관리
2. **module_diagrams.md**의 "성능 모니터링 시스템" - 성능 분석

## 🔍 다이어그램 보기

이 문서의 Mermaid 다이어그램들은 다음 방법으로 볼 수 있습니다:

### GitHub/GitLab
- GitHub나 GitLab에서 직접 렌더링됩니다
- Markdown 파일을 열면 자동으로 다이어그램이 표시됩니다

### 로컬 환경
- VS Code에서 Mermaid 확장 프로그램 설치
- 또는 온라인 Mermaid 편집기 사용: https://mermaid.live

### 문서 편집기
- Typora, Obsidian 등 Mermaid를 지원하는 마크다운 편집기 사용

## 📝 문서 업데이트

새로운 기능이나 변경사항이 있을 때:

1. **system_workflow.md** - 전체 워크플로우 변경사항 반영
2. **module_diagrams.md** - 해당 모듈의 다이어그램 업데이트
3. 이 README.md - 새로운 문서 추가 시 목록 업데이트

## 🎨 다이어그램 스타일 가이드

- **파란색 (#e1f5fe)**: 시작점, 입력
- **초록색 (#c8e6c9)**: 성공, 완료, 출력
- **주황색 (#fff3e0)**: 경고, 주의
- **빨간색 (#ffcdd2)**: 에러, 실패
- **보라색 (#f3e5f5)**: 외부 도구, 하드웨어

## 📞 문서 관련 문의

문서에 대한 질문이나 개선 제안이 있으시면:
1. GitHub Issues에 등록
2. 또는 프로젝트 관리자에게 직접 문의

---

*이 문서들은 시스템의 이해와 유지보수를 돕기 위해 작성되었습니다.*
