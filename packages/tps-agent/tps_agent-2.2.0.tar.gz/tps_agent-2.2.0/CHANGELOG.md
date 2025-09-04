# Changelog

All notable changes to TPS Agent will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.2.0] - 2024-09-04

### 🆕 Added
- **Database-Driven Throttling**: New `@db_throttle` decorator that retrieves TPS limits from PostgreSQL database
- **Hierarchical Throttling**: New `@hierarchical_throttle` decorator for Gateway → Endpoint level controls
- **Wait-on-Limit Feature**: Smart waiting up to 30 minutes instead of immediate throttling failures
- **TPS Recommendations System**: AI-powered optimal TPS suggestions based on historical data
- **Grafana Dashboard Integration**: Pre-built dashboards with TPS recommendations and analytics
- **PostgreSQL Strategy Enhancements**: Auto-creation of TPS limits table with 1000 TPS defaults
- **Dynamic TPS Management**: Database APIs for real-time TPS limit updates

### 🔧 Improved
- **PostgreSQL Strategy**: Added comprehensive TPS limits management with CRUD operations
- **Performance Optimization**: Efficient connection pooling and batch processing
- **Error Handling**: Better exception handling and logging for database operations
- **Documentation**: Comprehensive README with advanced usage examples

### 📊 Dashboard Features
- **Gateway Statistics Panel**: Success rates, request counts, performance metrics
- **Endpoint Statistics Panel**: Individual endpoint performance analysis  
- **TPS Recommendations Panels**: 
  - Ultra Conservative TPS (85% of baseline) 🟢
  - Recommended Optimal TPS (95% of baseline) 🟡
  - Recommended Max TPS (99% of baseline) 🔴
- **Real-time Monitoring**: Live TPS, response times, error rates

### 🗄️ Database Schema
- **tps_limits table**: Automatic TPS limits management
- **Optimized indexes**: Performance-tuned for time-series queries
- **Auto-initialization**: Tables and indexes created automatically

### 🧪 Testing
- **PostgreSQL Integration Tests**: Comprehensive database functionality testing
- **Throttling Tests**: Validation of all throttling strategies
- **Performance Benchmarks**: Sub-millisecond overhead validation

### 📦 Dependencies
- Added `psycopg2-binary` for PostgreSQL strategy
- Updated optional dependencies structure
- Python 3.12 compatibility

## [2.1.1] - 2024-08-15

### 🔧 Fixed
- Fixed PostgreSQL connection pool management
- Improved error handling in transmission layer
- Better cleanup of temporary storage files

### 📈 Improved
- Enhanced performance for high-throughput applications
- More robust retry mechanisms
- Better logging and debugging information

## [2.1.0] - 2024-08-01

### 🆕 Added
- **PostgreSQL Strategy**: Direct database storage without TPS Collector
- **Strategy Pattern**: Flexible architecture supporting multiple backends
- **Hybrid Strategy**: Combine multiple strategies simultaneously
- **Prometheus Strategy**: Export metrics to Prometheus
- **Enhanced Configuration**: Environment variable support

### 🔧 Improved
- Better error handling and recovery
- Improved documentation with strategy examples
- More efficient local storage and transmission

## [2.0.0] - 2024-07-15

### 🆕 Added
- **Strategy-based Architecture**: Complete rewrite with strategy pattern
- **Multiple Storage Backends**: Support for various metric storage systems
- **Enhanced Throttling**: More sophisticated rate limiting algorithms
- **Async Support**: Full async/await compatibility
- **Agent Health Monitoring**: Comprehensive health checks and heartbeats

### 💥 Breaking Changes
- Configuration API changed to support strategies
- Import paths updated for new architecture
- Some legacy decorators deprecated

### 🗑️ Removed
- Legacy single-backend architecture
- Deprecated configuration methods

## [1.2.0] - 2024-06-01

### 🆕 Added
- **Throttling Support**: `@throttle` decorator for rate limiting
- **Better Error Handling**: Comprehensive exception management
- **Metric Tags**: Support for custom metric tags
- **Health Endpoints**: Agent health monitoring

### 🔧 Improved
- Reduced memory footprint
- Better network error handling
- Enhanced logging capabilities

## [1.1.0] - 2024-05-15

### 🆕 Added
- **Async Function Support**: Decorators now work with async functions
- **Batch Transmission**: Improved efficiency with metric batching
- **Automatic Retry**: Built-in retry mechanism for failed transmissions

### 🔧 Improved
- Better connection management
- Enhanced error reporting
- Optimized local storage

## [1.0.0] - 2024-05-01

### 🎉 Initial Release
- **Basic TPS Monitoring**: `@measure_tps` decorator
- **Collector Integration**: Send metrics to TPS Collector server  
- **Local Storage**: Temporary metric storage with cleanup
- **Agent Configuration**: Simple configuration system
- **Documentation**: Complete setup and usage guide

### ✨ Features
- Lightweight and fast
- Zero-configuration setup
- Reliable metric transmission
- Cross-platform compatibility

---

## Release Notes

### Version 2.2.0 - Major Database Enhancement Release

This release represents a significant leap forward in TPS Agent capabilities, focusing on database-driven intelligence and advanced throttling mechanisms. The addition of AI-powered TPS recommendations and Grafana dashboard integration makes this release ideal for production-scale monitoring and optimization.

**Key Highlights:**
- 🎯 **Smart Throttling**: Database-driven limits with intelligent waiting
- 📊 **AI Recommendations**: Historical data analysis for optimal TPS settings  
- 🎛️ **Hierarchical Controls**: Multi-level throttling with Gateway → Endpoint cascade
- 📈 **Visual Analytics**: Pre-built Grafana dashboards with recommendations
- 🔄 **Dynamic Management**: Real-time TPS limit adjustments via database

**Migration Guide:**
Existing users can upgrade seamlessly. New database-driven features are opt-in and don't affect existing collector-based setups.

**Performance Impact:**
- Database operations: < 1ms overhead per decorated function
- Memory usage: Optimized connection pooling
- CPU usage: Efficient batch processing and caching