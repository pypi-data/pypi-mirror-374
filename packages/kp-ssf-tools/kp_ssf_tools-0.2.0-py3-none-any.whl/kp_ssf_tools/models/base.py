from pathlib import Path
from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict, field_serializer

if TYPE_CHECKING:
    from collections.abc import Callable
    from typing import Any as TypingAny

    # Type aliases for serializer function signature
    SerializerFunc = Callable[[TypingAny], TypingAny]
    SerializationInfo = TypingAny


class SSFToolsBaseModel(BaseModel):
    """Base model for all SSF Tools data models. Sets common config."""

    model_config = ConfigDict(
        # Core validation settings
        use_enum_values=True,
        extra="forbid",  # Prevent unknown fields - catch typos early
        validate_assignment=True,  # Validate on assignment - catch errors immediately
        validate_default=True,  # Validate default values - catch model definition errors
        # Early error detection
        str_strip_whitespace=True,  # Auto-strip whitespace from strings - prevent input issues
        validate_return=True,  # Validate return values from validators
        # CLI-friendly behavior
        populate_by_name=True,  # Allow both field names and aliases - flexible CLI inputs
        arbitrary_types_allowed=False,  # Keep strict typing - better error messages
        # Performance for single-user CLI
        frozen=False,  # Allow mutation - CLI tools often modify data
        # Error reporting
        loc_by_alias=False,  # Use field names in error messages, not aliases
        # Serialization settings
        ser_json_inf_nan="constants",  # Handle inf/nan in JSON
    )

    @field_serializer("*", mode="wrap")
    def serialize_paths(
        self,
        value: object,
        serializer: "SerializerFunc",
        _info: "SerializationInfo",
    ) -> object:
        """Convert Path objects to strings and tuples to lists during serialization."""
        if isinstance(value, Path):
            return str(value)

        # Convert tuples to lists for YAML compatibility
        if isinstance(value, tuple):
            return list(value)

        # Suppress Pydantic serializer warnings for enum values
        import warnings
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=UserWarning,
                                   message=".*Pydantic serializer warnings.*")
            return serializer(value)
