"""Timestamp service package."""

from kp_ssf_tools.core.services.timestamp.interfaces import TimestampProtocol
from kp_ssf_tools.core.services.timestamp.service import TimestampService

__all__ = ["TimestampProtocol", "TimestampService"]
