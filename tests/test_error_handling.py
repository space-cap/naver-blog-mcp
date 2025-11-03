"""에러 처리 및 재시도 로직 테스트."""

import asyncio
import sys

sys.path.insert(0, "src")

from naver_blog_mcp.utils.exceptions import (
    NaverBlogError,
    TimeoutError,
    NetworkError,
    ElementNotFoundError,
)
from naver_blog_mcp.utils.error_handler import is_retryable_error, should_use_alternative_selector
from naver_blog_mcp.utils.retry import retry_on_error


async def test_exception_types():
    """커스텀 예외 클래스 테스트."""
    print("=" * 60)
    print("커스텀 예외 클래스 테스트")
    print("=" * 60)
    print()

    # 1. 기본 에러
    try:
        raise NaverBlogError("기본 에러", details={"test": "data"})
    except NaverBlogError as e:
        assert e.message == "기본 에러"
        assert e.details["test"] == "data"
        print("✅ NaverBlogError 테스트 통과")

    # 2. TimeoutError
    try:
        raise TimeoutError("타임아웃 에러")
    except TimeoutError as e:
        assert isinstance(e, NaverBlogError)
        print("✅ TimeoutError 테스트 통과")

    # 3. NetworkError
    try:
        raise NetworkError("네트워크 에러")
    except NetworkError as e:
        assert isinstance(e, NaverBlogError)
        print("✅ NetworkError 테스트 통과")

    # 4. ElementNotFoundError
    try:
        raise ElementNotFoundError("요소를 찾을 수 없음")
    except ElementNotFoundError as e:
        assert isinstance(e, NaverBlogError)
        print("✅ ElementNotFoundError 테스트 통과")

    print()


def test_error_classification():
    """에러 분류 테스트."""
    print("=" * 60)
    print("에러 분류 테스트")
    print("=" * 60)
    print()

    # 재시도 가능한 에러
    retryable_errors = [
        NetworkError("네트워크 에러"),
        TimeoutError("타임아웃 에러"),
    ]

    for error in retryable_errors:
        assert is_retryable_error(error), f"{type(error).__name__} should be retryable"
        print(f"✅ {type(error).__name__}은 재시도 가능")

    # 재시도 불가능한 에러
    non_retryable_errors = [
        ElementNotFoundError("요소 없음"),
        ValueError("일반 에러"),
    ]

    for error in non_retryable_errors:
        assert not is_retryable_error(error), f"{type(error).__name__} should not be retryable"
        print(f"✅ {type(error).__name__}은 재시도 불가능")

    # 대체 셀렉터 사용 판단
    selector_errors = [
        ElementNotFoundError("요소 없음"),
    ]

    for error in selector_errors:
        assert should_use_alternative_selector(error)
        print(f"✅ {type(error).__name__}은 대체 셀렉터 사용")

    print()


async def test_retry_decorator():
    """재시도 데코레이터 테스트."""
    print("=" * 60)
    print("재시도 데코레이터 테스트")
    print("=" * 60)
    print()

    attempt_count = 0

    @retry_on_error
    async def failing_function():
        """처음 2번은 실패하고 3번째에 성공하는 함수."""
        nonlocal attempt_count
        attempt_count += 1
        print(f"   시도 #{attempt_count}")

        if attempt_count < 3:
            raise NetworkError(f"네트워크 에러 (시도 {attempt_count})")

        return {"success": True, "attempts": attempt_count}

    try:
        result = await failing_function()
        assert result["success"] is True
        assert result["attempts"] == 3
        print(f"✅ 재시도 성공: {attempt_count}회 시도 후 성공")
    except Exception as e:
        print(f"❌ 재시도 실패: {e}")
        raise

    print()


async def test_retry_exhaustion():
    """재시도 한도 초과 테스트."""
    print("=" * 60)
    print("재시도 한도 초과 테스트")
    print("=" * 60)
    print()

    attempt_count = 0

    @retry_on_error
    async def always_failing_function():
        """항상 실패하는 함수."""
        nonlocal attempt_count
        attempt_count += 1
        print(f"   시도 #{attempt_count}")
        raise NetworkError(f"네트워크 에러 (시도 {attempt_count})")

    try:
        await always_failing_function()
        print("❌ 재시도가 무한히 반복됨 (버그)")
    except NetworkError as e:
        assert attempt_count == 3  # 최대 3회 시도
        print(f"✅ 최대 재시도 횟수 도달: {attempt_count}회 시도 후 실패")

    print()


async def main():
    """전체 에러 처리 테스트 실행."""
    print("\n")
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 18 + "에러 처리 테스트" + " " * 24 + "║")
    print("╚" + "═" * 58 + "╝")
    print()

    # 1. 예외 클래스 테스트
    await test_exception_types()

    # 2. 에러 분류 테스트
    test_error_classification()

    # 3. 재시도 데코레이터 테스트
    await test_retry_decorator()

    # 4. 재시도 한도 초과 테스트
    await test_retry_exhaustion()

    # 최종 결과
    print("=" * 60)
    print("최종 결과")
    print("=" * 60)
    print()
    print("🎉 모든 에러 처리 테스트 통과!")
    print()


if __name__ == "__main__":
    asyncio.run(main())
