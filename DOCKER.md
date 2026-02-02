# Docker 배포 가이드

이 문서는 Docker를 사용하여 시스템 리소스 모니터링 스택을 배포하는 방법을 설명합니다.

## 📋 전제 조건

- Docker 설치 (20.10+)
- Docker Compose 설치 (v2.0+)

### Docker 설치 확인

```bash
docker --version
docker-compose --version
```

## 🚀 빠른 시작

### 1. 전체 스택 실행 (원클릭)

```bash
docker-compose up -d
```

이 명령어로 다음 서비스가 모두 실행됩니다:
- **Exporter** (포트 9100)
- **Prometheus** (포트 9090)
- **Grafana** (포트 3000)
- **Alertmanager** (포트 9093)

### 2. 서비스 확인

```bash
# 실행 중인 컨테이너 확인
docker-compose ps

# 로그 확인
docker-compose logs -f

# 특정 서비스 로그만 확인
docker-compose logs -f exporter
```

### 3. 접속

- **메트릭**: http://localhost:9100/metrics
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000 (admin/admin)
- **Alertmanager**: http://localhost:9093

## 📦 개별 서비스 관리

### Exporter만 실행

```bash
# Docker 이미지 빌드
docker build -t system-metrics-exporter .

# 컨테이너 실행
docker run -d \
  --name exporter \
  -p 9100:9100 \
  system-metrics-exporter

# 로그 확인
docker logs -f exporter
```

### 서비스 중지

```bash
# 전체 스택 중지
docker-compose down

# 데이터 볼륨까지 삭제
docker-compose down -v
```

### 서비스 재시작

```bash
# 전체 재시작
docker-compose restart

# 특정 서비스만 재시작
docker-compose restart exporter
```

## 🔧 설정 커스터마이징

### 환경 변수

`.env` 파일 생성:

```env
# Exporter 설정
EXPORTER_PORT=9100

# Prometheus 설정
PROMETHEUS_PORT=9090
PROMETHEUS_RETENTION=30d

# Grafana 설정
GRAFANA_PORT=3000
GRAFANA_ADMIN_PASSWORD=your_secure_password
```

### 볼륨 마운트

데이터 영속성을 위해 볼륨을 사용합니다:

```yaml
volumes:
  - prometheus-data:/prometheus  # Prometheus 데이터
  - grafana-data:/var/lib/grafana  # Grafana 설정
  - alertmanager-data:/alertmanager  # Alertmanager 데이터
```

### 포트 변경

`docker-compose.yml`에서 포트 매핑 수정:

```yaml
services:
  exporter:
    ports:
      - "9101:9100"  # 호스트:컨테이너
```

## 📊 Grafana 초기 설정

### 1. Prometheus 데이터소스 추가

```bash
# Grafana 접속 후
# Configuration → Data Sources → Add data source → Prometheus
# URL: http://prometheus:9090
```

### 2. 대시보드 가져오기

```bash
# Dashboards → Import → Upload JSON file
# 파일: dashboards/overview-dashboard.json
```

## 🔐 보안 설정

### Grafana 관리자 비밀번호 변경

```yaml
environment:
  - GF_SECURITY_ADMIN_PASSWORD=새로운_비밀번호
```

### Prometheus Basic Auth 추가

`config/prometheus.yml`:

```yaml
basic_auth_users:
  admin: $2y$10$...  # bcrypt 해시
```

### HTTPS 설정

리버스 프록시(Nginx) 사용:

```yaml
services:
  nginx:
    image: nginx:alpine
    ports:
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./certs:/etc/nginx/certs
```

## 📈 모니터링 및 유지보수

### 컨테이너 상태 확인

```bash
# 리소스 사용량
docker stats

# 헬스체크
docker inspect exporter | grep -A 5 Health
```

### 로그 관리

```bash
# 로그 크기 제한 (docker-compose.yml)
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```

### 백업

```bash
# Prometheus 데이터 백업
docker run --rm \
  -v prometheus-data:/data \
  -v $(pwd)/backup:/backup \
  alpine tar czf /backup/prometheus-$(date +%Y%m%d).tar.gz /data

# Grafana 데이터 백업
docker run --rm \
  -v grafana-data:/data \
  -v $(pwd)/backup:/backup \
  alpine tar czf /backup/grafana-$(date +%Y%m%d).tar.gz /data
```

## 🛠️ 문제 해결

### 컨테이너가 시작되지 않음

```bash
# 에러 로그 확인
docker-compose logs exporter

# 컨테이너 재빌드
docker-compose build --no-cache exporter
docker-compose up -d exporter
```

### 메트릭이 수집되지 않음

```bash
# Exporter 컨테이너 내부 접속
docker exec -it exporter bash

# 메트릭 확인
curl localhost:9100/metrics

# Prometheus 타겟 상태 확인
curl http://localhost:9090/api/v1/targets
```

### 디스크 공간 부족

```bash
# 사용하지 않는 이미지 정리
docker system prune -a

# 볼륨 정리 (주의: 데이터 삭제됨)
docker volume prune
```

## 📚 고급 설정

### 멀티 노드 모니터링

`docker-compose.yml`에 추가 exporter 서비스:

```yaml
services:
  exporter-node1:
    build: .
    ports:
      - "9100:9100"

  exporter-node2:
    build: .
    ports:
      - "9101:9100"
```

### Auto-scaling

Docker Swarm 또는 Kubernetes 사용:

```bash
# Docker Swarm
docker swarm init
docker stack deploy -c docker-compose.yml monitoring

# Kubernetes (Helm)
helm install monitoring ./charts/system-monitoring
```

### CI/CD 통합

`.github/workflows/docker.yml`:

```yaml
name: Docker Build and Push
on:
  push:
    branches: [main]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Build Docker image
        run: docker build -t system-metrics-exporter .
      - name: Push to registry
        run: docker push system-metrics-exporter
```

## 🔗 참고 자료

- [Docker 문서](https://docs.docker.com/)
- [Docker Compose 문서](https://docs.docker.com/compose/)
- [Prometheus Docker 이미지](https://hub.docker.com/r/prom/prometheus)
- [Grafana Docker 이미지](https://hub.docker.com/r/grafana/grafana)
