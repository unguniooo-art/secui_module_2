/**
 * Node.js Metrics Exporter
 * Exposes system metrics at :9100/metrics endpoint
 */
const http = require('http');
const promClient = require('prom-client');
const si = require('systeminformation');

// Create a Registry
const register = new promClient.Registry();

// Create Prometheus metrics
const cpuUsage = new promClient.Gauge({
  name: 'node_cpu_usage_percent',
  help: 'CPU usage percentage',
  registers: [register]
});

const cpuCount = new promClient.Gauge({
  name: 'node_cpu_count',
  help: 'Number of CPU cores',
  registers: [register]
});

const memoryTotal = new promClient.Gauge({
  name: 'node_memory_total_bytes',
  help: 'Total memory in bytes',
  registers: [register]
});

const memoryUsed = new promClient.Gauge({
  name: 'node_memory_used_bytes',
  help: 'Used memory in bytes',
  registers: [register]
});

const memoryPercent = new promClient.Gauge({
  name: 'node_memory_usage_percent',
  help: 'Memory usage percentage',
  registers: [register]
});

const diskUsage = new promClient.Gauge({
  name: 'node_disk_usage_percent',
  help: 'Disk usage percentage',
  labelNames: ['device', 'mountpoint'],
  registers: [register]
});

const networkReceive = new promClient.Counter({
  name: 'node_network_receive_bytes_total',
  help: 'Total bytes received',
  labelNames: ['interface'],
  registers: [register]
});

const networkTransmit = new promClient.Counter({
  name: 'node_network_transmit_bytes_total',
  help: 'Total bytes transmitted',
  labelNames: ['interface'],
  registers: [register]
});

// Update metrics function
async function updateMetrics() {
  try {
    // CPU metrics
    const cpuLoad = await si.currentLoad();
    const cpuInfo = await si.cpu();

    cpuUsage.set(cpuLoad.currentLoad);
    cpuCount.set(cpuInfo.cores);

    // Memory metrics
    const mem = await si.mem();
    memoryTotal.set(mem.total);
    memoryUsed.set(mem.used);
    memoryPercent.set((mem.used / mem.total) * 100);

    // Disk metrics
    const disks = await si.fsSize();
    disks.forEach(disk => {
      diskUsage.labels(disk.fs, disk.mount).set(disk.use);
    });

    // Network metrics
    const netStats = await si.networkStats();
    netStats.forEach(net => {
      if (net.iface) {
        networkReceive.labels(net.iface).inc(0); // Initialize
        networkTransmit.labels(net.iface).inc(0); // Initialize

        // Set values directly
        const recvMetric = networkReceive.labels(net.iface);
        const transMetric = networkTransmit.labels(net.iface);

        if (recvMetric && transMetric) {
          recvMetric._value.set(net.rx_bytes || 0);
          transMetric._value.set(net.tx_bytes || 0);
        }
      }
    });

  } catch (error) {
    console.error('Error updating metrics:', error.message);
  }
}

// Get current metrics as JSON
async function getCurrentMetrics() {
  const cpuLoad = await si.currentLoad();
  const mem = await si.mem();
  const disks = await si.fsSize();
  const netStats = await si.networkStats();
  const osInfo = await si.osInfo();
  const cpuInfo = await si.cpu();

  return {
    timestamp: Date.now(),
    cpu: {
      usage: Math.round(cpuLoad.currentLoad * 10) / 10,
      cores: cpuInfo.cores,
      model: cpuInfo.brand
    },
    memory: {
      total: mem.total,
      used: mem.used,
      free: mem.free,
      usagePercent: Math.round((mem.used / mem.total) * 100 * 10) / 10
    },
    disk: disks.map(disk => ({
      fs: disk.fs,
      mount: disk.mount,
      size: disk.size,
      used: disk.used,
      usagePercent: Math.round(disk.use * 10) / 10
    })),
    network: netStats.map(net => ({
      iface: net.iface,
      rx_sec: net.rx_sec,
      tx_sec: net.tx_sec
    })),
    system: {
      platform: osInfo.platform,
      distro: osInfo.distro,
      hostname: osInfo.hostname,
      uptime: Math.floor(si.time().uptime / 60)
    }
  };
}

// HTTP Server
const server = http.createServer(async (req, res) => {
  if (req.url === '/metrics') {
    await updateMetrics();
    res.setHeader('Content-Type', register.contentType);
    res.end(await register.metrics());
  } else if (req.url === '/api/metrics') {
    const data = await getCurrentMetrics();
    res.setHeader('Content-Type', 'application/json');
    res.end(JSON.stringify(data));
  } else {
    res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
    res.end(getDashboardHTML());
  }
});

function getDashboardHTML() {
  return `
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>시스템 리소스 모니터링</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            padding: 20px;
            min-height: 100vh;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
        }

        .header {
            background: white;
            padding: 20px 30px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            margin-bottom: 20px;
        }

        .header h1 {
            color: #667eea;
            font-size: 28px;
            margin-bottom: 10px;
        }

        .header .info {
            color: #666;
            font-size: 14px;
        }

        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }

        .card {
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            transition: transform 0.3s ease;
        }

        .card:hover {
            transform: translateY(-5px);
        }

        .card-title {
            font-size: 18px;
            color: #667eea;
            margin-bottom: 15px;
            font-weight: 600;
        }

        .metric-value {
            font-size: 48px;
            font-weight: bold;
            color: #333;
            line-height: 1;
        }

        .metric-label {
            font-size: 14px;
            color: #999;
            margin-top: 10px;
        }

        .progress-bar {
            width: 100%;
            height: 20px;
            background: #f0f0f0;
            border-radius: 10px;
            overflow: hidden;
            margin-top: 15px;
        }

        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            transition: width 0.5s ease;
            display: flex;
            align-items: center;
            justify-content: flex-end;
            padding-right: 10px;
            color: white;
            font-size: 12px;
            font-weight: bold;
        }

        .progress-fill.warning {
            background: linear-gradient(90deg, #f093fb 0%, #f5576c 100%);
        }

        .progress-fill.danger {
            background: linear-gradient(90deg, #fa709a 0%, #fee140 100%);
        }

        .disk-list {
            margin-top: 15px;
        }

        .disk-item {
            margin-bottom: 15px;
            padding-bottom: 15px;
            border-bottom: 1px solid #f0f0f0;
        }

        .disk-item:last-child {
            border-bottom: none;
            margin-bottom: 0;
            padding-bottom: 0;
        }

        .disk-name {
            font-size: 14px;
            color: #666;
            margin-bottom: 8px;
        }

        .system-info {
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }

        .system-info table {
            width: 100%;
            border-collapse: collapse;
        }

        .system-info td {
            padding: 10px;
            border-bottom: 1px solid #f0f0f0;
        }

        .system-info td:first-child {
            color: #667eea;
            font-weight: 600;
            width: 150px;
        }

        .status {
            display: inline-block;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background: #4ade80;
            margin-right: 10px;
            animation: pulse 2s infinite;
        }

        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }

        .footer {
            text-align: center;
            color: white;
            margin-top: 30px;
            font-size: 14px;
        }

        .footer a {
            color: white;
            text-decoration: none;
            font-weight: bold;
        }

        .last-update {
            color: white;
            text-align: center;
            margin-top: 10px;
            font-size: 12px;
            opacity: 0.8;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1><span class="status"></span>시스템 리소스 모니터링</h1>
            <div class="info">
                실시간 시스템 메트릭 대시보드 | 자동 업데이트: 3초마다
            </div>
        </div>

        <div class="grid">
            <div class="card">
                <div class="card-title">💻 CPU 사용률</div>
                <div class="metric-value" id="cpu-usage">--</div>
                <div class="metric-label">%</div>
                <div class="progress-bar">
                    <div class="progress-fill" id="cpu-progress" style="width: 0%"></div>
                </div>
                <div class="metric-label" style="margin-top: 10px;" id="cpu-info">--</div>
            </div>

            <div class="card">
                <div class="card-title">🧠 메모리 사용률</div>
                <div class="metric-value" id="memory-usage">--</div>
                <div class="metric-label">%</div>
                <div class="progress-bar">
                    <div class="progress-fill" id="memory-progress" style="width: 0%"></div>
                </div>
                <div class="metric-label" style="margin-top: 10px;" id="memory-info">--</div>
            </div>

            <div class="card">
                <div class="card-title">💾 디스크 사용률</div>
                <div class="disk-list" id="disk-list">
                    <div class="metric-label">로딩 중...</div>
                </div>
            </div>
        </div>

        <div class="system-info">
            <div class="card-title">⚙️ 시스템 정보</div>
            <table id="system-info-table">
                <tr><td>호스트명</td><td>--</td></tr>
                <tr><td>운영체제</td><td>--</td></tr>
                <tr><td>플랫폼</td><td>--</td></tr>
                <tr><td>가동 시간</td><td>--</td></tr>
                <tr><td>CPU 모델</td><td>--</td></tr>
                <tr><td>CPU 코어</td><td>--</td></tr>
            </table>
        </div>

        <div class="last-update" id="last-update">마지막 업데이트: --</div>

        <div class="footer">
            Prometheus 메트릭: <a href="/metrics" target="_blank">/metrics</a> |
            API 엔드포인트: <a href="/api/metrics" target="_blank">/api/metrics</a>
        </div>
    </div>

    <script>
        function formatBytes(bytes) {
            if (bytes === 0) return '0 B';
            const k = 1024;
            const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
            const i = Math.floor(Math.log(bytes) / Math.log(k));
            return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
        }

        function updateDashboard() {
            fetch('/api/metrics')
                .then(response => response.json())
                .then(data => {
                    // CPU
                    document.getElementById('cpu-usage').textContent = data.cpu.usage;
                    const cpuProgress = document.getElementById('cpu-progress');
                    cpuProgress.style.width = data.cpu.usage + '%';
                    cpuProgress.textContent = data.cpu.usage + '%';
                    cpuProgress.className = 'progress-fill';
                    if (data.cpu.usage > 80) cpuProgress.className += ' danger';
                    else if (data.cpu.usage > 60) cpuProgress.className += ' warning';
                    document.getElementById('cpu-info').textContent = data.cpu.cores + ' 코어';

                    // Memory
                    document.getElementById('memory-usage').textContent = data.memory.usagePercent;
                    const memProgress = document.getElementById('memory-progress');
                    memProgress.style.width = data.memory.usagePercent + '%';
                    memProgress.textContent = data.memory.usagePercent + '%';
                    memProgress.className = 'progress-fill';
                    if (data.memory.usagePercent > 90) memProgress.className += ' danger';
                    else if (data.memory.usagePercent > 70) memProgress.className += ' warning';
                    document.getElementById('memory-info').textContent =
                        formatBytes(data.memory.used) + ' / ' + formatBytes(data.memory.total);

                    // Disk
                    const diskList = document.getElementById('disk-list');
                    diskList.innerHTML = data.disk.map(disk => \`
                        <div class="disk-item">
                            <div class="disk-name">\${disk.mount} (\${disk.fs})</div>
                            <div class="progress-bar">
                                <div class="progress-fill \${disk.usagePercent > 85 ? 'danger' : disk.usagePercent > 75 ? 'warning' : ''}"
                                     style="width: \${disk.usagePercent}%">\${disk.usagePercent}%</div>
                            </div>
                            <div class="metric-label" style="margin-top: 5px;">
                                \${formatBytes(disk.used)} / \${formatBytes(disk.size)}
                            </div>
                        </div>
                    \`).join('');

                    // System Info
                    const systemTable = document.getElementById('system-info-table');
                    systemTable.innerHTML = \`
                        <tr><td>호스트명</td><td>\${data.system.hostname}</td></tr>
                        <tr><td>운영체제</td><td>\${data.system.distro}</td></tr>
                        <tr><td>플랫폼</td><td>\${data.system.platform}</td></tr>
                        <tr><td>가동 시간</td><td>\${data.system.uptime} 분</td></tr>
                        <tr><td>CPU 모델</td><td>\${data.cpu.model}</td></tr>
                        <tr><td>CPU 코어</td><td>\${data.cpu.cores} 개</td></tr>
                    \`;

                    // Last update
                    const now = new Date();
                    document.getElementById('last-update').textContent =
                        '마지막 업데이트: ' + now.toLocaleTimeString('ko-KR');
                })
                .catch(error => {
                    console.error('Error fetching metrics:', error);
                });
        }

        // Initial update
        updateDashboard();

        // Update every 3 seconds
        setInterval(updateDashboard, 3000);
    </script>
</body>
</html>
  `;
}

const PORT = process.env.PORT || 9100;

server.listen(PORT, () => {
  console.log('╔════════════════════════════════════════════╗');
  console.log('║  System Resource Monitoring Exporter      ║');
  console.log('╚════════════════════════════════════════════╝');
  console.log('');
  console.log(`✓ Server running on http://localhost:${PORT}`);
  console.log(`✓ Metrics endpoint: http://localhost:${PORT}/metrics`);
  console.log('');
  console.log('Press Ctrl+C to stop');
  console.log('');

  // Update metrics every 15 seconds
  setInterval(updateMetrics, 15000);

  // Initial update
  updateMetrics();
});
