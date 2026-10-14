"""Explicit settings for the loopback-only development slice."""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    host: str = "127.0.0.1"
    port: int = 8000
    queue_capacity: int = 64
    send_timeout_sec: float = 1.0
    mock_interval_sec: float = 1.0
    stale_threshold_ms: int = 3000
    enable_mock: bool = True
    storage_dir: Path | None = Path("data/sessions")
    logger_queue_capacity: int = 1024
    logger_flush_timeout_sec: float = 5.0

    def __post_init__(self):
        if self.host not in {"127.0.0.1", "::1"}:
            raise ValueError("This development server must bind loopback")
        if not 1 <= self.queue_capacity <= 64:
            raise ValueError("queue_capacity must be in 1..64")
        if not 0 < self.send_timeout_sec <= 1:
            raise ValueError("send_timeout_sec must be in (0,1]")
        if self.mock_interval_sec <= 0 or self.stale_threshold_ms != 3000:
            raise ValueError("Invalid mock interval or application stale threshold")
        if not 1 <= self.logger_queue_capacity <= 1024:
            raise ValueError("logger_queue_capacity must be in 1..1024")
        if not 0 < self.logger_flush_timeout_sec <= 30:
            raise ValueError("logger_flush_timeout_sec must be in (0,30]")
