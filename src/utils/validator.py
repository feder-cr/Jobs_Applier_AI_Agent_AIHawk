"""
validator.py - Module to perform validation operations for input data.
"""


class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass


def validate_list_of_strings(data: Any) -> None:
    """Validate that the input is a list of strings."""
    if not isinstance(data, list) or not all(isinstance(item, str) for item in data):
        raise ValidationError("Input must be a list of strings.")


def validate_string(data: Any, min_length: int = 0, max_length: int = 255) -> None:
    """Validate that the input is a string within the specified length range."""
    if not isinstance(data, str) or not min_length <= len(data) <= max_length:
        raise ValidationError(f"Input must be a string with length between {min_length} and {max_length}.")