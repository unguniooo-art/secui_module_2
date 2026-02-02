# 빠른 시작 가이드

## 🎨 새로운 기능: 실시간 대시보드!

Node.js 버전이 **아름다운 실시간 웹 대시보드**를 포함하도록 업데이트되었습니다!

**주요 특징:**
- 🎯 실시간 메트릭 업데이트 (3초마다)
- 📊 시각적 프로그레스 바
- 💻 CPU, 메모리, 디스크 사용률 표시
- ⚙️ 시스템 정보 자동 감지
- 📱 반응형 디자인 (모바일 지원)
- 🎨 모던한 그라디언트 UI

**접속 주소:** http://localhost:9100/

## Windows에서 실행하기

### ⭐ 방법 1: Node.js 버전 (가장 쉬움 + UI 대시보드!)

1. `run_exporter_node.bat` 파일을 더블클릭
2. 자동으로 의존성 설치 및 실행
3. 브라우저에서 접속:
   - **대시보드**: `http://localhost:9100/` (실시간 UI)
   - **메트릭**: `http://localhost:9100/metrics` (Prometheus)
   - **API**: `http://localhost:9100/api/metrics` (JSON)

### 방법 2: 명령 프롬프트로 Node.js 실행

```cmd
# 1. 프로젝트 디렉토리로 이동
cd C:\Users\student\Desktop\VibeCoding\module_4

# 2. 의존성 설치 (최초 1회만)
npm install

# 3. 익스포터 실행
node src\exporters\metrics_exporter_node.js

# 4. 브라우저에서 확인
# http://localhost:9100/ - 실시간 대시보드
```

### 방법 3: Python 버전 (대시보드 없음)

```cmd
# 1. Python 설치 필요 (INSTALL_PYTHON.md 참고)

# 2. 의존성 설치
python -m pip install psutil prometheus-client

# 3. 익스포터 실행
python src\exporters\metrics_exporter.py

# 4. 메트릭만 확인 가능
# http://localhost:9100/metrics
```

## 테스트 실행

### 배치 파일 사용
```cmd
run_tests.bat
```

### 수동 실행
```cmd
python -m pip install pytest
python -m pytest tests/ -v
```

## 메트릭 확인

익스포터가 실행되면 다음 주소에서 메트릭을 확인할 수 있습니다:

**브라우저**: http://localhost:9100/metrics

**출력 예시**:
```
# HELP node_cpu_usage_percent CPU usage percentage
# TYPE node_cpu_usage_percent gauge
node_cpu_usage_percent 15.3

# HELP node_memory_usage_percent Memory usage percentage
# TYPE node_memory_usage_percent gauge
node_memory_usage_percent 62.4

# HELP node_disk_usage_percent Disk usage percentage
# TYPE node_disk_usage_percent gauge
node_disk_usage_percent{device="C:\\",mountpoint="C:\\"} 45.2
```

## 다음 단계

### Prometheus 설치 (Windows)

1. https://prometheus.io/download/ 에서 다운로드
2. 압축 해제
3. 설정 파일 복사:
   ```cmd
   copy config\prometheus.yml prometheus-2.x.x.windows-amd64\prometheus.yml
   ```
4. Prometheus 실행:
   ```cmd
   cd prometheus-2.x.x.windows-amd64
   prometheus.exe
   ```
5. 브라우저에서 접속: http://localhost:9090

### Grafana 설치 (Windows)

1. https://grafana.com/grafana/download 에서 다운로드
2. 설치 후 실행
3. 브라우저에서 접속: http://localhost:3000
4. 기본 계정: admin / admin
5. Prometheus 데이터소스 추가 (http://localhost:9090)
6. 대시보드 생성

## 문제 해결

### Python을 찾을 수 없음
```cmd
# Python 설치 확인
python --version

# 없다면 Python 설치: https://www.python.org/downloads/
```

### 포트가 이미 사용 중
```cmd
# 사용 중인 프로세스 확인
netstat -ano | findstr :9100

# 프로세스 종료 (PID는 위 명령어에서 확인)
taskkill /PID <PID> /F
```

### 모듈을 찾을 수 없음
```cmd
# 현재 디렉토리에서 실행하는지 확인
cd C:\Users\student\Desktop\VibeCoding\module_4

# 의존성 재설치
python -m pip install --upgrade psutil prometheus-client
```

## 커스텀 설정

### 다른 포트로 실행
```cmd
python src\exporters\metrics_exporter.py --port 9101
```

### 디버그 모드
```cmd
python src\exporters\metrics_exporter.py --debug
```

## 실시간 대시보드 (간단 버전)

Python으로 간단한 웹 대시보드를 만들려면:

```cmd
# 추가 의존성 설치
python -m pip install flask

# 대시보드 실행 (별도 구현 필요)
python dashboard.py
```

## 지원

- 문서: `README.md`, `CLAUDE.md`
- PRD: `docs/system-resource-monitoring-prd.md`
- 이슈: GitHub Issues
