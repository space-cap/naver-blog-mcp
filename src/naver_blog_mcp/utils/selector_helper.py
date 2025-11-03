"""셀렉터 헬퍼 유틸리티."""

import logging
from typing import Optional, Union, List

from playwright.async_api import Page, Locator, TimeoutError as PlaywrightTimeoutError

from .exceptions import ElementNotFoundError

logger = logging.getLogger(__name__)


async def find_element_with_alternatives(
    page: Page,
    selectors: Union[str, List[str]],
    timeout: int = 5000,
    context: str = "unknown",
) -> Optional[Locator]:
    """
    여러 대체 셀렉터를 시도하여 요소를 찾습니다.

    Args:
        page: Playwright Page 객체
        selectors: 셀렉터 문자열 또는 대체 셀렉터 리스트
        timeout: 각 셀렉터의 타임아웃 (ms)
        context: 컨텍스트 (로깅용)

    Returns:
        찾은 Locator 또는 None

    Raises:
        ElementNotFoundError: 모든 셀렉터가 실패한 경우
    """
    # 단일 셀렉터를 리스트로 변환
    if isinstance(selectors, str):
        selectors = [selectors]

    for idx, selector in enumerate(selectors):
        try:
            logger.debug(f"Trying selector {idx + 1}/{len(selectors)} in {context}: {selector}")

            # 요소가 존재하는지 확인
            locator = page.locator(selector)
            count = await locator.count()

            if count > 0:
                logger.info(f"Found element with selector {idx + 1} in {context}: {selector}")
                return locator.first

        except PlaywrightTimeoutError:
            logger.debug(f"Selector {idx + 1} timed out in {context}: {selector}")
            continue
        except Exception as e:
            logger.warning(f"Selector {idx + 1} failed in {context}: {selector} - {e}")
            continue

    # 모든 셀렉터 실패
    raise ElementNotFoundError(
        f"Could not find element in {context} with any of {len(selectors)} selectors",
        details={
            "context": context,
            "selectors": selectors,
        }
    )


async def click_with_alternatives(
    page: Page,
    selectors: Union[str, List[str]],
    timeout: int = 5000,
    context: str = "unknown",
) -> bool:
    """
    대체 셀렉터를 시도하여 요소를 클릭합니다.

    Args:
        page: Playwright Page 객체
        selectors: 셀렉터 문자열 또는 대체 셀렉터 리스트
        timeout: 각 셀렉터의 타임아웃 (ms)
        context: 컨텍스트 (로깅용)

    Returns:
        클릭 성공 여부

    Raises:
        ElementNotFoundError: 모든 셀렉터가 실패한 경우
    """
    locator = await find_element_with_alternatives(page, selectors, timeout, context)
    await locator.click(timeout=timeout)
    logger.info(f"Clicked element in {context}")
    return True


async def fill_with_alternatives(
    page: Page,
    selectors: Union[str, List[str]],
    value: str,
    timeout: int = 5000,
    context: str = "unknown",
) -> bool:
    """
    대체 셀렉터를 시도하여 요소에 값을 입력합니다.

    Args:
        page: Playwright Page 객체
        selectors: 셀렉터 문자열 또는 대체 셀렉터 리스트
        value: 입력할 값
        timeout: 각 셀렉터의 타임아웃 (ms)
        context: 컨텍스트 (로깅용)

    Returns:
        입력 성공 여부

    Raises:
        ElementNotFoundError: 모든 셀렉터가 실패한 경우
    """
    locator = await find_element_with_alternatives(page, selectors, timeout, context)
    await locator.fill(value, timeout=timeout)
    logger.info(f"Filled element in {context}")
    return True


async def wait_for_any_selector(
    page: Page,
    selectors: Union[str, List[str]],
    timeout: int = 30000,
    state: str = "visible",
    context: str = "unknown",
) -> Optional[Locator]:
    """
    여러 셀렉터 중 하나가 나타날 때까지 대기합니다.

    Args:
        page: Playwright Page 객체
        selectors: 셀렉터 문자열 또는 대체 셀렉터 리스트
        timeout: 전체 타임아웃 (ms)
        state: 요소 상태 ("visible", "attached", "hidden")
        context: 컨텍스트 (로깅용)

    Returns:
        찾은 Locator 또는 None

    Raises:
        ElementNotFoundError: 모든 셀렉터가 타임아웃된 경우
    """
    # 단일 셀렉터를 리스트로 변환
    if isinstance(selectors, str):
        selectors = [selectors]

    import asyncio

    # 각 셀렉터에 대해 비동기로 대기
    tasks = []
    for selector in selectors:
        async def wait_for_selector(sel):
            try:
                locator = page.locator(sel)
                await locator.wait_for(state=state, timeout=timeout)
                return locator.first
            except:
                return None

        tasks.append(wait_for_selector(selector))

    # 첫 번째로 완료되는 것을 반환
    done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)

    # 나머지 취소
    for task in pending:
        task.cancel()

    # 결과 확인
    for task in done:
        result = task.result()
        if result:
            logger.info(f"Found element with one of the selectors in {context}")
            return result

    # 모든 셀렉터 실패
    raise ElementNotFoundError(
        f"Could not find any element in {context} with {len(selectors)} selectors",
        details={
            "context": context,
            "selectors": selectors,
        }
    )
