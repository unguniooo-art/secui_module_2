# System Resource Monitoring

Python 기반 시스템 리소스 모니터링 시스템. Prometheus와 Grafana를 사용하여 CPU, 메모리, 디스크, 네트워크 메트릭을 수집하고 시각화합니다.

## 빠른 시작

### 1. 의존성 설치

```bash
pip install -r requirements.txt
```

### 2. 메트릭 익스포터 실행

```bash
python src/exporters/metrics_exporter.py
```

익스포터가 `http://localhost:9100/metrics`에서 실행됩니다.

### 3. 메트릭 확인

브라우저나 curl로 메트릭을 확인할 수 있습니다:

```bash
curl http://localhost:9100/metrics
```

출력 예시:
```
# HELP node_cpu_usage_percent CPU usage percentage
# TYPE node_cpu_usage_percent gauge
node_cpu_usage_percent 23.4

# HELP node_memory_usage_percent Memory usage percentage
# TYPE node_memory_usage_percent gauge
node_memory_usage_percent 45.8
```

## 프로젝트 구조

```
module_4/
├── src/
│   ├── collectors/          # 메트릭 수집기
│   │   ├── base_collector.py      # 기본 인터페이스
│   │   ├── cpu_collector.py       # CPU 메트릭
│   │   ├── memory_collector.py    # 메모리 메트릭
│   │   ├── disk_collector.py      # 디스크 메트릭
│   │   └── network_collector.py   # 네트워크 메트릭
│   └── exporters/
│       └── metrics_exporter.py    # Prometheus 익스포터
├── config/
│   ├── prometheus.yml             # Prometheus 설정
│   └── alerts/
│       └── system_alerts.yml      # 알림 규칙
├── tests/
│   └── unit/                      # 단위 테스트
├── requirements.txt               # Python 의존성
└── CLAUDE.md                      # 개발 가이드
```

## 주요 기능

### 수집되는 메트릭

- **CPU**: 사용률, 코어별 사용률, 로드 평균
- **메모리**: 사용량, 사용률, Swap 메모리
- **디스크**: 파티션별 사용량, I/O 통계
- **네트워크**: 인터페이스별 송수신 바이트, 연결 통계

### 알림 규칙

- CPU 사용률 > 80% (5분 지속)
- 메모리 사용률 > 90% (3분 지속)
- 디스크 사용률 > 85%
- Swap 사용 시작

## Prometheus와 연동

### Prometheus 설치 (Windows)

```bash
# Prometheus 다운로드
# https://prometheus.io/download/ 에서 다운로드

# 압축 해제 후 실행
prometheus.exe --config.file=config/prometheus.yml
```

### Prometheus 접속

```
http://localhost:9090
```

### 유용한 PromQL 쿼리

```promql
# CPU 사용률
node_cpu_usage_percent

# 메모리 사용률
node_memory_usage_percent

# 디스크 I/O 속도 (5분 평균)
rate(node_disk_io_read_bytes_total[5m])

# 네트워크 대역폭
rate(node_network_receive_bytes_total[1m]) * 8 / 1000000
```

## Grafana 대시보드

Grafana를 사용하여 메트릭을 시각화할 수 있습니다:

1. Grafana 설치: https://grafana.com/grafana/download
2. Prometheus 데이터소스 추가
3. 새 대시보드 생성
4. 패널 추가 및 PromQL 쿼리 입력

## 테스트 실행

```bash
# 모든 테스트 실행
pytest tests/

# 특정 테스트 파일
pytest tests/unit/test_cpu_collector.py

# 커버리지와 함께 실행
pytest --cov=src tests/
```

## 개발

### 코드 포맷팅

```bash
black src/ tests/
```

### 린팅

```bash
flake8 src/ tests/
```

### 타입 체크

```bash
mypy src/
```

## 커스텀 포트로 실행

```bash
python src/exporters/metrics_exporter.py --port 9101
```

## 문제 해결

### 포트가 이미 사용 중

```bash
# Windows
netstat -an | findstr 9100

# Linux/macOS
netstat -an | grep 9100
```

### 메트릭이 수집되지 않음

1. 익스포터가 실행 중인지 확인
2. 방화벽 설정 확인
3. Python 의존성 설치 확인: `pip list`

## 라이선스

MIT

## 참고 자료

- PRD: `docs/system-resource-monitoring-prd.md`
- 개발 가이드: `CLAUDE.md`
- [Prometheus 문서](https://prometheus.io/docs/)
- [psutil 문서](https://psutil.readthedocs.io/)
