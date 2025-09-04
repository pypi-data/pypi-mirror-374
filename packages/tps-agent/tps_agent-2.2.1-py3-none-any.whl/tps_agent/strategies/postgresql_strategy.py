"""Direct PostgreSQL monitoring strategy."""

import logging
import os
import threading
import time
from datetime import datetime
from queue import Queue
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

import psycopg2
from psycopg2.pool import SimpleConnectionPool

from ..models import Metric
from .base import MonitoringStrategy

logger = logging.getLogger(__name__)


class PostgreSQLStrategy(MonitoringStrategy):
    """Strategy for TPS Agent -> PostgreSQL -> Grafana monitoring.

    This strategy directly stores metrics in PostgreSQL database
    without requiring a separate TPS Collector server.
    """

    def __init__(
        self,
        server_id: Optional[str] = None,
        database_url: Optional[str] = None,
        batch_size: Optional[int] = None,
        flush_interval: Optional[int] = None,
        max_queue_size: Optional[int] = None,
        connection_pool_size: Optional[int] = None,
        connection_pool_max: Optional[int] = None,
        **kwargs,
    ):
        """Initialize PostgreSQL strategy with environment variable support.

        Args:
            server_id: Unique identifier for this server (default: TPS_SERVER_ID env var)
            database_url: PostgreSQL connection URL (default: from TPS_DB_* env vars)
            batch_size: Number of metrics to insert in one batch (default: TPS_BATCH_SIZE env var)
            flush_interval: How often to flush metrics to database in seconds (default: TPS_FLUSH_INTERVAL env var)
            max_queue_size: Maximum number of metrics to queue locally (default: TPS_MAX_QUEUE_SIZE env var)
            connection_pool_size: Minimum connections in pool (default: TPS_CONNECTION_POOL_SIZE env var)
            connection_pool_max: Maximum connections in pool (default: TPS_CONNECTION_POOL_MAX env var)

        Environment Variables:
            TPS_SERVER_ID: Server identifier (default: 'tps-agent-1')
            TPS_DB_HOST: Database host (default: 'localhost')
            TPS_DB_PORT: Database port (default: '5432')
            TPS_DB_NAME: Database name (default: 'tps_monitoring')
            TPS_DB_USER: Database username (default: 'tps_user')
            TPS_DB_PASSWORD: Database password (required)
            TPS_BATCH_SIZE: Batch size (default: 100)
            TPS_FLUSH_INTERVAL: Flush interval in seconds (default: 30)
            TPS_MAX_QUEUE_SIZE: Maximum queue size (default: 10000)
            TPS_CONNECTION_POOL_SIZE: Min pool connections (default: 5)
            TPS_CONNECTION_POOL_MAX: Max pool connections (default: 20)
        """
        # Load configuration from environment variables with defaults
        server_id = server_id or os.getenv("TPS_SERVER_ID", "tps-agent-1")

        # Build database URL from environment variables if not provided
        if database_url is None:
            db_host = os.getenv("TPS_DB_HOST", "localhost")
            db_port = os.getenv("TPS_DB_PORT", "5432")
            db_name = os.getenv("TPS_DB_NAME", "tps_monitoring")
            db_user = os.getenv("TPS_DB_USER", "tps_user")
            db_password = os.getenv("TPS_DB_PASSWORD")

            if db_password is None:
                raise ValueError(
                    "Database password required. Either provide 'database_url' parameter or set 'TPS_DB_PASSWORD' environment variable."
                )

            database_url = (
                f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
            )

        # Load other settings from environment variables
        batch_size = batch_size or int(os.getenv("TPS_BATCH_SIZE", "100"))
        flush_interval = flush_interval or int(os.getenv("TPS_FLUSH_INTERVAL", "30"))
        max_queue_size = max_queue_size or int(os.getenv("TPS_MAX_QUEUE_SIZE", "10000"))
        connection_pool_size = connection_pool_size or int(
            os.getenv("TPS_CONNECTION_POOL_SIZE", "5")
        )
        connection_pool_max = connection_pool_max or int(
            os.getenv("TPS_CONNECTION_POOL_MAX", "20")
        )

        super().__init__(server_id, **kwargs)

        self.database_url = database_url
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        self.max_queue_size = max_queue_size
        self.connection_pool_size = connection_pool_size
        self.connection_pool_max = connection_pool_max

        # Connection pool
        self.connection_pool: Optional[SimpleConnectionPool] = None

        # Metrics queue for batching
        self.metrics_queue: Queue[Metric] = Queue(maxsize=max_queue_size)

        # Background thread for flushing
        self._flush_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._stats = {
            "metrics_queued": 0,
            "metrics_flushed": 0,
            "flush_errors": 0,
            "last_flush": None,
        }

    def initialize(self) -> bool:
        """Initialize the PostgreSQL strategy."""
        try:
            # First, ensure database exists
            if not self._ensure_database_exists():
                return False

            # Create connection pool
            self.connection_pool = SimpleConnectionPool(
                self.connection_pool_size, self.connection_pool_max, self.database_url
            )

            # Test connection
            conn = self.connection_pool.getconn()
            try:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    cursor.fetchone()
                logger.info("Successfully connected to PostgreSQL database")
            finally:
                self.connection_pool.putconn(conn)

            # Create tables if they don't exist
            self._create_tables()

            # Register this agent
            self._register_agent()

            # Start background flush thread
            self._flush_thread = threading.Thread(
                target=self._flush_worker, daemon=True, name="PostgreSQLFlush"
            )
            self._flush_thread.start()

            self._initialized = True
            logger.info(
                f"PostgreSQLStrategy initialized for server_id: {self.server_id}"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to initialize PostgreSQLStrategy: {e}")
            return False

    def _ensure_database_exists(self) -> bool:
        """Ensure the target database exists, create if it doesn't."""
        try:
            # Parse database URL
            parsed = urlparse(self.database_url)
            target_db = parsed.path.lstrip("/")

            # Create connection URL to 'postgres' database (always exists)
            admin_db_url = self.database_url.replace(f"/{target_db}", "/postgres")

            logger.info(f"Checking if database '{target_db}' exists...")

            # Connect to 'postgres' database to check/create target database
            conn = psycopg2.connect(admin_db_url)
            conn.autocommit = True  # Required for CREATE DATABASE

            try:
                with conn.cursor() as cursor:
                    # Check if database exists
                    cursor.execute(
                        "SELECT 1 FROM pg_database WHERE datname = %s", (target_db,)
                    )

                    if cursor.fetchone():
                        logger.info(f"Database '{target_db}' already exists")
                    else:
                        logger.info(f"Creating database '{target_db}'...")
                        cursor.execute(f'CREATE DATABASE "{target_db}"')
                        logger.info(f"✅ Database '{target_db}' created successfully")

                return True

            finally:
                conn.close()

        except Exception as e:
            logger.error(f"Failed to ensure database exists: {e}")
            logger.info(
                "Make sure the database exists or the user has CREATE DATABASE privileges"
            )
            return False

    def record_metric(self, metric: Metric) -> None:
        """Record a metric using PostgreSQL strategy."""
        if not self._initialized:
            logger.warning("PostgreSQLStrategy not initialized, skipping metric")
            return

        # Ensure server_id is set
        metric.server_id = self.server_id

        try:
            # Add to queue (non-blocking)
            self.metrics_queue.put_nowait(metric)
            self._stats["metrics_queued"] += 1
            logger.debug(f"Queued metric: {metric.gateway}/{metric.endpoint}")
        except Exception:
            # Queue is full, log warning and continue
            logger.warning("Metrics queue is full, dropping metric")

    def _create_tables(self) -> None:
        """Create database tables if they don't exist."""
        conn = self.connection_pool.getconn()
        try:
            with conn.cursor() as cursor:
                # Create tps_metrics table
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS tps_metrics (
                        id BIGSERIAL PRIMARY KEY,
                        gateway VARCHAR(255) NOT NULL,
                        endpoint VARCHAR(255) NOT NULL,
                        server_id VARCHAR(255) NOT NULL,
                        timestamp TIMESTAMPTZ NOT NULL,
                        duration_ms FLOAT NOT NULL,
                        success BOOLEAN NOT NULL,
                        error TEXT,
                        tags JSONB,
                        created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
                    )
                """
                )

                # Create indexes
                cursor.execute(
                    """
                    CREATE INDEX IF NOT EXISTS idx_tps_metrics_gateway_timestamp
                    ON tps_metrics (gateway, timestamp)
                """
                )
                cursor.execute(
                    """
                    CREATE INDEX IF NOT EXISTS idx_tps_metrics_server_timestamp
                    ON tps_metrics (server_id, timestamp)
                """
                )

                # Create tps_agents table
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS tps_agents (
                        server_id VARCHAR(255) PRIMARY KEY,
                        first_seen TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                        last_seen TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                        status VARCHAR(50) NOT NULL DEFAULT 'healthy',
                        metrics_count BIGINT DEFAULT 0,
                        local_queue_size INTEGER DEFAULT 0,
                        last_transmission TIMESTAMPTZ,
                        updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
                    )
                """
                )

                cursor.execute(
                    """
                    CREATE INDEX IF NOT EXISTS idx_tps_agents_last_seen
                    ON tps_agents (last_seen)
                """
                )

                # Create 5-minute aggregated statistics table
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS tps_statistics_5min (
                        id BIGSERIAL PRIMARY KEY,
                        gateway VARCHAR(255) NOT NULL,
                        endpoint VARCHAR(255) NOT NULL,
                        time_bucket TIMESTAMPTZ NOT NULL,
                        total_requests INTEGER NOT NULL,
                        successful_requests INTEGER NOT NULL,
                        failed_requests INTEGER NOT NULL,
                        avg_duration_ms FLOAT,
                        min_duration_ms FLOAT,
                        max_duration_ms FLOAT,
                        p50_duration_ms FLOAT,
                        p95_duration_ms FLOAT,
                        p99_duration_ms FLOAT,
                        server_ids TEXT[],
                        created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE (gateway, endpoint, time_bucket)
                    )
                """
                )

                cursor.execute(
                    """
                    CREATE INDEX IF NOT EXISTS idx_tps_statistics_time_bucket
                    ON tps_statistics_5min (time_bucket)
                """
                )
                cursor.execute(
                    """
                    CREATE INDEX IF NOT EXISTS idx_tps_statistics_gateway
                    ON tps_statistics_5min (gateway, time_bucket)
                """
                )

                # Create TPS limits configuration table
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS tps_limits (
                        id BIGSERIAL PRIMARY KEY,
                        gateway VARCHAR(255) NOT NULL,
                        endpoint VARCHAR(255),  -- NULL for gateway-level limits
                        max_tps INTEGER NOT NULL DEFAULT 1000,
                        enabled BOOLEAN NOT NULL DEFAULT true,
                        created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE (gateway, endpoint)
                    )
                """
                )

                cursor.execute(
                    """
                    CREATE INDEX IF NOT EXISTS idx_tps_limits_gateway
                    ON tps_limits (gateway)
                """
                )

                cursor.execute(
                    """
                    CREATE INDEX IF NOT EXISTS idx_tps_limits_enabled
                    ON tps_limits (enabled) WHERE enabled = true
                """
                )

                conn.commit()
                logger.info("Database tables created/verified successfully")

        finally:
            self.connection_pool.putconn(conn)

    def _register_agent(self) -> None:
        """Register this agent in the database."""
        conn = self.connection_pool.getconn()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO tps_agents (server_id, first_seen, last_seen, status)
                    VALUES (%s, NOW(), NOW(), 'healthy')
                    ON CONFLICT (server_id)
                    DO UPDATE SET
                        last_seen = NOW(),
                        status = 'healthy',
                        updated_at = NOW()
                """,
                    (self.server_id,),
                )
                conn.commit()
                logger.info(f"Registered agent: {self.server_id}")
        finally:
            self.connection_pool.putconn(conn)

    def _flush_worker(self) -> None:
        """Background worker to flush metrics to database."""
        logger.info("Started PostgreSQL flush worker")

        while not self._stop_event.is_set():
            try:
                # Collect metrics from queue
                metrics_batch = []

                # Wait for first metric or timeout
                try:
                    metric = self.metrics_queue.get(timeout=self.flush_interval)
                    metrics_batch.append(metric)
                except Exception:
                    # Timeout, check stop event
                    continue

                # Collect additional metrics up to batch_size
                while len(metrics_batch) < self.batch_size:
                    try:
                        metric = self.metrics_queue.get_nowait()
                        metrics_batch.append(metric)
                    except Exception:
                        break  # No more metrics in queue

                if metrics_batch:
                    self._flush_metrics(metrics_batch)

            except Exception as e:
                logger.error(f"Error in flush worker: {e}")
                self._stats["flush_errors"] += 1
                time.sleep(1)  # Brief pause before retrying

        logger.info("PostgreSQL flush worker stopped")

    def _flush_metrics(self, metrics: List[Metric]) -> None:
        """Flush a batch of metrics to the database."""
        if not metrics:
            return

        conn = self.connection_pool.getconn()
        try:
            import json

            with conn.cursor() as cursor:
                # Prepare batch insert
                values = []
                for metric in metrics:
                    # Convert tags dict to JSON string for JSONB column
                    tags_json = json.dumps(metric.tags) if metric.tags else None
                    values.append(
                        (
                            metric.gateway,
                            metric.endpoint,
                            metric.server_id,
                            metric.timestamp,
                            metric.duration_ms,
                            metric.success,
                            metric.error,
                            tags_json,
                        )
                    )

                # Batch insert
                cursor.executemany(
                    """
                    INSERT INTO tps_metrics
                    (gateway, endpoint, server_id, timestamp, duration_ms, success, error, tags)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                    values,
                )

                # Update agent statistics
                cursor.execute(
                    """
                    UPDATE tps_agents
                    SET last_seen = NOW(),
                        metrics_count = metrics_count + %s,
                        local_queue_size = %s,
                        last_transmission = NOW(),
                        updated_at = NOW()
                    WHERE server_id = %s
                """,
                    (len(metrics), self.metrics_queue.qsize(), self.server_id),
                )

                # Auto-create TPS limits for new gateway/endpoint combinations
                self._ensure_tps_limits(cursor, metrics)

                conn.commit()

                self._stats["metrics_flushed"] += len(metrics)
                self._stats["last_flush"] = datetime.utcnow()

                logger.debug(f"Flushed {len(metrics)} metrics to PostgreSQL")

        except Exception as e:
            logger.error(f"Failed to flush metrics to database: {e}")
            self._stats["flush_errors"] += 1
            conn.rollback()
        finally:
            self.connection_pool.putconn(conn)

    def _ensure_tps_limits(self, cursor, metrics: List[Metric]) -> None:
        """Ensure TPS limits exist for all gateway/endpoint combinations in metrics."""
        try:
            # Collect unique gateway/endpoint combinations
            gateway_endpoints = set()
            gateways = set()
            
            for metric in metrics:
                gateways.add(metric.gateway)
                gateway_endpoints.add((metric.gateway, metric.endpoint))
            
            # Ensure gateway-level limits exist
            # Note: We need to use a partial unique index to handle NULL values properly
            # For now, use INSERT with a subquery to check existence atomically
            for gateway in gateways:
                cursor.execute(
                    """
                    INSERT INTO tps_limits (gateway, endpoint, max_tps, enabled)
                    SELECT %s, NULL, 1000, true
                    WHERE NOT EXISTS (
                        SELECT 1 FROM tps_limits 
                        WHERE gateway = %s AND endpoint IS NULL
                        LIMIT 1
                    )
                    """,
                    (gateway, gateway)
                )
                
                if cursor.rowcount > 0:
                    logger.debug(f"Inserted gateway-level limit for {gateway}")
                else:
                    logger.debug(f"Gateway-level limit already exists for {gateway}")
            
            # Ensure endpoint-level limits exist
            # Using ON CONFLICT for endpoints since non-NULL endpoints work correctly with unique constraints
            for gateway, endpoint in gateway_endpoints:
                if endpoint is not None:  # Only insert if endpoint is not NULL
                    cursor.execute(
                        """
                        INSERT INTO tps_limits (gateway, endpoint, max_tps, enabled)
                        VALUES (%s, %s, 1000, true)
                        ON CONFLICT (gateway, endpoint) DO NOTHING
                        """,
                        (gateway, endpoint)
                    )
            
            logger.debug(f"Ensured TPS limits for {len(gateways)} gateways and {len(gateway_endpoints)} endpoints")
            
        except Exception as e:
            logger.error(f"Failed to ensure TPS limits: {e}")
            # Don't raise - this shouldn't block metric insertion

    def get_tps_limits(self, gateway: Optional[str] = None, endpoint: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get TPS limits configuration.
        
        Args:
            gateway: Filter by gateway (optional)
            endpoint: Filter by endpoint (optional, requires gateway)
            
        Returns:
            List of TPS limit configurations
        """
        if not self._initialized:
            return []
        
        conn = self.connection_pool.getconn()
        try:
            with conn.cursor() as cursor:
                if gateway and endpoint:
                    # Get specific endpoint limit
                    cursor.execute(
                        """
                        SELECT gateway, endpoint, max_tps, enabled, created_at, updated_at
                        FROM tps_limits
                        WHERE gateway = %s AND endpoint = %s
                        ORDER BY gateway, endpoint
                        """,
                        (gateway, endpoint)
                    )
                elif gateway:
                    # Get all limits for a gateway
                    cursor.execute(
                        """
                        SELECT gateway, endpoint, max_tps, enabled, created_at, updated_at
                        FROM tps_limits
                        WHERE gateway = %s
                        ORDER BY endpoint NULLS FIRST
                        """,
                        (gateway,)
                    )
                else:
                    # Get all limits
                    cursor.execute(
                        """
                        SELECT gateway, endpoint, max_tps, enabled, created_at, updated_at
                        FROM tps_limits
                        ORDER BY gateway, endpoint NULLS FIRST
                        """
                    )
                
                results = []
                for row in cursor.fetchall():
                    results.append({
                        'gateway': row[0],
                        'endpoint': row[1],
                        'max_tps': row[2],
                        'enabled': row[3],
                        'created_at': row[4],
                        'updated_at': row[5]
                    })
                
                return results
        
        except Exception as e:
            logger.error(f"Failed to get TPS limits: {e}")
            return []
        finally:
            self.connection_pool.putconn(conn)

    def update_tps_limit(self, gateway: str, endpoint: Optional[str], max_tps: int, enabled: bool = True) -> bool:
        """Update TPS limit configuration.
        
        Args:
            gateway: Gateway name
            endpoint: Endpoint name (None for gateway-level limit)
            max_tps: Maximum TPS allowed
            enabled: Whether the limit is enabled
            
        Returns:
            True if update was successful
        """
        if not self._initialized:
            return False
        
        conn = self.connection_pool.getconn()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO tps_limits (gateway, endpoint, max_tps, enabled, updated_at)
                    VALUES (%s, %s, %s, %s, NOW())
                    ON CONFLICT (gateway, endpoint)
                    DO UPDATE SET
                        max_tps = EXCLUDED.max_tps,
                        enabled = EXCLUDED.enabled,
                        updated_at = NOW()
                    """,
                    (gateway, endpoint, max_tps, enabled)
                )
                
                conn.commit()
                
                limit_type = "gateway" if endpoint is None else "endpoint"
                target = gateway if endpoint is None else f"{gateway}/{endpoint}"
                logger.info(f"Updated TPS limit for {limit_type} '{target}': {max_tps} TPS (enabled: {enabled})")
                
                return True
        
        except Exception as e:
            logger.error(f"Failed to update TPS limit: {e}")
            conn.rollback()
            return False
        finally:
            self.connection_pool.putconn(conn)

    def get_active_tps_limits(self) -> Dict[str, Dict[str, int]]:
        """Get all active TPS limits organized by gateway and endpoint.
        
        Returns:
            Dict with structure: {
                'gateway_limits': {'gateway1': max_tps, ...},
                'endpoint_limits': {'gateway1': {'endpoint1': max_tps, ...}, ...}
            }
        """
        if not self._initialized:
            return {'gateway_limits': {}, 'endpoint_limits': {}}
        
        conn = self.connection_pool.getconn()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT gateway, endpoint, max_tps
                    FROM tps_limits
                    WHERE enabled = true
                    ORDER BY gateway, endpoint
                    """
                )
                
                gateway_limits = {}
                endpoint_limits = {}
                
                for row in cursor.fetchall():
                    gateway, endpoint, max_tps = row
                    
                    if endpoint is None:
                        # Gateway-level limit
                        gateway_limits[gateway] = max_tps
                    else:
                        # Endpoint-level limit
                        if gateway not in endpoint_limits:
                            endpoint_limits[gateway] = {}
                        endpoint_limits[gateway][endpoint] = max_tps
                
                return {
                    'gateway_limits': gateway_limits,
                    'endpoint_limits': endpoint_limits
                }
        
        except Exception as e:
            logger.error(f"Failed to get active TPS limits: {e}")
            return {'gateway_limits': {}, 'endpoint_limits': {}}
        finally:
            self.connection_pool.putconn(conn)

    def get_stats(self) -> Dict[str, Any]:
        """Get PostgreSQL strategy statistics."""
        if not self._initialized:
            return {"error": "Strategy not initialized"}

        return {
            "strategy": "postgresql",
            "server_id": self.server_id,
            "database_url": self.database_url.split("@")[-1],  # Hide credentials
            "initialized": self._initialized,
            "queue_size": self.metrics_queue.qsize(),
            "max_queue_size": self.max_queue_size,
            "batch_size": self.batch_size,
            "flush_interval": self.flush_interval,
            **self._stats,
        }

    def cleanup(self) -> None:
        """Clean up PostgreSQL strategy resources."""
        logger.info("Cleaning up PostgreSQLStrategy")

        # Stop flush worker
        if self._flush_thread and self._flush_thread.is_alive():
            self._stop_event.set()
            self._flush_thread.join(timeout=5)

        # Flush remaining metrics
        remaining_metrics = []
        while True:
            try:
                metric = self.metrics_queue.get_nowait()
                remaining_metrics.append(metric)
            except Exception:
                break

        if remaining_metrics:
            try:
                self._flush_metrics(remaining_metrics)
                logger.info(f"Flushed {len(remaining_metrics)} remaining metrics")
            except Exception as e:
                logger.error(f"Failed to flush remaining metrics: {e}")

        # Close connection pool
        if self.connection_pool:
            self.connection_pool.closeall()
            self.connection_pool = None

        self._initialized = False
        logger.info("PostgreSQLStrategy cleanup completed")
