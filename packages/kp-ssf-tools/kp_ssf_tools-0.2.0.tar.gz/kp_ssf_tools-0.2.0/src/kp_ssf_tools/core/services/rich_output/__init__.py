"""
Rich output service for SSF Tools.

This module provides a Rich-based output service that implements the RichOutputProtocol
for dependency injection across the SSF Tools application.
"""

from kp_ssf_tools.core.services.rich_output.interfaces import (
    MessageSeverity,
    RichOutputProtocol,
)
from kp_ssf_tools.core.services.rich_output.service import RichOutputService

__all__ = [
    "MessageSeverity",
    "RichOutputProtocol",
    "RichOutputService",
]
