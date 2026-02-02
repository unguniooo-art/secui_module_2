# System Resource Monitoring - Product Requirements Document

## 1. 프로젝트 개요

### 1.1 목적
서버의 시스템 리소스를 실시간으로 수집, 저장, 모니터링하여 시스템 상태를 가시화하고 이상 징후를 조기에 감지하는 모니터링 시스템을 구축한다.

### 1.2 배경
- 서버 장애의 70% 이상이 리소스 고갈로 인해 발생
- 사전 예방적 모니터링을 통한 서비스 가용성 향상 필요
- 리소스 사용 패턴 분석을 통한 용량 계획 수립 필요

### 1.3 범위
- **포함**: CPU, 메모리, 디스크, 네트워크 메트릭 수집 및 모니터링
- **제외**: 애플리케이션 레벨 메트릭, 로그 분석, 분산 트레이싱

---

## 2. 목표 및 성공 지표

### 2.1 비즈니스 목표
- 시스템 장애 사전 감지율 80% 이상 달성
- 평균 장애 탐지 시간(MTTD) 5분 이내로 단축
- 리소스 최적화를 통한 인프라 비용 20% 절감

### 2.2 기술 목표
- 메트릭 수집 주기: 15초 간격
- 데이터 보관 기간: 30일 (원본), 1년 (다운샘플링)
- 시스템 오버헤드: CPU 5% 미만, 메모리 200MB 미만
- 대시보드 응답 시간: 3초 이내

---

## 3. 핵심 기능 요구사항

### 3.1 메트릭 수집
#### 3.1.1 CPU 메트릭
- **수집 항목**
  - 전체 CPU 사용률 (%)
  - 코어별 CPU 사용률 (%)
  - CPU 사용률 분류 (user, system, idle, iowait)
  - CPU 로드 평균 (1분, 5분, 15분)
  - 컨텍스트 스위칭 횟수

- **구현 방법**
  ```python
  import psutil

  # CPU 사용률
  cpu_percent = psutil.cpu_percent(interval=1, percpu=True)

  # CPU 로드 평균
  load_avg = psutil.getloadavg()

  # CPU 상세 시간
  cpu_times = psutil.cpu_times_percent(interval=1)
  ```

#### 3.1.2 메모리 메트릭
- **수집 항목**
  - 전체 메모리 (Total)
  - 사용 중인 메모리 (Used)
  - 사용 가능한 메모리 (Available)
  - 메모리 사용률 (%)
  - Swap 메모리 사용량 및 사용률
  - 캐시/버퍼 메모리

- **구현 방법**
  ```python
  # 메모리 정보
  memory = psutil.virtual_memory()
  swap = psutil.swap_memory()

  metrics = {
      'total': memory.total,
      'used': memory.used,
      'available': memory.available,
      'percent': memory.percent,
      'swap_total': swap.total,
      'swap_used': swap.used,
      'swap_percent': swap.percent
  }
  ```

#### 3.1.3 디스크 메트릭
- **수집 항목**
  - 파티션별 전체 용량
  - 파티션별 사용량 및 사용률
  - 디스크 I/O 통계 (read/write bytes, read/write count)
  - 디스크 I/O 대기 시간
  - inode 사용률 (Linux)

- **구현 방법**
  ```python
  # 디스크 사용량
  disk_usage = psutil.disk_usage('/')

  # 디스크 I/O
  disk_io = psutil.disk_io_counters(perdisk=True)

  # 모든 파티션
  partitions = psutil.disk_partitions()
  ```

#### 3.1.4 네트워크 메트릭
- **수집 항목**
  - 인터페이스별 송수신 바이트
  - 인터페이스별 송수신 패킷
  - 패킷 드롭/에러 수
  - 네트워크 연결 수 (TCP/UDP)
  - 연결 상태별 분류 (ESTABLISHED, TIME_WAIT 등)

- **구현 방법**
  ```python
  # 네트워크 I/O
  net_io = psutil.net_io_counters(pernic=True)

  # 네트워크 연결
  connections = psutil.net_connections(kind='inet')
  ```

#### 3.1.5 프로세스 메트릭
- **수집 항목**
  - 실행 중인 프로세스 수
  - Top N 프로세스 (CPU/메모리 기준)
  - 프로세스별 CPU/메모리 사용량
  - 프로세스별 스레드 수
  - 좀비 프로세스 수

### 3.2 데이터 저장
- **저장소**: Prometheus Time-Series Database
- **보관 정책**
  - 원본 데이터: 30일 (15초 간격)
  - 다운샘플링 데이터: 1년 (5분 평균)
- **데이터 압축**: 활성화
- **백업**: 일일 백업 (7일 보관)

### 3.3 시각화
- **대시보드 구성**
  - Overview 대시보드: 전체 시스템 상태 한눈에 보기
  - CPU 상세 대시보드: 코어별 사용률, 로드 분포
  - 메모리 상세 대시보드: 메모리 사용 추세, Swap 사용
  - 디스크 상세 대시보드: I/O 성능, 용량 추이
  - 네트워크 상세 대시보드: 대역폭, 연결 상태
  - 프로세스 대시보드: Top 프로세스 모니터링

- **차트 타입**
  - 시계열 그래프 (Time-series line chart)
  - 게이지 차트 (사용률 표시)
  - 히트맵 (시간대별 패턴)
  - 테이블 (Top 프로세스)

### 3.4 알림
- **알림 조건**
  - CPU 사용률 > 80% (5분 지속)
  - 메모리 사용률 > 90% (3분 지속)
  - 디스크 사용률 > 85%
  - 디스크 사용률 > 95% (Critical)
  - 네트워크 에러율 > 1%
  - Swap 사용 시작 시점

- **알림 채널**
  - Email
  - Slack/Discord
  - SMS (Critical 알림만)
  - Webhook (커스텀 통합)

- **알림 그룹핑**: 5분 내 동일 알림은 하나로 통합

---

## 4. 기술 스택

### 4.1 메트릭 수집
- **언어**: Python 3.9+
- **라이브러리**:
  - `psutil`: 시스템 리소스 수집
  - `prometheus_client`: Prometheus 메트릭 포맷 생성
- **대안**: Node Exporter (Prometheus 공식), Telegraf (InfluxData)

### 4.2 메트릭 저장
- **Primary**: Prometheus 2.40+
  - 시계열 데이터에 최적화
  - Pull 기반 수집 모델
  - PromQL 쿼리 언어
  - 높은 압축률 (10:1 이상)

### 4.3 시각화
- **Grafana 9.0+**
  - Prometheus 네이티브 지원
  - 다양한 차트 타입
  - 알림 통합
  - 대시보드 버전 관리

### 4.4 알림
- **Alertmanager**
  - Prometheus와 긴밀한 통합
  - 알림 라우팅 및 그룹핑
  - Silence 기능

---

## 5. 시스템 아키텍처

```
┌─────────────────┐
│  Target Server  │
│                 │
│  ┌───────────┐ │
│  │  Metrics  │ │  ← psutil로 리소스 수집
│  │ Exporter  │ │
│  └─────┬─────┘ │
│        │       │
│   :9100/metrics│  ← HTTP Endpoint 노출
└────────┼───────┘
         │
         │ Pull (15s interval)
         │
    ┌────▼────────┐
    │ Prometheus  │  ← 메트릭 저장 및 쿼리
    │   Server    │
    └────┬────┬───┘
         │    │
         │    └────────────┐
         │                 │
    ┌────▼────────┐   ┌────▼─────────┐
    │  Grafana    │   │ Alertmanager │
    │ Dashboard   │   │              │
    └─────────────┘   └──────┬───────┘
                             │
                        ┌────▼─────┐
                        │  Email   │
                        │  Slack   │
                        │  Webhook │
                        └──────────┘
```

### 5.1 컴포넌트 역할
1. **Metrics Exporter**: 시스템 메트릭을 수집하여 HTTP 엔드포인트로 노출
2. **Prometheus Server**: 주기적으로 메트릭을 수집(Pull)하고 시계열 DB에 저장
3. **Grafana**: 메트릭 시각화 및 대시보드 제공
4. **Alertmanager**: 알림 규칙 평가 및 알림 발송

---

## 6. 메트릭 명세

### 6.1 메트릭 네이밍 컨벤션
- Prometheus 표준을 따름
- 형식: `<namespace>_<subsystem>_<name>_<unit>`
- 예시: `node_cpu_seconds_total`, `node_memory_bytes`

### 6.2 주요 메트릭 목록

| 메트릭명 | 타입 | 설명 | 단위 |
|---------|------|------|------|
| `node_cpu_usage_percent` | Gauge | CPU 사용률 | % |
| `node_cpu_load_average` | Gauge | CPU 로드 평균 | - |
| `node_memory_usage_bytes` | Gauge | 메모리 사용량 | bytes |
| `node_memory_usage_percent` | Gauge | 메모리 사용률 | % |
| `node_memory_swap_usage_bytes` | Gauge | Swap 사용량 | bytes |
| `node_disk_usage_bytes` | Gauge | 디스크 사용량 | bytes |
| `node_disk_usage_percent` | Gauge | 디스크 사용률 | % |
| `node_disk_io_read_bytes_total` | Counter | 디스크 읽기 총량 | bytes |
| `node_disk_io_write_bytes_total` | Counter | 디스크 쓰기 총량 | bytes |
| `node_network_receive_bytes_total` | Counter | 네트워크 수신 총량 | bytes |
| `node_network_transmit_bytes_total` | Counter | 네트워크 송신 총량 | bytes |
| `node_network_receive_packets_total` | Counter | 패킷 수신 총 개수 | packets |
| `node_network_transmit_packets_total` | Counter | 패킷 송신 총 개수 | packets |

### 6.3 레이블 정의
```yaml
# 공통 레이블
instance: "server-hostname"
job: "node-exporter"

# CPU 레이블
cpu: "0"  # 코어 번호
mode: "user|system|idle|iowait"

# 디스크 레이블
device: "/dev/sda1"
mountpoint: "/"

# 네트워크 레이블
interface: "eth0"
```

---

## 7. 구현 계획

### 7.1 Phase 1: 기본 메트릭 수집 (Week 1-2)
- [ ] Python 기반 메트릭 수집기 개발
  - [ ] CPU 메트릭 수집
  - [ ] 메모리 메트릭 수집
  - [ ] 디스크 메트릭 수집
  - [ ] 네트워크 메트릭 수집
- [ ] Prometheus 포맷으로 메트릭 노출
- [ ] 유닛 테스트 작성

### 7.2 Phase 2: 저장 및 시각화 (Week 3)
- [ ] Prometheus 서버 설치 및 설정
- [ ] Grafana 설치 및 연동
- [ ] 기본 대시보드 구축
  - [ ] Overview 대시보드
  - [ ] CPU 상세 대시보드
  - [ ] 메모리 상세 대시보드

### 7.3 Phase 3: 알림 시스템 (Week 4)
- [ ] Alertmanager 설정
- [ ] 알림 규칙 정의
- [ ] 알림 채널 연동 (Email, Slack)
- [ ] 알림 테스트 및 튜닝

### 7.4 Phase 4: 최적화 및 확장 (Week 5-6)
- [ ] 프로세스 메트릭 추가
- [ ] 추가 대시보드 구축
- [ ] 성능 최적화
- [ ] 다중 서버 지원
- [ ] 문서화

---

## 8. 설치 및 배포

### 8.1 시스템 요구사항
- **OS**: Linux (Ubuntu 20.04+, CentOS 7+), Windows Server
- **Python**: 3.9 이상
- **메모리**: 최소 2GB (권장 4GB)
- **디스크**: 최소 10GB (데이터 보관 기간에 따라 조정)

### 8.2 설치 단계
```bash
# 1. Python 의존성 설치
pip install psutil prometheus_client

# 2. Prometheus 설치
wget https://github.com/prometheus/prometheus/releases/download/v2.40.0/prometheus-2.40.0.linux-amd64.tar.gz
tar xvfz prometheus-*.tar.gz
cd prometheus-*

# 3. Grafana 설치
sudo apt-get install -y software-properties-common
sudo add-apt-repository "deb https://packages.grafana.com/oss/deb stable main"
sudo apt-get update
sudo apt-get install grafana

# 4. 메트릭 수집기 실행
python metrics_exporter.py

# 5. Prometheus 실행
./prometheus --config.file=prometheus.yml

# 6. Grafana 실행
sudo systemctl start grafana-server
```

---

## 9. 보안 고려사항

### 9.1 인증 및 권한
- Grafana 접근 시 인증 필수
- Prometheus API 접근 제어 (Basic Auth)
- 메트릭 엔드포인트 방화벽 설정

### 9.2 데이터 보호
- HTTPS 통신 (TLS 1.3)
- 민감한 정보 마스킹 (프로세스 명령줄 인자)
- 정기적인 보안 업데이트

---

## 10. 모니터링 및 유지보수

### 10.1 시스템 자체 모니터링
- Prometheus 자체의 메트릭 수집
- Grafana 접근 로그 모니터링
- 디스크 용량 모니터링 (30% 여유 유지)

### 10.2 정기 점검
- 주간: 알림 규칙 적정성 검토
- 월간: 대시보드 업데이트 및 최적화
- 분기: 저장 용량 계획 검토

---

## 11. 참고 자료

### 11.1 공식 문서
- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [psutil Documentation](https://psutil.readthedocs.io/)

### 11.2 대시보드 템플릿
- [Grafana Dashboard for Node Exporter](https://grafana.com/grafana/dashboards/1860)
- [Prometheus Node Exporter Full](https://grafana.com/grafana/dashboards/11074)

### 11.3 Best Practices
- [Prometheus Best Practices](https://prometheus.io/docs/practices/)
- [Grafana Best Practices](https://grafana.com/docs/grafana/latest/best-practices/)

---

## 12. FAQ

**Q: Node Exporter vs 커스텀 Exporter?**
A: Node Exporter는 검증된 솔루션이지만, 커스텀 Exporter는 특정 요구사항에 맞춘 메트릭 수집이 가능합니다. 초기에는 Node Exporter를 사용하고, 필요시 커스텀 메트릭을 추가하는 하이브리드 방식을 권장합니다.

**Q: 메트릭 수집 간격을 15초로 설정한 이유는?**
A: Prometheus의 기본 권장 간격은 15초입니다. 더 짧은 간격(예: 5초)은 시스템 오버헤드를 증가시키고, 더 긴 간격(예: 60초)은 이상 감지가 지연될 수 있습니다.

**Q: Windows 서버도 지원되나요?**
A: psutil은 크로스 플랫폼을 지원하므로 Windows에서도 동작합니다. 단, 일부 메트릭(예: inode)은 Linux에서만 사용 가능합니다.

---

## 변경 이력

| 버전 | 날짜 | 작성자 | 변경 내용 |
|-----|------|--------|----------|
| 1.0 | 2026-02-02 | - | 초안 작성 |

---

## 문의 및 지원

- **프로젝트 리드**: [담당자명]
- **기술 문의**: [이메일]
- **이슈 트래킹**: [GitHub Issues 링크]
