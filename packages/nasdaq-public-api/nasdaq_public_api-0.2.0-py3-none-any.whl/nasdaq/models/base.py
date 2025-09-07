"""
Base model classes for NASDAQ API response dataclasses.
"""

from abc import ABC
from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class BaseModel(ABC):
    """Base model class for all NASDAQ API response dataclasses."""

    def __post_init__(self):
        """Post-initialization processing for data validation and transformation."""
        pass

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "BaseModel":
        """
        Create model instance from dictionary data.

        Args:
            data: Dictionary containing model data

        Returns:
            BaseModel instance
        """
        # Get all field names for the class
        field_names = cls.__annotations__.keys()

        # Filter data to only include relevant fields
        filtered_data = {k: v for k, v in data.items() if k in field_names}

        # Handle missing fields by using defaults or None
        for field_name in field_names:
            if field_name not in filtered_data:
                # Get the field type annotation
                field_type = cls.__annotations__[field_name]
                # Handle Optional types
                if hasattr(field_type, "__args__") and type(None) in field_type.__args__:
                    filtered_data[field_name] = None
                # Try to determine a sensible default based on type
                elif field_type is str:
                    filtered_data[field_name] = ""
                elif field_type is int:
                    filtered_data[field_name] = 0
                elif field_type is float:
                    filtered_data[field_name] = 0.0
                elif field_type is bool:
                    filtered_data[field_name] = False
                elif field_type is datetime:
                    filtered_data[field_name] = datetime.min
                else:
                    filtered_data[field_name] = None

        return cls(**filtered_data)

    def to_dict(self) -> dict[str, Any]:
        """
        Convert model instance to dictionary.

        Returns:
            Dictionary representation of the model
        """
        return {k: v for k, v in self.__dict__.items() if not k.startswith("_")}

    def __str__(self) -> str:
        """String representation of the model."""
        attrs = ", ".join(f"{k}={v}" for k, v in self.__dict__.items() if not k.startswith("_"))
        return f"{self.__class__.__name__}({attrs})"

    def __repr__(self) -> str:
        """Detailed string representation of the model."""
        return self.__str__()


def parse_monetary_value(value: str | float | int | None) -> float | None:
    """
    Parse monetary values with currency signs, commas, and units (M, B).

    Args:
        value: Monetary value as string or number

    Returns:
        Parsed float value or None if parsing fails
    """
    if value is None or value in {"", "N/A"}:
        return None

    if isinstance(value, int | float):
        return float(value)

    if not isinstance(value, str):
        return None

    # Remove currency signs and whitespace
    cleaned_value = value.strip().replace("$", "").replace(",", "")

    # Handle units (millions, billions)
    multiplier = 1.0
    if cleaned_value.endswith("M"):
        multiplier = 1_000_000.0
        cleaned_value = cleaned_value[:-1]
    elif cleaned_value.endswith("B"):
        multiplier = 1_000_000_000.0
        cleaned_value = cleaned_value[:-1]
    elif cleaned_value.endswith("T"):
        multiplier = 1_000_000_000_000.0
        cleaned_value = cleaned_value[:-1]

    # Handle percentage signs
    is_percentage = cleaned_value.endswith("%")
    if is_percentage:
        cleaned_value = cleaned_value[:-1]

    try:
        result = float(cleaned_value) * multiplier
        # If it was a percentage, convert to decimal
        if is_percentage:
            result = result / 100.0
        return result
    except ValueError:
        return None


def parse_datetime_value(date_str: str | datetime | None, formats: list[str]) -> datetime | None:
    """
    Parse datetime values from various string formats.

    Args:
        date_str: Date string or datetime object
        formats: List of datetime formats to try

    Returns:
        Parsed datetime object or None if parsing fails
    """
    if date_str is None or date_str == "":
        return None

    if isinstance(date_str, datetime):
        return date_str

    if not isinstance(date_str, str):
        return None

    for fmt in formats:
        try:
            return datetime.strptime(date_str.strip(), fmt)
        except ValueError:
            continue

    return None
