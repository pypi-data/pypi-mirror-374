"""Cache-related data models."""

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any

from pydantic import BaseModel, Field


type CacheKey = str

# Constants
CACHE_KEY_PARTS_COUNT = 3  # repository_url:branch:file_path


@dataclass
class CacheEntry:
    """Cache entry with metadata."""

    value: Any
    created_at: datetime
    ttl_seconds: int | None = None
    access_count: int = 0
    last_accessed: datetime | None = None
    size_bytes: int | None = None

    @property
    def is_expired(self) -> bool:
        """Check if entry is expired."""
        if self.ttl_seconds is None:
            return False

        expiry_time = self.created_at + timedelta(seconds=self.ttl_seconds)
        return datetime.now(tz=UTC) > expiry_time

    @property
    def expires_at(self) -> datetime | None:
        """Get expiration time."""
        if self.ttl_seconds is None:
            return None
        return self.created_at + timedelta(seconds=self.ttl_seconds)

    def access(self) -> None:
        """Mark entry as accessed."""
        self.access_count += 1
        self.last_accessed = datetime.now(tz=UTC)


class CacheStats(BaseModel):
    """Cache statistics."""

    item_count: int = Field(description="Number of items in cache")
    hit_count: int = Field(default=0, description="Cache hits")
    miss_count: int = Field(default=0, description="Cache misses")
    memory_usage_bytes: int | None = Field(default=None)
    storage_usage_bytes: int | None = Field(default=None)
    oldest_entry: datetime | None = Field(default=None)
    newest_entry: datetime | None = Field(default=None)

    @property
    def hit_rate(self) -> float:
        """Calculate hit rate."""
        total_requests = self.hit_count + self.miss_count
        if total_requests == 0:
            return 0.0
        return self.hit_count / total_requests

    @property
    def miss_rate(self) -> float:
        """Calculate miss rate."""
        return 1.0 - self.hit_rate


class CacheConfiguration(BaseModel):
    """Runtime cache configuration."""

    backend_type: str = Field(description="Cache backend type")
    ttl_seconds: int = Field(description="Default TTL in seconds")
    max_size: int = Field(description="Maximum cache size")
    storage_path: str | None = Field(default=None)
    cleanup_interval_seconds: int = Field(default=300, description="Cleanup interval")
    enable_statistics: bool = Field(default=True, description="Enable statistics collection")
