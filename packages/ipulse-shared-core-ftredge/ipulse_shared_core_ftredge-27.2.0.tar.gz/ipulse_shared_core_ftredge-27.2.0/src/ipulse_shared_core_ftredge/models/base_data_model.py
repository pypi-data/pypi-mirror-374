from datetime import datetime, timezone
from typing import Any
from typing import ClassVar
from pydantic import BaseModel, Field, ConfigDict, field_validator
import dateutil.parser

class BaseDataModel(BaseModel):
    """Base model with common fields and configuration"""
    model_config = ConfigDict(frozen=False, extra="forbid")

    # Required class variables that must be defined in subclasses
    VERSION: ClassVar[float]
    DOMAIN: ClassVar[str]
    OBJ_REF: ClassVar[str]

    # Schema versioning
    schema_version: float = Field(
        ...,  # Make this required
        description="Version of this Class == version of DB Schema",
        frozen=True  # Keep schema version frozen for data integrity
    )

    # Audit fields - created fields are frozen after creation, updated fields are mutable
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), frozen=True)
    created_by: str = Field(..., frozen=True)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_by: str = Field(...)

    @classmethod
    def get_collection_name(cls) -> str:
        """Generate standard collection name"""
        return f"{cls.DOMAIN}_{cls.OBJ_REF}s"

    @field_validator('created_at', 'updated_at', mode='before')
    @classmethod
    def parse_datetime(cls, v: Any) -> datetime:
        """
        Ensures that datetime fields are properly parsed into datetime objects.
        Handles both datetime objects (from Firestore) and ISO format strings (from APIs).
        """
        if isinstance(v, datetime):
            # If it's already a datetime object (including Firestore's DatetimeWithNanoseconds),
            # return it directly.
            return v

        if isinstance(v, str):
            # If it's a string, parse it into a datetime object.
            try:
                return dateutil.parser.isoparse(v)
            except (TypeError, ValueError) as e:
                raise ValueError(f"Invalid datetime string format: {v} - {e}")

        # If the type is not a datetime or a string, it's an unsupported format.
        raise ValueError(f"Unsupported type for datetime parsing: {type(v)}")
