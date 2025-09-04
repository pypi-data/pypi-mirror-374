__all__ = [
    'aretry',
    'is_true',
    'warn_immediate_errors',
]

import logging
from collections.abc import Callable
from functools import update_wrapper
from inspect import iscoroutinefunction
from typing import Protocol, cast

from httpx import HTTPError
from tenacity import (
    BaseRetrying,
    RetryCallState,
    RetryError,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_fixed,
)

logger = logging.getLogger(__name__)
_ENV_VARS_TRUE_VALUES = frozenset({'1', 'ON', 'YES', 'TRUE'})


def is_true(value: str | None) -> bool:
    if value is None:
        return False
    return value.upper() in _ENV_VARS_TRUE_VALUES


class _Decorator(Protocol):
    def __call__[**P, R](self, f: Callable[P, R], /) -> Callable[P, R]: ...


def aretry(
    *extra_errors: type[BaseException],
    max_attempts: int = 10,
    wait: float = 1,
) -> _Decorator:
    """Wrap sync or async function with a new `Retrying` object.

    By default handles only HTTPError. To add more add more.
    """
    # Protect to not accidentally call aretry(fn)
    assert all(
        isinstance(tp, type) and issubclass(tp, BaseException)
        for tp in extra_errors
    )

    def deco[**P, R](f: Callable[P, R]) -> Callable[P, R]:
        w = retry(
            stop=stop_after_attempt(max_attempts),
            wait=wait_fixed(wait),
            retry=retry_if_exception_type((HTTPError, *extra_errors)),
            before_sleep=warn_immediate_errors,
        )(f)
        r: BaseRetrying = w.retry  # type: ignore[attr-defined]

        async def async_wrapper(*args: P.args, **kwargs: P.kwargs):
            assert iscoroutinefunction(f)
            copy = r.copy()
            try:
                return await copy(f, *args, **kwargs)
            except RetryError as e:
                exc = e.last_attempt.exception()
                assert exc is not None
                raise exc from None

        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            copy = r.copy()
            try:
                return copy(f, *args, **kwargs)
            except RetryError as e:
                exc = e.last_attempt.exception()
                assert exc is not None
                raise exc from None

        w2 = async_wrapper if iscoroutinefunction(f) else wrapper
        return cast('Callable[P, R]', update_wrapper(w2, f))

    return deco


def warn_immediate_errors(s: RetryCallState) -> None:
    if (
        not s.outcome
        or not s.next_action
        or not s.outcome.failed
        or (ex := s.outcome.exception()) is None
    ):
        return

    fn = s.fn
    if fn is None:
        qualname = '<unknown>'
    else:
        name = getattr(fn, '__qualname__', getattr(fn, '__name__', None))
        mod = getattr(fn, '__module__', None)
        qualname = (f'{mod}.{name}' if mod else name) if name else repr(fn)

    logger.warning(
        'Retrying %s in %d seconds as it raised %s: %s.',
        qualname,
        s.next_action.sleep,
        ex.__class__.__name__,
        ex,
    )
