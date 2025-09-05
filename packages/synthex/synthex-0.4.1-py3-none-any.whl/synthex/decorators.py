from pydantic import validate_call, ValidationError
from typing import Any, Callable, TypeVar
from functools import wraps
import inspect

from synthex.exceptions import ValidationError as SynthexValidationError


T = TypeVar("T", bound=type)


def auto_validate_methods(cls: T) -> T:
    """
    A class decorator that combines Pydantic's `validate_call` for input validation
    and automatic handling of validation errors, raising a custom `SynthexValidationError`.
    This decorator applies to methods that have parameters beyond 'self'.
    """
    
    for attr_name in dir(cls):
        if attr_name.startswith("__"):
            continue

        attr = getattr(cls, attr_name)
        if not callable(attr):
            continue

        # Get method signature and skip methods that only have 'self' as parameter
        sig = inspect.signature(attr)
        params = list(sig.parameters.values())
        if len(params) <= 1:
            continue

        # Apply validate_call to the method
        validated = validate_call(attr)

        # Wrap the method with both validation and error handling
        @wraps(attr)
        def wrapper(*args: Any, __f: Callable[..., Any] = validated, **kwargs: Any) -> Any:
            try:
                return __f(*args, **kwargs)
            except ValidationError as e:
                raise SynthexValidationError(f"Invalid input: {e}") from e

        setattr(cls, attr_name, wrapper)

    return cls
