# Grafana 대시보드

이 디렉토리에는 Grafana 대시보드 JSON 정의가 포함되어 있습니다.

## 대시보드 목록

### 1. overview-dashboard.json
- **설명**: 시스템 전체 상태 개요
- **포함 패널**:
  - CPU 사용률 게이지
  - 메모리 사용률 게이지
  - 디스크 사용률 게이지
  - CPU 사용률 시계열 그래프
  - 메모리 사용률 시계열 그래프
  - 네트워크 트래픽 그래프
  - 디스크 I/O 그래프

## 대시보드 가져오기

### 방법 1: Grafana UI 사용

1. Grafana 접속 (http://localhost:3000)
2. 좌측 메뉴 → "Dashboards" → "+ Import"
3. "Upload JSON file" 클릭
4. 대시보드 JSON 파일 선택
5. "Load" 클릭
6. Prometheus 데이터소스 선택
7. "Import" 클릭

### 방법 2: API 사용

```bash
# Overview 대시보드 가져오기
curl -X POST http://admin:admin@localhost:3000/api/dashboards/db \
  -H "Content-Type: application/json" \
  -d @dashboards/overview-dashboard.json
```

### 방법 3: Provisioning (자동화)

1. Grafana provisioning 디렉토리 생성
   ```bash
   mkdir -p /etc/grafana/provisioning/dashboards
   ```

2. Provisioning 설정 파일 생성
   ```yaml
   # /etc/grafana/provisioning/dashboards/dashboards.yml
   apiVersion: 1
   providers:
     - name: 'System Monitoring'
       orgId: 1
       folder: 'System'
       type: file
       disableDeletion: false
       updateIntervalSeconds: 10
       allowUiUpdates: true
       options:
         path: /path/to/module_4/dashboards
   ```

3. Grafana 재시작
   ```bash
   sudo systemctl restart grafana-server
   ```

## 대시보드 커스터마이징

### 새로고침 간격 변경
대시보드 JSON에서 `refresh` 값 수정:
```json
"refresh": "15s"  // 15초 간격
```

### 패널 추가
1. Grafana UI에서 대시보드 편집
2. "Add panel" 클릭
3. PromQL 쿼리 입력
4. 저장 후 "Save dashboard" → "Export" → "Save to file"

### 변수 추가
인스턴스 선택 변수:
```json
"templating": {
  "list": [
    {
      "name": "instance",
      "type": "query",
      "query": "label_values(node_cpu_usage_percent, instance)"
    }
  ]
}
```

## PromQL 쿼리 예제

### CPU 관련
```promql
# CPU 사용률
node_cpu_usage_percent

# 평균 CPU 사용률 (5분)
avg_over_time(node_cpu_usage_percent[5m])

# CPU 로드 평균
node_load_average{period="5m"}
```

### 메모리 관련
```promql
# 메모리 사용률
node_memory_usage_percent

# 사용 가능 메모리 (GB)
node_memory_available_bytes / 1024 / 1024 / 1024
```

### 디스크 관련
```promql
# 디스크 사용률 (파티션별)
node_disk_usage_percent

# 디스크 I/O 속도
rate(node_disk_io_read_bytes_total[5m])
```

### 네트워크 관련
```promql
# 네트워크 대역폭 (Mbps)
rate(node_network_receive_bytes_total[1m]) * 8 / 1000000

# 네트워크 패킷 손실
rate(node_network_receive_drop_total[5m])
```

## 문제 해결

### 데이터가 표시되지 않음
1. Prometheus 데이터소스 확인
2. 메트릭 익스포터가 실행 중인지 확인
3. PromQL 쿼리 테스트 (Prometheus UI에서)

### 그래프가 느림
1. 쿼리 간격 조정
2. 시간 범위 축소
3. 집계 함수 사용 (avg, max, min)

## 참고 자료

- [Grafana 문서](https://grafana.com/docs/)
- [Prometheus PromQL](https://prometheus.io/docs/prometheus/latest/querying/basics/)
- [대시보드 Best Practices](https://grafana.com/docs/grafana/latest/best-practices/)
