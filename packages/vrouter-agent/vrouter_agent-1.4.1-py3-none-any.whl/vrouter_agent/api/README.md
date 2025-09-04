# VRouter Agent API Documentation

This document describes the available API endpoints for the VRouter Agent.

## Base URL
The API is served at: `http://localhost:8000` (default)

## Authentication
Currently, the API endpoints are open. Consider implementing authentication for production use.

## Available Endpoints

### Orders API (`/orders`)
- **GET** `/orders/` - List all orders
- **POST** `/orders/` - Create a new order  
- **GET** `/orders/{order_id}` - Get specific order

### Transactions API (`/transactions`)
- **GET** `/transactions/` - List all transactions
- **POST** `/transactions/` - Create a new transaction
- **GET** `/transactions/{transaction_id}` - Get specific transaction
- **GET** `/transactions/status` - Get basic system status

### Tunnel Configuration API (`/tunnel-config`)
- **GET** `/tunnel-config/` - Retrieve all tunnel configurations
  - Query params: `skip`, `limit`, `device_serial`, `status`, `tunnel_type`
- **GET** `/tunnel-config/{config_id}` - Get specific configuration by ID
- **GET** `/tunnel-config/by-tunnel/{tunnel_id}` - Get configuration by tunnel ID
  - Query params: `include_history` (boolean)
- **GET** `/tunnel-config/device/{device_serial}` - Get configurations for specific device
  - Query params: `skip`, `limit`, `status`
- **GET** `/tunnel-config/current-device/` - Get configurations for current device
  - Query params: `skip`, `limit`, `status`
- **GET** `/tunnel-config/stats/` - Get tunnel configuration statistics
- **GET** `/tunnel-config/health/` - Get tunnel config system health

### Telemetry API (`/telemetry`)
- **GET** `/telemetry/metrics/` - Enhanced system metrics with success/failure rates
- **GET** `/telemetry/status/` - System status with health indicators
- **GET** `/telemetry/health/` - Comprehensive health check with issue detection
- **GET** `/telemetry/performance/` - Detailed performance metrics and throughput
- **GET** `/telemetry/system-info/` - General system information and configuration
- **GET** `/telemetry/alerts/` - System alerts and warnings
  - Query params: `severity` (critical, high, medium, low)

## Response Formats

All endpoints return JSON responses with the following standard structure:

### Success Response
```json
{
  "success": true,
  "data": {...},
  "timestamp": "2025-06-05T10:30:00Z"
}
```

### Error Response
```json
{
  "success": false,
  "error": "Error description",
  "timestamp": "2025-06-05T10:30:00Z"
}
```

### Pagination
List endpoints support pagination with `skip` and `limit` parameters:
- `skip`: Number of items to skip (default: 0)
- `limit`: Maximum number of items to return (default: 100, max: 1000)

## Health Monitoring

The telemetry endpoints provide comprehensive health monitoring:

### Health Status Levels
- **healthy**: All systems operating normally
- **warning**: Some issues detected but system is functional
- **critical**: Serious issues requiring immediate attention

### Alert Severity Levels
- **critical**: Immediate action required
- **high**: Action needed soon
- **medium**: Should be addressed
- **low**: Informational

## Example Usage

### Get System Health
```bash
curl http://localhost:8000/telemetry/health/
```

### Get Tunnel Configurations for Current Device
```bash
curl http://localhost:8000/tunnel-config/current-device/
```

### Get Critical Alerts
```bash
curl http://localhost:8000/telemetry/alerts/?severity=critical
```

### Get Performance Metrics
```bash
curl http://localhost:8000/telemetry/performance/
```

## Integration Notes

- The tunnel configuration endpoints integrate with the enhanced stream processor
- Telemetry data is collected from the VRouter agent's internal metrics
- All timestamps are in ISO 8601 format (UTC)
- The API is designed to be stateless and can handle high-frequency polling

## Development

To start the API server:
```bash
cd /srv/salt/base/vrouter-agent/files/vrouter-agent
python -m vrouter_agent.main
```

Or using the start function:
```python
from vrouter_agent.main import start
start()
```
