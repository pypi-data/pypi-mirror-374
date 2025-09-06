"""Cache manager with high-level operations."""

import asyncio
import contextlib
from dataclasses import dataclass
from typing import Any

from ..utils.logging import get_logger
from .models import CacheStats
from .protocol import CacheProtocol


logger = get_logger("cache.manager")


@dataclass(slots=True)
class CacheManager:
    """High-level cache manager."""

    cache: CacheProtocol
    _cleanup_task: asyncio.Task[None] | None = None

    def __post_init__(self) -> None:
        """Post-initialization setup."""
        logger.info("Cache manager initialized")

    async def start(self) -> None:
        """Start cache manager and background tasks."""
        # Start cleanup task
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        logger.info("Cache manager started")

    async def stop(self) -> None:
        """Stop cache manager and cleanup."""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._cleanup_task

        await self.cache.close()
        logger.info("Cache manager stopped")

    async def __aenter__(self) -> "CacheManager":
        """Async context manager entry."""
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:  # type: ignore
        """Async context manager exit."""
        await self.stop()

    async def _cleanup_loop(self) -> None:
        """Background cleanup loop."""
        while True:
            try:
                await asyncio.sleep(300)  # Cleanup every 5 minutes

                cleaned_count = await self.cache.cleanup_expired()
                if cleaned_count > 0:
                    logger.info("Background cleanup completed", count=cleaned_count)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.exception("Error in cleanup loop", error=str(e))
                await asyncio.sleep(60)  # Wait before retrying

    async def clear_all(self) -> None:
        """Clear all cached data."""
        await self.cache.clear()
        logger.info("Cleared all cached data")

    async def get_stats(self) -> CacheStats:
        """Get cache statistics.

        Returns:
            Cache statistics
        """
        return await self.cache.get_stats()

    async def cleanup_expired(self) -> int:
        """Manually trigger cleanup of expired entries.

        Returns:
            Number of cleaned up entries
        """
        count = await self.cache.cleanup_expired()
        logger.info("Manual cleanup completed", count=count)
        return count

    # Generic cache methods for non-rule content
    async def get(self, key: str) -> Any | None:
        """Get value from cache using string key.

        Args:
            key: String cache key

        Returns:
            Cached value or None if not found
        """
        return await self.cache.get(key)

    async def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        """Set value in cache using string key.

        Args:
            key: String cache key
            value: Value to cache
            ttl: Optional TTL override
        """
        await self.cache.set(key, value, ttl)
