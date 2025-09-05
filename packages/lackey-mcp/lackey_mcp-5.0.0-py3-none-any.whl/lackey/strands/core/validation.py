"""AWS profile validation for strands functionality."""

from functools import lru_cache
from typing import Any, Callable, Tuple


class StrandsProfileError(Exception):
    """Raised when AWS profile for strands is not configured or invalid."""

    pass


@lru_cache(maxsize=1)
def validate_aws_profile() -> Tuple[bool, str]:
    """Check if strands AWS profile exists (cached result)."""
    try:
        import boto3

        from lackey.config.config_manager import get_config

        config = get_config()
        profile_name = config.get_aws_profile()
        boto3.Session(profile_name=profile_name)
        return True, ""

    except Exception as e:
        return False, f"AWS profile '{profile_name}' not found or invalid: {str(e)}"


def require_aws_profile(func: Callable[..., Any]) -> Callable[..., Any]:
    """Validate AWS profile before executing strands functions."""

    def wrapper(*args: Any, **kwargs: Any) -> Any:
        is_valid, error_msg = validate_aws_profile()
        if not is_valid:
            raise StrandsProfileError(f"Strands functionality disabled: {error_msg}")
        return func(*args, **kwargs)

    return wrapper
