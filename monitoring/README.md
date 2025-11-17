# Gaming Platform - Monitoring Setup

This directory contains the complete monitoring infrastructure for the Gaming Platform using Prometheus, Grafana, AlertManager, and Loki.

## Components

### 1. Prometheus
- **Purpose**: Metrics collection and alerting
- **Port**: 9090
- **Access**: http://localhost:9090

### 2. Grafana
- **Purpose**: Visualization and dashboards
- **Port**: 3000
- **Access**: http://localhost:3000
- **Default Credentials**:
  - Username: `admin`
  - Password: `admin123`

### 3. AlertManager
- **Purpose**: Alert routing and management
- **Port**: 9093
- **Access**: http://localhost:9093

### 4. Loki & Promtail
- **Purpose**: Log aggregation and querying
- **Port**: 3100 (Loki)

### 5. Exporters
- **Node Exporter**: System metrics (Port: 9100)
- **PostgreSQL Exporter**: Database metrics (Port: 9187)
- **Redis Exporter**: Cache metrics (Port: 9121)

## Quick Start

### Start Monitoring Stack

```bash
# Navigate to monitoring directory
cd monitoring

# Start all monitoring services
docker-compose -f docker-compose.monitoring.yml up -d

# Check status
docker-compose -f docker-compose.monitoring.yml ps

# View logs
docker-compose -f docker-compose.monitoring.yml logs -f
```

### Access Dashboards

1. **Grafana**: http://localhost:3000
   - Login with admin/admin123
   - Navigate to Dashboards → Browse
   - Import pre-configured dashboards

2. **Prometheus**: http://localhost:9090
   - Query metrics directly
   - View active alerts
   - Check targets status

3. **AlertManager**: http://localhost:9093
   - View active alerts
   - Manage silence rules

## Metrics Collection

### Backend API Metrics

The backend exposes metrics at `/metrics` endpoint:

- **HTTP Request Metrics**:
  - `http_requests_total`: Total number of HTTP requests
  - `http_request_duration_seconds`: Request duration histogram
  - `http_request_size_bytes`: Request size
  - `http_response_size_bytes`: Response size

- **Application Metrics**:
  - `game_sessions_active`: Number of active game sessions
  - `game_sessions_created_total`: Total game sessions created
  - `wallet_transactions_total`: Total wallet transactions
  - `payment_processing_duration_seconds`: Payment processing time
  - `user_registrations_total`: Total user registrations
  - `authentication_attempts_total`: Authentication attempts
  - `kyc_submissions_total`: KYC document submissions

### Database Metrics

PostgreSQL exporter provides:
- Connection pool stats
- Query performance
- Table sizes
- Index usage
- Replication lag

### Redis Metrics

Redis exporter provides:
- Memory usage
- Connected clients
- Commands per second
- Hit/miss ratio
- Evicted keys

### System Metrics

Node exporter provides:
- CPU usage
- Memory usage
- Disk I/O
- Network statistics
- Filesystem usage

## Alerts Configuration

Alerts are defined in `prometheus/alerts.yml`:

### Critical Alerts
- **APIDown**: API is unreachable
- **DatabaseDown**: Database connection lost
- **RedisDown**: Redis cache unavailable
- **PaymentProcessingFailure**: High payment failure rate

### Warning Alerts
- **HighErrorRate**: API error rate above threshold
- **SlowAPIResponse**: Response times degraded
- **HighCPUUsage**: CPU usage above 80%
- **HighMemoryUsage**: Memory usage above 85%
- **DiskSpaceLow**: Disk space below 15%

## Alert Notifications

Configure AlertManager to send notifications via:

### Email
```yaml
receivers:
  - name: 'email'
    email_configs:
      - to: 'alerts@yourdomain.com'
        from: 'alertmanager@yourdomain.com'
        smarthost: 'smtp.gmail.com:587'
        auth_username: 'your-email@gmail.com'
        auth_password: 'your-app-password'
```

### Slack
```yaml
receivers:
  - name: 'slack'
    slack_configs:
      - api_url: 'YOUR_SLACK_WEBHOOK_URL'
        channel: '#alerts'
        text: '{{ range .Alerts }}{{ .Annotations.description }}{{ end }}'
```

### PagerDuty
```yaml
receivers:
  - name: 'pagerduty'
    pagerduty_configs:
      - service_key: 'YOUR_PAGERDUTY_KEY'
```

## Grafana Dashboards

### Pre-configured Dashboards

1. **System Overview**
   - CPU, Memory, Disk, Network metrics
   - System load and uptime

2. **API Performance**
   - Request rate and latency
   - Error rates
   - Endpoint performance

3. **Database Performance**
   - Connection pool stats
   - Query performance
   - Table growth

4. **Redis Performance**
   - Memory usage
   - Cache hit ratio
   - Command statistics

5. **Business Metrics**
   - User registrations
   - Game sessions
   - Wallet transactions
   - Payment processing

### Import Custom Dashboard

1. Open Grafana (http://localhost:3000)
2. Click "+" → Import
3. Upload JSON file or paste dashboard ID
4. Select Prometheus as data source

## Log Management with Loki

### Query Logs

In Grafana:
1. Navigate to Explore
2. Select Loki data source
3. Use LogQL queries:

```logql
# All backend logs
{job="backend"}

# Error logs only
{job="backend"} |= "ERROR"

# Filter by level
{job="backend"} | json | level="error"

# Search for specific text
{job="backend"} |~ "payment.*failed"
```

## Performance Tuning

### Prometheus Retention

Adjust retention in `prometheus.yml`:
```yaml
--storage.tsdb.retention.time=30d  # Keep 30 days of data
--storage.tsdb.retention.size=50GB  # Or limit by size
```

### Scrape Interval

Balance between granularity and load:
```yaml
global:
  scrape_interval: 15s  # Default
  
scrape_configs:
  - job_name: 'high-freq'
    scrape_interval: 5s  # More frequent for critical services
```

## Troubleshooting

### Check Prometheus Targets

```bash
curl http://localhost:9090/api/v1/targets
```

### Verify Metrics Endpoint

```bash
curl http://localhost:8000/metrics
```

### Check AlertManager Config

```bash
docker exec gaming_platform_alertmanager amtool check-config /etc/alertmanager/alertmanager.yml
```

### View Container Logs

```bash
docker-compose -f docker-compose.monitoring.yml logs -f prometheus
docker-compose -f docker-compose.monitoring.yml logs -f grafana
docker-compose -f docker-compose.monitoring.yml logs -f alertmanager
```

## Best Practices

1. **Set up notifications** immediately for critical alerts
2. **Monitor alert fatigue** - tune thresholds to reduce false positives
3. **Regular dashboard review** - ensure metrics are meaningful
4. **Capacity planning** - monitor trends for resource planning
5. **Document custom metrics** - keep metrics documentation updated
6. **Test alerts** - regularly test alert routing
7. **Backup Grafana** - export dashboards regularly
8. **Security** - change default passwords immediately

## Maintenance

### Backup Grafana Dashboards

```bash
docker exec gaming_platform_grafana grafana-cli admin reset-admin-password newpassword
```

### Clean Old Prometheus Data

```bash
docker exec gaming_platform_prometheus promtool tsdb create-blocks-from openmetrics /prometheus
```

### Update Components

```bash
docker-compose -f docker-compose.monitoring.yml pull
docker-compose -f docker-compose.monitoring.yml up -d
```

## Resources

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [AlertManager Guide](https://prometheus.io/docs/alerting/latest/alertmanager/)
- [Loki Documentation](https://grafana.com/docs/loki/latest/)
- [PromQL Cheat Sheet](https://promlabs.com/promql-cheat-sheet/)

## Support

For issues or questions:
1. Check logs: `docker-compose logs -f [service]`
2. Verify configuration files
3. Check network connectivity
4. Review Prometheus targets page
5. Consult component documentation
