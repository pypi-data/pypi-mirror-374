"""Decorators for TPS measurement and throttling."""

import asyncio
import functools
import time
from typing import Any, Callable, Dict, Optional, TypeVar, cast

from .agent import get_agent, record_metric

F = TypeVar("F", bound=Callable[..., Any])


def measure_tps(
    gateway: str,
    endpoint: Optional[str] = None,
    tags: Optional[Dict[str, Any]] = None,
    track_errors: bool = True,
) -> Callable[[F], F]:
    """
    Decorator to measure TPS for a function.

    Args:
        gateway: The gateway/service name for grouping metrics
        endpoint: Optional endpoint name (defaults to module.function)
        tags: Optional additional tags for the metric
        track_errors: Whether to track error messages

    Example:
        @measure_tps(gateway="payment_api", endpoint="process_payment")
        def process_payment(amount):
            # Your code here
            pass
    """

    def decorator(func: F) -> F:
        # Safe access to function attributes
        func_module = getattr(func, "__module__", "<unknown>")
        func_name = getattr(func, "__name__", "<unknown>")
        endpoint_name = endpoint or f"{func_module}.{func_name}"

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            agent = get_agent()
            if not agent.config or not agent.config.enable_metrics:
                return func(*args, **kwargs)

            start_time = time.perf_counter()
            error_msg = None
            success = True

            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                success = False
                if track_errors:
                    error_msg = str(e)
                raise
            finally:
                duration_ms = (time.perf_counter() - start_time) * 1000
                record_metric(
                    gateway=gateway,
                    endpoint=endpoint_name,
                    duration_ms=duration_ms,
                    success=success,
                    error=error_msg,
                    tags=tags,
                )

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            agent = get_agent()
            if not agent.config or not agent.config.enable_metrics:
                return await func(*args, **kwargs)

            start_time = time.perf_counter()
            error_msg = None
            success = True

            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                success = False
                if track_errors:
                    error_msg = str(e)
                raise
            finally:
                duration_ms = (time.perf_counter() - start_time) * 1000
                record_metric(
                    gateway=gateway,
                    endpoint=endpoint_name,
                    duration_ms=duration_ms,
                    success=success,
                    error=error_msg,
                    tags=tags,
                )

        if asyncio.iscoroutinefunction(func):
            return cast(F, async_wrapper)
        else:
            return cast(F, wrapper)

    return decorator


class ThrottleException(Exception):
    """Exception raised when rate limit is exceeded."""

    def __init__(self, gateway: str, max_tps: float, current_tps: float):
        self.gateway = gateway
        self.max_tps = max_tps
        self.current_tps = current_tps
        super().__init__(
            f"Rate limit exceeded for {gateway}: {current_tps:.2f} > {max_tps:.2f} TPS"
        )


# Simple in-memory throttling (since we don't have Redis in agent)
class SimpleThrottler:
    """Simple in-memory throttling for agent."""

    def __init__(self):
        self._calls = {}  # gateway -> list of timestamps

    def check_rate_limit(
        self, gateway: str, max_tps: float, window_seconds: int = 1
    ) -> bool:
        """Check if rate limit allows this call."""
        now = time.time()
        window_start = now - window_seconds

        # Clean old calls
        if gateway in self._calls:
            self._calls[gateway] = [
                t for t in self._calls[gateway] if t >= window_start
            ]
        else:
            self._calls[gateway] = []

        # Check rate
        current_calls = len(self._calls[gateway])
        current_tps = current_calls / window_seconds

        if current_tps >= max_tps:
            return False

        # Record this call
        self._calls[gateway].append(now)
        return True

    def get_current_tps(self, gateway: str, window_seconds: int = 1) -> float:
        """Get current TPS for a gateway."""
        now = time.time()
        window_start = now - window_seconds

        if gateway not in self._calls:
            return 0.0

        recent_calls = [t for t in self._calls[gateway] if t >= window_start]
        return len(recent_calls) / window_seconds


# Global throttler instance
_throttler = SimpleThrottler()


def _wait_and_execute(
    func, args, kwargs, gateway, endpoint_key, 
    gateway_max_tps, endpoint_max_tps, window_seconds, max_wait_seconds
):
    """Helper function to wait and execute with throttling."""
    import logging
    
    logger = logging.getLogger(__name__)
    start_wait_time = time.time()
    wait_interval = 0.1  # Start with 100ms wait
    max_wait_interval = 5.0  # Max 5 seconds wait interval
    
    while True:
        # Check if we can execute now
        gateway_ok = True
        endpoint_ok = True
        
        if gateway_max_tps is not None:
            gateway_ok = _throttler.check_rate_limit(gateway, gateway_max_tps, window_seconds)
        
        if endpoint_max_tps is not None and gateway_ok:
            endpoint_ok = _throttler.check_rate_limit(endpoint_key, endpoint_max_tps, window_seconds)
        
        if gateway_ok and endpoint_ok:
            # Both limits allow execution
            return func(*args, **kwargs)
        
        # Check if we've exceeded max wait time
        elapsed = time.time() - start_wait_time
        if elapsed >= max_wait_seconds:
            # Determine which limit was hit for better error message
            if not gateway_ok:
                current_tps = _throttler.get_current_tps(gateway, window_seconds)
                raise ThrottleException(gateway, gateway_max_tps, current_tps)
            else:
                current_tps = _throttler.get_current_tps(endpoint_key, window_seconds)
                raise ThrottleException(endpoint_key, endpoint_max_tps, current_tps)
        
        # Log wait (only occasionally to avoid spam)
        if int(elapsed) % 10 == 0 and elapsed > 10:  # Log every 10 seconds after first 10s
            logger.info(f"Throttle waiting for {gateway}/{endpoint_key}: {elapsed:.1f}s elapsed")
        
        # Wait with exponential backoff (capped)
        time.sleep(wait_interval)
        wait_interval = min(wait_interval * 1.2, max_wait_interval)


async def _wait_and_execute_async(
    func, args, kwargs, gateway, endpoint_key,
    gateway_max_tps, endpoint_max_tps, window_seconds, max_wait_seconds
):
    """Helper function to wait and execute with throttling (async version)."""
    import logging
    
    logger = logging.getLogger(__name__)
    start_wait_time = time.time()
    wait_interval = 0.1  # Start with 100ms wait
    max_wait_interval = 5.0  # Max 5 seconds wait interval
    
    while True:
        # Check if we can execute now
        gateway_ok = True
        endpoint_ok = True
        
        if gateway_max_tps is not None:
            gateway_ok = _throttler.check_rate_limit(gateway, gateway_max_tps, window_seconds)
        
        if endpoint_max_tps is not None and gateway_ok:
            endpoint_ok = _throttler.check_rate_limit(endpoint_key, endpoint_max_tps, window_seconds)
        
        if gateway_ok and endpoint_ok:
            # Both limits allow execution
            return await func(*args, **kwargs)
        
        # Check if we've exceeded max wait time
        elapsed = time.time() - start_wait_time
        if elapsed >= max_wait_seconds:
            # Determine which limit was hit for better error message
            if not gateway_ok:
                current_tps = _throttler.get_current_tps(gateway, window_seconds)
                raise ThrottleException(gateway, gateway_max_tps, current_tps)
            else:
                current_tps = _throttler.get_current_tps(endpoint_key, window_seconds)
                raise ThrottleException(endpoint_key, endpoint_max_tps, current_tps)
        
        # Log wait (only occasionally to avoid spam)
        if int(elapsed) % 10 == 0 and elapsed > 10:  # Log every 10 seconds after first 10s
            logger.info(f"Throttle waiting for {gateway}/{endpoint_key}: {elapsed:.1f}s elapsed")
        
        # Async wait with exponential backoff (capped)
        await asyncio.sleep(wait_interval)
        wait_interval = min(wait_interval * 1.2, max_wait_interval)


def throttle(gateway: str, max_tps: float, window_seconds: int = 1) -> Callable[[F], F]:
    """
    Decorator to throttle function calls based on TPS limit.

    Args:
        gateway: The gateway/service name for throttling
        max_tps: Maximum transactions per second allowed
        window_seconds: Time window for rate calculation

    Example:
        @throttle(gateway="external_api", max_tps=100)
        def call_external_api():
            # Your code here
            pass
    """

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            agent = get_agent()
            if not agent.config or not agent.config.enable_throttling:
                return func(*args, **kwargs)

            if not _throttler.check_rate_limit(gateway, max_tps, window_seconds):
                current_tps = _throttler.get_current_tps(gateway, window_seconds)
                raise ThrottleException(gateway, max_tps, current_tps)

            return func(*args, **kwargs)

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            agent = get_agent()
            if not agent.config or not agent.config.enable_throttling:
                return await func(*args, **kwargs)

            if not _throttler.check_rate_limit(gateway, max_tps, window_seconds):
                current_tps = _throttler.get_current_tps(gateway, window_seconds)
                raise ThrottleException(gateway, max_tps, current_tps)

            return await func(*args, **kwargs)

        if asyncio.iscoroutinefunction(func):
            return cast(F, async_wrapper)
        else:
            return cast(F, wrapper)

    return decorator


def hierarchical_throttle(
    gateway: str,
    endpoint: Optional[str] = None,
    gateway_max_tps: Optional[float] = None,
    endpoint_max_tps: Optional[float] = None,
    window_seconds: int = 1,
    wait_on_limit: bool = False,
    max_wait_seconds: int = 1800,  # 30 minutes
) -> Callable[[F], F]:
    """
    Decorator to apply hierarchical throttling: Gateway → Endpoint.
    
    Args:
        gateway: The gateway/service name for throttling
        endpoint: Optional endpoint name (defaults to module.function)
        gateway_max_tps: Maximum TPS for the entire gateway
        endpoint_max_tps: Maximum TPS for the specific endpoint
        window_seconds: Time window for rate calculation
        wait_on_limit: If True, wait when limit is exceeded instead of immediate exception
        max_wait_seconds: Maximum time to wait (default 1800 = 30 minutes)
        
    Example:
        @hierarchical_throttle(
            gateway="firmbank-gateway", 
            endpoint="withdrawal_transfer",
            gateway_max_tps=200,  # Gateway level limit
            endpoint_max_tps=50,  # Endpoint level limit
            wait_on_limit=True,   # Wait instead of immediate exception
            max_wait_seconds=1800 # Max 30 minutes wait
        )
        def withdrawal_transfer():
            # Your code here
            pass
    """
    
    def decorator(func: F) -> F:
        # Safe access to function attributes
        func_module = getattr(func, "__module__", "<unknown>")
        func_name = getattr(func, "__name__", "<unknown>")
        endpoint_name = endpoint or f"{func_module}.{func_name}"
        endpoint_key = f"{gateway}.{endpoint_name}"
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            agent = get_agent()
            if not agent.config or not agent.config.enable_throttling:
                return func(*args, **kwargs)
            
            if wait_on_limit:
                return _wait_and_execute(
                    func, args, kwargs, gateway, endpoint_key, 
                    gateway_max_tps, endpoint_max_tps, window_seconds, max_wait_seconds
                )
            else:
                # Original immediate exception behavior
                # First check: Gateway level throttling
                if gateway_max_tps is not None:
                    if not _throttler.check_rate_limit(gateway, gateway_max_tps, window_seconds):
                        current_tps = _throttler.get_current_tps(gateway, window_seconds)
                        raise ThrottleException(gateway, gateway_max_tps, current_tps)
                
                # Second check: Endpoint level throttling
                if endpoint_max_tps is not None:
                    if not _throttler.check_rate_limit(endpoint_key, endpoint_max_tps, window_seconds):
                        current_tps = _throttler.get_current_tps(endpoint_key, window_seconds)
                        raise ThrottleException(endpoint_key, endpoint_max_tps, current_tps)
                
                return func(*args, **kwargs)
        
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            agent = get_agent()
            if not agent.config or not agent.config.enable_throttling:
                return await func(*args, **kwargs)
            
            if wait_on_limit:
                return await _wait_and_execute_async(
                    func, args, kwargs, gateway, endpoint_key,
                    gateway_max_tps, endpoint_max_tps, window_seconds, max_wait_seconds
                )
            else:
                # Original immediate exception behavior
                # First check: Gateway level throttling
                if gateway_max_tps is not None:
                    if not _throttler.check_rate_limit(gateway, gateway_max_tps, window_seconds):
                        current_tps = _throttler.get_current_tps(gateway, window_seconds)
                        raise ThrottleException(gateway, gateway_max_tps, current_tps)
                
                # Second check: Endpoint level throttling  
                if endpoint_max_tps is not None:
                    if not _throttler.check_rate_limit(endpoint_key, endpoint_max_tps, window_seconds):
                        current_tps = _throttler.get_current_tps(endpoint_key, window_seconds)
                        raise ThrottleException(endpoint_key, endpoint_max_tps, current_tps)
                
                return await func(*args, **kwargs)
        
        if asyncio.iscoroutinefunction(func):
            return cast(F, async_wrapper)
        else:
            return cast(F, wrapper)
    
    return decorator


def db_throttle(
    gateway: str,
    endpoint: Optional[str] = None,
    window_seconds: int = 1,
    wait_on_limit: bool = False,
    max_wait_seconds: int = 1800,  # 30 minutes
) -> Callable[[F], F]:
    """
    Decorator to throttle based on TPS limits stored in database.
    
    This decorator retrieves TPS limits from the database and applies
    hierarchical throttling (Gateway -> Endpoint).
    
    Args:
        gateway: The gateway/service name
        endpoint: Optional endpoint name (defaults to module.function)
        window_seconds: Time window for rate calculation
        wait_on_limit: If True, wait when limit is exceeded instead of immediate exception
        max_wait_seconds: Maximum time to wait (default 1800 = 30 minutes)
        
    Example:
        @db_throttle(
            gateway="firmbank-gateway",
            endpoint="withdrawal_transfer",
            wait_on_limit=True,
            max_wait_seconds=1800
        )
        def withdrawal_transfer():
            # Your code here
            pass
    """
    
    def decorator(func: F) -> F:
        # Safe access to function attributes
        func_module = getattr(func, "__module__", "<unknown>")
        func_name = getattr(func, "__name__", "<unknown>")
        endpoint_name = endpoint or f"{func_module}.{func_name}"
        endpoint_key = f"{gateway}.{endpoint_name}"
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            agent = get_agent()
            if not agent.config or not agent.config.enable_throttling:
                return func(*args, **kwargs)
            
            # Get TPS limits from database via strategy
            gateway_max_tps, endpoint_max_tps = _get_tps_limits_from_db(gateway, endpoint_name)
            
            if wait_on_limit:
                return _wait_and_execute(
                    func, args, kwargs, gateway, endpoint_key, 
                    gateway_max_tps, endpoint_max_tps, window_seconds, max_wait_seconds
                )
            else:
                # Immediate exception behavior
                # First check: Gateway level throttling
                if gateway_max_tps is not None:
                    if not _throttler.check_rate_limit(gateway, gateway_max_tps, window_seconds):
                        current_tps = _throttler.get_current_tps(gateway, window_seconds)
                        raise ThrottleException(gateway, gateway_max_tps, current_tps)
                
                # Second check: Endpoint level throttling
                if endpoint_max_tps is not None:
                    if not _throttler.check_rate_limit(endpoint_key, endpoint_max_tps, window_seconds):
                        current_tps = _throttler.get_current_tps(endpoint_key, window_seconds)
                        raise ThrottleException(endpoint_key, endpoint_max_tps, current_tps)
                
                return func(*args, **kwargs)
        
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            agent = get_agent()
            if not agent.config or not agent.config.enable_throttling:
                return await func(*args, **kwargs)
            
            # Get TPS limits from database via strategy
            gateway_max_tps, endpoint_max_tps = _get_tps_limits_from_db(gateway, endpoint_name)
            
            if wait_on_limit:
                return await _wait_and_execute_async(
                    func, args, kwargs, gateway, endpoint_key,
                    gateway_max_tps, endpoint_max_tps, window_seconds, max_wait_seconds
                )
            else:
                # Immediate exception behavior
                # First check: Gateway level throttling
                if gateway_max_tps is not None:
                    if not _throttler.check_rate_limit(gateway, gateway_max_tps, window_seconds):
                        current_tps = _throttler.get_current_tps(gateway, window_seconds)
                        raise ThrottleException(gateway, gateway_max_tps, current_tps)
                
                # Second check: Endpoint level throttling  
                if endpoint_max_tps is not None:
                    if not _throttler.check_rate_limit(endpoint_key, endpoint_max_tps, window_seconds):
                        current_tps = _throttler.get_current_tps(endpoint_key, window_seconds)
                        raise ThrottleException(endpoint_key, endpoint_max_tps, current_tps)
                
                return await func(*args, **kwargs)
        
        if asyncio.iscoroutinefunction(func):
            return cast(F, async_wrapper)
        else:
            return cast(F, wrapper)
    
    return decorator


def _get_tps_limits_from_db(gateway: str, endpoint: str) -> tuple[Optional[float], Optional[float]]:
    """Get TPS limits from database via agent strategy."""
    try:
        agent = get_agent()
        if not hasattr(agent, 'strategy') or not hasattr(agent.strategy, 'get_active_tps_limits'):
            # Fallback to default limits if strategy doesn't support DB limits
            return None, None
        
        limits = agent.strategy.get_active_tps_limits()
        
        gateway_max_tps = limits.get('gateway_limits', {}).get(gateway)
        endpoint_max_tps = None
        
        if gateway in limits.get('endpoint_limits', {}):
            endpoint_max_tps = limits['endpoint_limits'][gateway].get(endpoint)
        
        return gateway_max_tps, endpoint_max_tps
        
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to get TPS limits from database: {e}")
        # Return None to disable throttling on error
        return None, None
