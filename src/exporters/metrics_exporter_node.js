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

// HTTP Server
const server = http.createServer(async (req, res) => {
  if (req.url === '/metrics') {
    await updateMetrics();

    res.setHeader('Content-Type', register.contentType);
    res.end(await register.metrics());
  } else {
    res.writeHead(200, { 'Content-Type': 'text/html' });
    res.end(`
      <html>
        <head><title>System Resource Monitor</title></head>
        <body>
          <h1>System Resource Monitoring Exporter</h1>
          <p>Metrics available at <a href="/metrics">/metrics</a></p>
          <hr>
          <p>Running on Node.js ${process.version}</p>
          <p>Update interval: 15 seconds</p>
        </body>
      </html>
    `);
  }
});

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
