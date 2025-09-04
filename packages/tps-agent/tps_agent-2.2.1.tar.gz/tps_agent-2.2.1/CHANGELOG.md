# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.2.1] - 2025-01-04

### Fixed
- Fixed duplicate gateway-level TPS limits creation in PostgreSQL strategy
  - PostgreSQL's UNIQUE constraint treats NULL values as unique, causing multiple entries
  - Replaced `ON CONFLICT` with atomic `INSERT ... SELECT ... WHERE NOT EXISTS` query
  - Added debug logging for better monitoring
  - Prevents race conditions in concurrent environments

### Changed
- Improved `_ensure_tps_limits` method in `PostgreSQLStrategy` for atomic operations

## [2.2.0] - Previous Release

### Added
- PostgreSQL strategy for direct database monitoring
- Strategy-based architecture for flexible monitoring backends
- Support for multiple monitoring strategies (Collector, Prometheus, PostgreSQL, Hybrid)

### Changed
- Refactored agent architecture to use strategy pattern
- Improved modularity and extensibility

## [2.1.0] - Previous Release

### Added
- Initial TPS monitoring capabilities
- Decorator-based metrics collection
- Local metrics storage with automatic transmission