# Python 설치 가이드

현재 시스템에 Python이 설치되어 있지 않습니다. 아래 방법 중 하나를 선택하여 설치하세요.

## 방법 1: Python 공식 웹사이트 (추천)

### 단계별 설치

1. **Python 다운로드**
   - 웹사이트: https://www.python.org/downloads/
   - "Download Python 3.12.x" 버튼 클릭

2. **설치 프로그램 실행**
   - 다운로드한 `python-3.12.x-amd64.exe` 실행
   - ⚠️ **중요**: "Add Python to PATH" 체크박스 **반드시 체크**
   - "Install Now" 클릭

3. **설치 확인**
   - 새 명령 프롬프트 열기 (Win + R → cmd)
   - 입력: `python --version`
   - 출력: `Python 3.12.x`

4. **프로젝트 실행**
   ```cmd
   cd C:\Users\student\Desktop\VibeCoding\module_4
   run_exporter.bat
   ```

## 방법 2: Microsoft Store (간편)

1. **Microsoft Store 열기** (Win + S → "Microsoft Store" 검색)
2. "Python 3.12" 검색
3. "설치" 버튼 클릭
4. 설치 완료 후 명령 프롬프트에서 확인:
   ```cmd
   python --version
   ```

## 방법 3: Chocolatey (개발자용)

관리자 권한 PowerShell에서:
```powershell
# Chocolatey 설치 (없는 경우)
Set-ExecutionPolicy Bypass -Scope Process -Force
iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))

# Python 설치
choco install python -y
```

## 방법 4: Node.js로 대체 실행 (Python 없이)

Node.js가 이미 설치되어 있다면 JavaScript 버전으로 실행 가능합니다.

### Node.js 설치 확인
```cmd
node --version
```

### Node.js가 있다면
```cmd
# 프로젝트에 Node.js 버전 생성
cd C:\Users\student\Desktop\VibeCoding\module_4
```

Node.js 버전 구현을 원하시면 말씀해주세요!

## 설치 후 프로젝트 실행

Python 설치가 완료되면:

1. **새 명령 프롬프트 열기** (기존 창은 닫기)
2. 프로젝트 디렉토리로 이동:
   ```cmd
   cd C:\Users\student\Desktop\VibeCoding\module_4
   ```
3. 배치 파일 실행:
   ```cmd
   run_exporter.bat
   ```

또는 수동 실행:
```cmd
python -m pip install psutil prometheus-client
python src\exporters\metrics_exporter.py
```

## 문제 해결

### "Add Python to PATH" 체크를 안 했다면

1. Python을 다시 설치하거나
2. 수동으로 PATH 추가:
   - 시스템 속성 → 고급 → 환경 변수
   - Path 편집
   - 추가: `C:\Users\student\AppData\Local\Programs\Python\Python312`
   - 추가: `C:\Users\student\AppData\Local\Programs\Python\Python312\Scripts`

### 여전히 안 된다면

전체 경로로 실행:
```cmd
C:\Users\student\AppData\Local\Programs\Python\Python312\python.exe -m pip install psutil prometheus-client
C:\Users\student\AppData\Local\Programs\Python\Python312\python.exe src\exporters\metrics_exporter.py
```

## 빠른 확인

설치가 제대로 되었는지 확인:
```cmd
python --version
python -m pip --version
```

정상 출력:
```
Python 3.12.x
pip 24.x.x from ...
```
