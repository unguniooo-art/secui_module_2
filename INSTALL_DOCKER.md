# Docker 설치 가이드 (Windows)

Docker가 설치되어 있지 않습니다. 아래 방법으로 설치하세요.

## 방법 1: Docker Desktop 설치 (추천)

### 1. Docker Desktop 다운로드

**공식 웹사이트**: https://www.docker.com/products/docker-desktop/

또는 직접 다운로드:
```
https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe
```

### 2. 설치 단계

1. **다운로드한 설치 파일 실행**
   - `Docker Desktop Installer.exe` 더블클릭

2. **설치 옵션 선택**
   - ✅ "Use WSL 2 instead of Hyper-V" (권장)
   - ✅ "Add shortcut to desktop"

3. **설치 완료 후 재부팅**

4. **Docker Desktop 실행**
   - 바탕화면 아이콘 또는 시작 메뉴에서 실행
   - 트레이에서 Docker 아이콘 확인 (고래 모양)

### 3. Docker 설치 확인

새 PowerShell 또는 명령 프롬프트를 열고:

```powershell
docker --version
docker-compose --version
```

정상 출력:
```
Docker version 24.0.x, build xxxxx
Docker Compose version v2.x.x
```

## 방법 2: Chocolatey 사용 (개발자용)

관리자 권한 PowerShell:

```powershell
# Chocolatey 설치 (없는 경우)
Set-ExecutionPolicy Bypass -Scope Process -Force
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Docker Desktop 설치
choco install docker-desktop -y
```

## 시스템 요구사항

### 최소 사양
- **OS**: Windows 10 64-bit (버전 1903 이상) 또는 Windows 11
- **RAM**: 4GB (권장 8GB)
- **CPU**: SLAT 지원 64-bit 프로세서
- **BIOS**: 가상화 활성화

### WSL 2 요구사항 (권장)

WSL 2가 활성화되어 있어야 합니다:

```powershell
# 관리자 권한 PowerShell
wsl --install
```

또는 수동 활성화:

```powershell
# 1. WSL 활성화
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart

# 2. Virtual Machine Platform 활성화
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart

# 3. 재부팅
shutdown /r /t 0

# 4. WSL 2를 기본으로 설정
wsl --set-default-version 2
```

## Docker Desktop 실행 확인

### 1. Docker Desktop이 실행 중인지 확인

트레이에서 Docker 아이콘 확인:
- 🐋 아이콘이 있으면 실행 중
- 아이콘을 클릭하여 상태 확인

### 2. Docker 데몬 상태 확인

```powershell
docker ps
```

정상 출력 (빈 목록도 정상):
```
CONTAINER ID   IMAGE     COMMAND   CREATED   STATUS    PORTS     NAMES
```

에러 발생 시:
```
error during connect: This error may indicate that the docker daemon is not running.
```
→ Docker Desktop을 시작해야 함

## 프로젝트 실행

Docker 설치 및 실행 확인 후:

### PowerShell 사용

```powershell
# 프로젝트 디렉토리로 이동
cd C:\Users\student\Desktop\VibeCoding\module_4

# Docker Compose 실행
docker-compose up -d
```

### 명령 프롬프트 사용

```cmd
cd C:\Users\student\Desktop\VibeCoding\module_4
docker-compose up -d
```

## Docker Desktop 설정 최적화

### 1. 리소스 할당

Docker Desktop → Settings → Resources:
- **CPUs**: 2-4 cores
- **Memory**: 4-8 GB
- **Disk**: 20 GB

### 2. WSL 2 통합

Docker Desktop → Settings → Resources → WSL Integration:
- ✅ Enable integration with my default WSL distro

### 3. 파일 공유

Docker Desktop → Settings → Resources → File Sharing:
- 프로젝트 디렉토리 경로 추가

## 문제 해결

### Docker Desktop이 시작되지 않음

1. **가상화 확인**
   ```powershell
   # 작업 관리자 → 성능 → CPU
   # "가상화: 사용" 확인
   ```

2. **Hyper-V 활성화** (WSL 2 대신 사용하는 경우)
   ```powershell
   # 관리자 권한 PowerShell
   Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V -All
   ```

3. **로그 확인**
   - Docker Desktop 아이콘 → Troubleshoot → View logs

### "docker: command not found" 에러

1. Docker Desktop이 실행 중인지 확인
2. 새 터미널 창 열기 (환경 변수 갱신)
3. 시스템 재부팅

### WSL 2 설치 에러

```powershell
# WSL 업데이트
wsl --update

# WSL 상태 확인
wsl --status
```

### 네트워크 에러

```powershell
# Docker 네트워크 재설정
docker network prune -f
docker network create monitoring
```

## Docker 없이 실행하기

Docker 설치가 어려운 경우, 다른 방법으로 실행:

### Node.js 버전 (추천)

```cmd
run_exporter_node.bat
```

Node.js만 설치되어 있으면 즉시 실행 가능!

### Python 버전

1. Python 설치: `INSTALL_PYTHON.md` 참고
2. 실행: `run_exporter.bat`

## 참고 자료

- [Docker Desktop 공식 문서](https://docs.docker.com/desktop/install/windows-install/)
- [WSL 2 설치 가이드](https://docs.microsoft.com/en-us/windows/wsl/install)
- [Docker 문제 해결](https://docs.docker.com/desktop/troubleshoot/overview/)

## 설치 완료 후

Docker가 정상 작동하면:

```powershell
# 전체 스택 실행
docker-compose up -d

# 상태 확인
docker-compose ps

# 로그 확인
docker-compose logs -f

# 접속
# Metrics: http://localhost:9100/metrics
# Prometheus: http://localhost:9090
# Grafana: http://localhost:3000
```
