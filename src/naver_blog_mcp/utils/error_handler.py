"""Playwright 에러 핸들링 유틸리티."""

import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

from playwright.async_api import Page, Error as PlaywrightError, TimeoutError as PlaywrightTimeoutError

from .exceptions import (
    ElementNotFoundError,
    NavigationError,
    NetworkError,
    TimeoutError,
    UIChangedError,
)

logger = logging.getLogger(__name__)


async def handle_playwright_error(
    error: Exception,
    page: Page,
    context: str = "unknown",
    save_screenshot: bool = True,
) -> Exception:
    """
    Playwright 에러를 커스텀 에러로 변환하고 스크린샷을 저장합니다.

    Args:
        error: 원본 Playwright 에러
        page: Playwright Page 객체
        context: 에러 발생 컨텍스트 (예: "login", "post_write")
        save_screenshot: 스크린샷 저장 여부

    Returns:
        변환된 커스텀 예외
    """
    error_str = str(error)
    error_type = type(error).__name__

    logger.error(f"Playwright error in {context}: {error_type} - {error_str}")

    # 스크린샷 저장
    screenshot_path = None
    if save_screenshot:
        try:
            screenshot_path = await save_error_screenshot(page, context, error_type)
            logger.info(f"Screenshot saved: {screenshot_path}")
        except Exception as e:
            logger.warning(f"Failed to save screenshot: {e}")

    # 에러 타입별 변환
    if isinstance(error, PlaywrightTimeoutError):
        # Timeout 에러
        return TimeoutError(
            f"Timeout in {context}: {error_str}",
            details={
                "context": context,
                "screenshot": screenshot_path,
                "original_error": error_str,
            }
        )
    elif "locator" in error_str.lower() or "selector" in error_str.lower():
        # 셀렉터 에러
        return ElementNotFoundError(
            f"Element not found in {context}: {error_str}",
            details={
                "context": context,
                "screenshot": screenshot_path,
                "original_error": error_str,
            }
        )
    elif "navigation" in error_str.lower() or "goto" in error_str.lower():
        # 네비게이션 에러
        return NavigationError(
            f"Navigation failed in {context}: {error_str}",
            details={
                "context": context,
                "screenshot": screenshot_path,
                "original_error": error_str,
            }
        )
    elif "net::" in error_str.lower() or "network" in error_str.lower():
        # 네트워크 에러
        return NetworkError(
            f"Network error in {context}: {error_str}",
            details={
                "context": context,
                "screenshot": screenshot_path,
                "original_error": error_str,
            }
        )
    else:
        # 기타 에러
        from .exceptions import NaverBlogError
        return NaverBlogError(
            f"Unexpected error in {context}: {error_str}",
            details={
                "context": context,
                "error_type": error_type,
                "screenshot": screenshot_path,
                "original_error": error_str,
            }
        )


async def save_error_screenshot(
    page: Page,
    context: str,
    error_type: str,
) -> str:
    """
    에러 발생 시 스크린샷을 저장합니다.

    Args:
        page: Playwright Page 객체
        context: 에러 발생 컨텍스트
        error_type: 에러 타입

    Returns:
        저장된 스크린샷 경로
    """
    # 스크린샷 디렉토리 생성
    screenshot_dir = Path("playwright-state/screenshots")
    screenshot_dir.mkdir(parents=True, exist_ok=True)

    # 파일명 생성
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"error_{context}_{error_type}_{timestamp}.png"
    filepath = screenshot_dir / filename

    # 스크린샷 저장
    await page.screenshot(path=str(filepath), full_page=True)

    return str(filepath)


async def save_page_html(
    page: Page,
    context: str,
) -> str:
    """
    디버깅을 위해 현재 페이지의 HTML을 저장합니다.

    Args:
        page: Playwright Page 객체
        context: 저장 컨텍스트

    Returns:
        저장된 HTML 파일 경로
    """
    # HTML 디렉토리 생성
    html_dir = Path("playwright-state/html")
    html_dir.mkdir(parents=True, exist_ok=True)

    # 파일명 생성
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"page_{context}_{timestamp}.html"
    filepath = html_dir / filename

    # HTML 저장
    content = await page.content()
    filepath.write_text(content, encoding="utf-8")

    return str(filepath)


def is_retryable_error(error: Exception) -> bool:
    """
    에러가 재시도 가능한지 판단합니다.

    Args:
        error: 발생한 에러

    Returns:
        재시도 가능 여부
    """
    # 재시도 가능한 에러 타입
    retryable_types = (
        NetworkError,
        TimeoutError,
        NavigationError,
    )

    if isinstance(error, retryable_types):
        return True

    # Playwright 기본 에러 체크
    if isinstance(error, PlaywrightTimeoutError):
        return True

    error_str = str(error).lower()
    retryable_keywords = [
        "timeout",
        "network",
        "net::",
        "connection",
        "socket",
    ]

    return any(keyword in error_str for keyword in retryable_keywords)


def should_use_alternative_selector(error: Exception) -> bool:
    """
    대체 셀렉터를 사용해야 하는지 판단합니다.

    Args:
        error: 발생한 에러

    Returns:
        대체 셀렉터 사용 여부
    """
    if isinstance(error, (ElementNotFoundError, UIChangedError)):
        return True

    error_str = str(error).lower()
    selector_keywords = [
        "locator",
        "selector",
        "element",
        "not found",
        "no node found",
    ]

    return any(keyword in error_str for keyword in selector_keywords)
