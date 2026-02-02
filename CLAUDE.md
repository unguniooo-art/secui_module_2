# CLAUDE.md

이 파일은 이 저장소에서 작업할 때 Claude Code (claude.ai/code)에 대한 가이드를 제공합니다.

## 프로젝트 개요

시스템 리소스 모니터링은 Prometheus와 Grafana를 사용하여 시스템 메트릭(CPU, 메모리, 디스크, 네트워크)을 수집, 저장, 시각화하는 Python 기반 서버 모니터링 시스템입니다.

**기술 스택**: Python 3.9+, psutil, prometheus_client, Prometheus, Grafana, Alertmanager

**성능 목표**:
- 메트릭 수집 간격: 15초
- 시스템 오버헤드: CPU 5% 미만, 메모리 200MB 미만
- 대시보드 응답 시간: 3초 이내

## 아키텍처

시스템은 Pull 기반 모니터링 아키텍처를 따릅니다:

1. **메트릭 익스포터** (`src/exporters/`): psutil을 통해 시스템 메트릭을 수집하고 Prometheus 포맷으로 :9100/metrics HTTP 엔드포인트 노출
2. **Prometheus 서버**: 15초마다 메트릭을 수집(Pull)하고 시계열 데이터베이스에 저장
3. **Grafana**: Prometheus를 쿼리하고 대시보드 렌더링
4. **Alertmanager**: 알림 규칙을 평가하고 알림 발송

핵심 데이터 흐름: `psutil → Exporter (:9100) ← Prometheus → Grafana`

## 대안 기술 스택 (간단한 구현)

프로젝트 요구사항에 따라 다음과 같은 간단한 대안을 고려할 수 있습니다:

### 1. Node.js 기반 (가장 간단)
```
메트릭 수집: systeminformation (npm)
메트릭 노출: prom-client
저장: Prometheus
시각화: Grafana
```

**30분 안에 시작하기:**
```bash
npm install express systeminformation prom-client
node exporter.js  # Python 없이 동일한 기능
```

**장점:** JavaScript로 풀스택 개발, 비동기 처리로 고성능
**단점:** systeminformation이 일부 플랫폼에서 제한적

### 2. 실시간 웹 대시보드 (프로토타입)
```
백엔드: Node.js + Express
실시간 통신: Socket.io
프론트엔드: Chart.js / ApexCharts
메트릭: systeminformation
```

**1시간 안에 완성:**
```bash
npm install express socket.io systeminformation
node server.js
# 브라우저에서 localhost:3000으로 실시간 모니터링
```

**장점:** 설정 없이 즉시 시각화, 모바일 지원
**단점:** 데이터 저장 기능 없음, 장기 분석 불가

### 3. 올인원 솔루션 (설정 제로)
```
도구: Netdata (단일 바이너리)
설치: curl -Ss https://get.netdata.cloud/kickstart.sh | bash
접속: http://localhost:19999
```

**5분 안에 완료:**
- 자동으로 모든 시스템 메트릭 수집
- 실시간 대시보드 제공 (1초 해상도)
- 알림 내장

**장점:** 제로 설정, 초고성능, 즉시 사용 가능
**단점:** 커스터마이징 제한적, 장기 저장은 별도 설정 필요

### 선택 가이드

| 요구사항 | 추천 스택 | 구현 시간 |
|---------|----------|----------|
| **학습 목적** | Python + Prometheus (현재) | 2-3시간 |
| **빠른 프로토타입** | Node.js + Socket.io | 1시간 |
| **즉시 사용** | Netdata | 5분 |
| **JavaScript 선호** | Node.js + prom-client | 30분 |

**현재 프로젝트는 Python + Prometheus 스택을 기본으로 사용합니다.**

## 개발 명령어

### 설치
```bash
# Python 의존성 설치
pip install -r requirements.txt

# 개발 의존성 설치
pip install -r requirements-dev.txt
```

### 실행
```bash
# 메트릭 익스포터 실행 (자동 리로드 개발 모드)
python src/exporters/metrics_exporter.py --debug

# 커스텀 포트로 실행
python src/exporters/metrics_exporter.py --port 9101

# Prometheus 실행 (설치 필요)
prometheus --config.file=config/prometheus.yml

# Grafana 실행
sudo systemctl start grafana-server
```

### 테스트
```bash
# 모든 테스트 실행
pytest tests/

# 단위 테스트만 실행
pytest tests/unit/

# 통합 테스트 실행
pytest tests/integration/

# 특정 테스트 파일 실행
pytest tests/unit/test_cpu_collector.py

# 커버리지와 함께 실행
pytest --cov=src --cov-report=html tests/

# watch 모드로 테스트 실행 (pytest-watch 필요)
ptw
```

### 린팅 및 포맷팅
```bash
# 린터 실행
flake8 src/ tests/

# 코드 포맷팅
black src/ tests/

# 타입 체크
mypy src/

# 모든 품질 검사 실행
flake8 src/ tests/ && black --check src/ tests/ && mypy src/
```

### 메트릭 검증
```bash
# 익스포터 실행 및 메트릭 노출 확인
curl http://localhost:9100/metrics

# Prometheus 설정 검증
promtool check config config/prometheus.yml

# 알림 규칙 검증
promtool check rules config/alerts/*.yml

# PromQL 쿼리 테스트
curl 'http://localhost:9090/api/v1/query?query=node_cpu_usage_percent'
```

## 코드 구조

### Collector 패턴
모든 메트릭 수집기는 `src/collectors/base_collector.py`에 정의된 공통 인터페이스를 따릅니다:
- `collect()`: 메트릭명 → 값의 딕셔너리 반환
- 각 수집기는 독립적이며 하나의 리소스 타입(CPU, 메모리, 디스크, 네트워크)을 처리
- 수집기는 내부적으로 psutil을 사용하지만 구현을 추상화

### Exporter 구현
익스포터(`src/exporters/metrics_exporter.py`)는 Registry 패턴을 사용합니다:
- 시작 시 모든 수집기 등록
- HTTP 서버가 `/metrics` 엔드포인트 노출
- 각 스크랩 시 수집기를 순회하며 Prometheus 포맷 출력 생성
- `prometheus_client` 라이브러리를 사용하여 메트릭 타입 처리 (Gauge, Counter)

### 메트릭 네이밍 컨벤션
Prometheus 표준을 따릅니다: `node_<subsystem>_<name>_<unit>`
- 예시: `node_cpu_usage_percent`, `node_memory_bytes`
- 순간 값에는 Gauge 사용 (CPU%, 메모리 사용량)
- 누적 값에는 Counter 사용 (디스크 I/O 바이트, 네트워크 패킷)
- 차원에 레이블 포함: `{instance="hostname", cpu="0", mode="user"}`

## 주요 구현 세부사항

### CPU 메트릭
- 코어별 메트릭은 `psutil.cpu_percent(interval=1, percpu=True)` 사용
- 로드 평균은 `psutil.getloadavg()` (Linux/macOS만, Windows는 gracefully 처리)
- `cpu_times_percent()`는 모드별 분류 제공 (user, system, idle, iowait)

### 메모리 메트릭
- `psutil.virtual_memory()`는 total, used, available, percent가 포함된 namedtuple 반환
- 절대값(bytes)과 백분율 모두 추적
- Swap 메트릭은 별도: `psutil.swap_memory()`

### 디스크 메트릭
- 모든 마운트포인트에 대해 `psutil.disk_partitions()` 순회
- 용량 메트릭은 `disk_usage(mountpoint)` 사용
- I/O 통계는 `disk_io_counters(perdisk=True)`
- 프로덕션에서는 가상 파일시스템(tmpfs, devtmpfs) 필터링

### 네트워크 메트릭
- `net_io_counters(pernic=True)`는 인터페이스별 딕셔너리 반환
- Counter 메트릭은 PromQL에서 rate 계산 필요: `rate(node_network_receive_bytes_total[5m])`
- 연결 통계는 `net_connections(kind='inet')`를 통해 수집하지만 비용이 높을 수 있음 - 샘플링 고려

## 설정

### Prometheus 설정
`config/prometheus.yml`에 위치:
- 스크랩 간격: 15s (목표 사양과 일치)
- 스크랩 타임아웃: 10s
- 데이터 보관 기간: 30일
- 타겟: `localhost:9100` (메트릭 익스포터)

### 알림 규칙
`config/alerts/`에 위치:
- `system_alerts.yml`: 리소스 임계값 알림 (CPU>80%, 메모리>90%, 디스크>85%)
- 알림 평가 간격: 15s
- 그룹 대기: 30s, 그룹 간격: 5m (알림 스팸 방지)

### Grafana 대시보드
`dashboards/`에 JSON 정의:
- Grafana UI 또는 프로비저닝을 통해 임포트
- 인스턴스 선택을 위한 변수 사용: `$instance`, `$interface`
- 새로고침 간격을 스크랩 간격과 일치하도록 설정 (15s)

## 테스트 전략

### 단위 테스트
psutil 호출을 모킹하여 알려진 값 반환. 테스트 항목:
- 수집기 로직 및 메트릭 계산
- 엣지 케이스: 누락된 데이터, 권한 오류
- Prometheus 포맷 생성

### 통합 테스트
실제 익스포터를 실행하고 검증:
- HTTP 엔드포인트가 올바르게 응답
- 메트릭 포맷이 유효한 Prometheus exposition 포맷
- 모든 예상 메트릭이 존재

### 부하 테스트
15초 간격으로 메트릭을 수집하는 동안 익스포터 오버헤드 모니터링. 확인 사항:
- CPU 사용률 5% 미만 유지
- 메모리 200MB 미만 유지
- 24시간 실행 동안 메모리 누수 없음

## 크로스 플랫폼 고려사항

- **Windows**: `getloadavg()` 없음, inode 메트릭 없음. `try/except` 블록 사용.
- **Linux**: 전체 기능 세트 사용 가능
- **macOS**: Linux와 유사하지만 일부 메트릭이 다를 수 있음

플랫폼 감지 사용:
```python
import platform
if platform.system() == 'Linux':
    # Linux 전용 메트릭
elif platform.system() == 'Windows':
    # Windows 대체 방법
```

## Prometheus 쿼리 예제

```promql
# 모든 코어의 CPU 사용률
avg(node_cpu_usage_percent{mode!="idle"})

# 메모리 사용률 추이
node_memory_usage_percent

# 디스크 I/O 속도 (bytes/sec)
rate(node_disk_io_read_bytes_total[5m])

# 네트워크 대역폭 (Mbps)
rate(node_network_receive_bytes_total[1m]) * 8 / 1000000

# CPU가 5분간 높을 경우 알림
avg(node_cpu_usage_percent) > 80 for 5m
```

## 일반적인 문제

### 익스포터가 시작되지 않음
- 포트 9100이 이미 사용 중인지 확인: `netstat -an | grep 9100`
- Python 의존성이 설치되었는지 확인: `pip list | grep psutil`

### 메트릭 누락
- 일부 메트릭은 상승된 권한 필요 (예: Windows의 프로세스별 CPU)
- try/except와 함께 `psutil` 사용하고 사용 불가능한 메트릭에 대해 경고 로그

### Prometheus가 스크랩하지 않음
- 익스포터가 실행 중인지 확인: `curl localhost:9100/metrics`
- Prometheus 타겟 페이지 확인: `http://localhost:9090/targets`
- 스크랩 오류에 대한 Prometheus 로그 검토

### 높은 메모리 사용량
- `prometheus.yml`의 보관 설정 확인
- 메트릭 카디널리티 감소 (PID 같은 높은 카디널리티 레이블 피하기)
- Prometheus WAL 압축 활성화

## 문서 참조

- PRD: `docs/system-resource-monitoring-prd.md`
- psutil 문서: https://psutil.readthedocs.io/
- Prometheus exposition 포맷: https://prometheus.io/docs/instrumenting/exposition_formats/
- PromQL 가이드: https://prometheus.io/docs/prometheus/latest/querying/basics/
