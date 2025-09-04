# TPS Agent

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI version](https://badge.fury.io/py/tps-agent.svg)](https://badge.fury.io/py/tps-agent)

A comprehensive Python library for measuring, throttling, and managing TPS (Transactions Per Second) in distributed applications. TPS Agent provides flexible strategies for collecting metrics and supports database-driven throttling with Grafana dashboard integration.

## ✨ Features

### Core Functionality
- **🎯 Simple Decorators**: `@measure_tps`, `@throttle`, `@hierarchical_throttle`, `@db_throttle`
- **⚡ Async Support**: Works with both sync and async functions
- **🔄 Multiple Strategies**: Collector, PostgreSQL, Prometheus, Hybrid strategies
- **📊 Real-time Monitoring**: Live metrics collection and visualization
- **🛡️ Intelligent Throttling**: Gateway + Endpoint level controls with wait capability

### Advanced Features
- **🗄️ Database-driven Limits**: Dynamic TPS limits stored in PostgreSQL
- **📈 Grafana Integration**: Pre-built dashboards with TPS recommendations
- **⏱️ Wait-on-Limit**: Smart waiting up to 30 minutes instead of immediate failures
- **🎛️ Hierarchical Controls**: Gateway → Endpoint throttling cascade
- **📋 TPS Recommendations**: AI-powered optimal TPS suggestions based on historical data
- **🔧 Zero Configuration**: Works out of the box with sensible defaults

## 📦 Installation

```bash
pip install tps-agent
```

### Optional Dependencies

```bash
# For PostgreSQL strategy
pip install tps-agent[postgresql]

# For Prometheus integration  
pip install tps-agent[prometheus]

# For all features
pip install tps-agent[all]
```

## 🚀 Quick Start

### 1. Basic Usage with Collector Strategy

```python
from tps_agent import configure_agent, measure_tps, throttle

# Configure once at application startup
configure_agent(
    collector_url="http://tps-collector:8080",
    server_id="web-server-1"
)

@measure_tps(gateway="payment_api")
def process_payment(amount):
    # Your payment processing logic
    return {"status": "success", "amount": amount}

@throttle(gateway="external_api", max_tps=100)
@measure_tps(gateway="external_api")
def call_external_service():
    # This will be throttled to max 100 TPS
    # and metrics will be collected
    return requests.get("https://api.example.com/data")
```

### 2. PostgreSQL Strategy with Database-Driven Throttling

```python
from tps_agent import configure_strategy_agent, PostgreSQLStrategy, db_throttle

# Configure PostgreSQL strategy
strategy = PostgreSQLStrategy(
    server_id="web-server-1",
    # Database connection via environment variables
    # TPS_DB_HOST, TPS_DB_PASSWORD, etc.
)
configure_strategy_agent(strategy)

# Database-driven throttling - limits stored in PostgreSQL
@db_throttle(
    gateway="critical-service",
    endpoint="process_payment",
    wait_on_limit=True,        # Wait up to 30 minutes when throttled
    max_wait_seconds=1800
)
def process_critical_payment(amount):
    # TPS limits automatically retrieved from database
    # Defaults to 1000 TPS, configurable via database
    return {"status": "processed", "amount": amount}
```

### 3. Hierarchical Throttling

```python
from tps_agent import hierarchical_throttle

@hierarchical_throttle(
    gateway="firmbank-gateway",
    endpoint="withdrawal_transfer",
    gateway_max_tps=200,       # Gateway-level limit
    endpoint_max_tps=50,       # Endpoint-level limit  
    wait_on_limit=True,        # Wait when limits exceeded
    max_wait_seconds=300       # Max 5 minutes wait
)
def withdrawal_transfer(amount, account):
    # Both gateway AND endpoint limits must be satisfied
    return {"status": "transferred", "amount": amount}
```

## 🏗️ Architecture

### Strategy Pattern
TPS Agent uses a flexible strategy pattern to support different backend systems:

- **CollectorStrategy**: Send metrics to centralized TPS Collector server
- **PostgreSQLStrategy**: Store metrics directly in PostgreSQL database  
- **PrometheusStrategy**: Export metrics to Prometheus
- **HybridStrategy**: Combine multiple strategies

### Database Schema (PostgreSQL)
```sql
-- Automatic TPS limits management
CREATE TABLE tps_limits (
    gateway VARCHAR(255) NOT NULL,
    endpoint VARCHAR(255),              -- NULL for gateway-level limits
    max_tps INTEGER DEFAULT 1000,
    enabled BOOLEAN DEFAULT true,
    UNIQUE (gateway, endpoint)
);

-- Metrics storage
CREATE TABLE tps_metrics (
    gateway VARCHAR(255) NOT NULL,
    endpoint VARCHAR(255) NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    duration_ms FLOAT NOT NULL,
    success BOOLEAN NOT NULL
);
```

## 📊 Grafana Dashboard

### TPS Recommendations Dashboard
The PostgreSQL strategy includes pre-built Grafana dashboards with:

- **Gateway Statistics**: Success rates, request counts, performance metrics
- **Endpoint Statistics**: Individual endpoint performance analysis
- **TPS Recommendations**: AI-powered optimal TPS suggestions
  - Ultra Conservative TPS (85% of baseline) 🟢
  - Recommended Optimal TPS (95% of baseline) 🟡  
  - Recommended Max TPS (99% of baseline) 🔴
- **Real-time Monitoring**: Live TPS, response times, error rates

### Dashboard Import
```json
{
  "dashboard": "grafana/dashboards/tps-external-db.json",
  "datasource": "PostgreSQL TPS Database"
}
```

## 🔧 Configuration

### Environment Variables (PostgreSQL Strategy)
```bash
# Database Connection
TPS_DB_HOST=localhost
TPS_DB_PORT=5432
TPS_DB_NAME=tps_monitoring
TPS_DB_USER=tps_user
TPS_DB_PASSWORD=your_password

# Agent Settings
TPS_SERVER_ID=web-server-1
TPS_BATCH_SIZE=100
TPS_FLUSH_INTERVAL=30
TPS_MAX_QUEUE_SIZE=10000
```

### Programmatic Configuration
```python
from tps_agent import PostgreSQLStrategy, configure_strategy_agent

strategy = PostgreSQLStrategy(
    server_id="my-service",
    database_url="postgresql://user:pass@localhost/tps_monitoring",
    batch_size=50,
    flush_interval=15,
    max_queue_size=5000
)

# Auto-creates database tables and indexes
configure_strategy_agent(strategy)
```

## 💡 Usage Examples

### Dynamic TPS Limit Management
```python
# Get current TPS limits
limits = strategy.get_tps_limits(gateway="payment-api")
print(f"Current limits: {limits}")

# Update TPS limits
strategy.update_tps_limit("payment-api", None, 500, True)           # Gateway limit
strategy.update_tps_limit("payment-api", "process_payment", 100, True)  # Endpoint limit

# Get active limits for throttling
active = strategy.get_active_tps_limits()
print(f"Gateway limits: {active['gateway_limits']}")
print(f"Endpoint limits: {active['endpoint_limits']}")
```

### Error Handling
```python
from tps_agent import ThrottleException

@db_throttle(gateway="external-api", wait_on_limit=False)
def call_external_api():
    try:
        return requests.get("https://api.example.com/data")
    except ThrottleException as e:
        logger.warning(f"API throttled: {e}")
        return {"error": "rate_limited", "retry_after": 60}
```

## 🧪 Testing

```bash
# Run tests
pytest

# With coverage
pytest --cov=tps_agent

# Integration tests (requires PostgreSQL)
pytest tests/integration/
```

## 📈 Performance

- **Low Overhead**: < 1ms per decorated function call
- **Efficient Batching**: Configurable batch sizes for optimal performance  
- **Connection Pooling**: PostgreSQL strategy uses connection pools
- **Async Support**: Non-blocking operation with async/await
- **Memory Efficient**: Automatic cleanup of old metrics

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [Full Documentation](https://tps-agent.readthedocs.io)
- **Issues**: [GitHub Issues](https://github.com/your-org/tps-agent/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-org/tps-agent/discussions)

## 🗺️ Roadmap

- [ ] **Redis Strategy**: Redis-based metrics storage and throttling
- [ ] **Slack Integration**: Real-time alerts and TPS limit adjustments
- [ ] **REST API**: HTTP API for managing TPS limits
- [ ] **Machine Learning**: Advanced TPS prediction based on traffic patterns
- [ ] **Multi-tenant**: Support for multiple applications in single instance

---

**Made with ❤️ for high-performance distributed systems**