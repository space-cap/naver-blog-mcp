"""재시도 로직 유틸리티."""

import logging
from typing import Callable, Any

from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception,
    before_sleep_log,
    after_log,
)

from .error_handler import is_retryable_error

logger = logging.getLogger(__name__)


def create_retry_decorator(
    max_attempts: int = 3,
    min_wait: int = 2,
    max_wait: int = 10,
    multiplier: int = 2,
):
    """
    재시도 데코레이터를 생성합니다.

    Args:
        max_attempts: 최대 재시도 횟수
        min_wait: 최소 대기 시간 (초)
        max_wait: 최대 대기 시간 (초)
        multiplier: 지수 백오프 배수

    Returns:
        재시도 데코레이터
    """
    return retry(
        # 재시도 가능한 에러만 재시도
        retry=retry_if_exception(is_retryable_error),
        # 최대 시도 횟수
        stop=stop_after_attempt(max_attempts),
        # 지수 백오프
        wait=wait_exponential(multiplier=multiplier, min=min_wait, max=max_wait),
        # 재시도 전 로깅
        before_sleep=before_sleep_log(logger, logging.WARNING),
        # 완료 후 로깅
        after=after_log(logger, logging.INFO),
        # 재시도 시 에러 다시 발생
        reraise=True,
    )


# 기본 재시도 데코레이터 (3회, 2-10초)
retry_on_error = create_retry_decorator()

# 빠른 재시도 (3회, 1-5초)
retry_quick = create_retry_decorator(max_attempts=3, min_wait=1, max_wait=5)

# 느린 재시도 (5회, 5-30초)
retry_slow = create_retry_decorator(max_attempts=5, min_wait=5, max_wait=30)


def retry_with_fallback(fallback_value: Any = None):
    """
    재시도 후 실패 시 fallback 값을 반환하는 데코레이터.

    Args:
        fallback_value: 실패 시 반환할 값

    Example:
        @retry_with_fallback(fallback_value={})
        async def get_data():
            ...
    """
    def decorator(func: Callable):
        @retry_on_error
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                logger.error(f"All retries failed for {func.__name__}: {e}")
                return fallback_value
        return wrapper
    return decorator
