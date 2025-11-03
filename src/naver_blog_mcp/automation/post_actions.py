"""네이버 블로그 글쓰기 자동화."""

import asyncio
from typing import Optional, Dict, Any
from pathlib import Path

from playwright.async_api import Page, TimeoutError as PlaywrightTimeout

from .selectors import (
    POST_WRITE_TITLE,
    POST_WRITE_CONTENT_FRAME,
    POST_WRITE_CONTENT_BODY,
    POST_WRITE_PUBLISH_BTN,
    POST_WRITE_CATEGORY_BTN,
    POST_WRITE_TAG_INPUT,
)


class NaverBlogPostError(Exception):
    """네이버 블로그 글쓰기 관련 에러."""

    pass


async def navigate_to_post_write_page(
    page: Page, blog_id: Optional[str] = None, timeout: int = 30000
) -> None:
    """
    네이버 블로그 글쓰기 페이지로 이동합니다.

    Args:
        page: Playwright Page 객체
        blog_id: 블로그 ID (옵션, 없으면 자동으로 현재 로그인된 블로그 사용)
        timeout: 페이지 로딩 대기 시간 (ms)

    Raises:
        NaverBlogPostError: 페이지 이동 실패 시
    """
    try:
        if blog_id:
            # 특정 블로그의 글쓰기 페이지로 이동
            url = f"https://blog.naver.com/{blog_id}/postwrite"
        else:
            # 블로그 메인에서 글쓰기 버튼 클릭 방식
            url = "https://blog.naver.com/postwrite"

        await page.goto(url, wait_until="networkidle", timeout=timeout)
        await asyncio.sleep(2)  # 에디터 로딩 대기

        # 글쓰기 페이지인지 확인 (제목 입력란 존재 여부)
        title_input_exists = False
        if isinstance(POST_WRITE_TITLE, list):
            for selector in POST_WRITE_TITLE:
                count = await page.locator(selector).count()
                if count > 0:
                    title_input_exists = True
                    break
        else:
            count = await page.locator(POST_WRITE_TITLE).count()
            title_input_exists = count > 0

        if not title_input_exists:
            raise NaverBlogPostError("글쓰기 페이지 로딩에 실패했습니다.")

        print(f"✅ 글쓰기 페이지로 이동: {url}")

    except PlaywrightTimeout as e:
        raise NaverBlogPostError(f"글쓰기 페이지 이동 시간 초과: {str(e)}")
    except Exception as e:
        raise NaverBlogPostError(f"글쓰기 페이지 이동 중 오류: {str(e)}")


async def fill_post_title(page: Page, title: str) -> None:
    """
    블로그 글 제목을 입력합니다.

    Args:
        page: Playwright Page 객체
        title: 글 제목

    Raises:
        NaverBlogPostError: 제목 입력 실패 시
    """
    try:
        # 제목 입력란 찾기 (대체 셀렉터 시도)
        title_filled = False
        if isinstance(POST_WRITE_TITLE, list):
            for selector in POST_WRITE_TITLE:
                try:
                    await page.fill(selector, title, timeout=5000)
                    title_filled = True
                    print(f"✅ 제목 입력 완료: {title}")
                    break
                except PlaywrightTimeout:
                    continue
        else:
            await page.fill(POST_WRITE_TITLE, title)
            title_filled = True
            print(f"✅ 제목 입력 완료: {title}")

        if not title_filled:
            raise NaverBlogPostError("제목 입력란을 찾을 수 없습니다.")

        await asyncio.sleep(0.5)

    except Exception as e:
        raise NaverBlogPostError(f"제목 입력 중 오류: {str(e)}")


async def fill_post_content(page: Page, content: str, use_html: bool = False) -> None:
    """
    블로그 글 본문을 입력합니다.
    네이버 블로그의 스마트에디터는 iframe 내부에 있으므로 iframe 처리가 필요합니다.

    Args:
        page: Playwright Page 객체
        content: 글 본문 내용
        use_html: HTML 모드로 입력할지 여부 (기본: False, 텍스트 모드)

    Raises:
        NaverBlogPostError: 본문 입력 실패 시
    """
    try:
        # 1. iframe 찾기 (대체 셀렉터 시도)
        iframe_found = None
        if isinstance(POST_WRITE_CONTENT_FRAME, list):
            for selector in POST_WRITE_CONTENT_FRAME:
                try:
                    frame_element = await page.wait_for_selector(
                        selector, timeout=10000
                    )
                    iframe_found = await frame_element.content_frame()
                    if iframe_found:
                        print(f"✅ iframe 발견: {selector}")
                        break
                except PlaywrightTimeout:
                    continue
        else:
            frame_element = await page.wait_for_selector(
                POST_WRITE_CONTENT_FRAME, timeout=10000
            )
            iframe_found = await frame_element.content_frame()

        if not iframe_found:
            raise NaverBlogPostError("스마트에디터 iframe을 찾을 수 없습니다.")

        # 2. iframe 내부의 contenteditable 영역 찾기
        content_body = None
        if isinstance(POST_WRITE_CONTENT_BODY, list):
            for selector in POST_WRITE_CONTENT_BODY:
                try:
                    content_body = await iframe_found.wait_for_selector(
                        selector, timeout=5000
                    )
                    if content_body:
                        print(f"✅ 본문 영역 발견: {selector}")
                        break
                except PlaywrightTimeout:
                    continue
        else:
            content_body = await iframe_found.wait_for_selector(
                POST_WRITE_CONTENT_BODY, timeout=5000
            )

        if not content_body:
            raise NaverBlogPostError("본문 입력 영역을 찾을 수 없습니다.")

        # 3. 본문 입력
        if use_html:
            # HTML 모드: innerHTML로 직접 삽입
            await content_body.evaluate(f"el => el.innerHTML = `{content}`")
            print(f"✅ 본문 입력 완료 (HTML 모드)")
        else:
            # 텍스트 모드: type으로 자연스럽게 입력
            await content_body.click()
            await asyncio.sleep(0.5)
            await content_body.type(content, delay=10)  # 10ms 딜레이로 자연스러운 타이핑
            print(f"✅ 본문 입력 완료 (텍스트 모드)")

        await asyncio.sleep(1)

    except PlaywrightTimeout as e:
        raise NaverBlogPostError(f"본문 입력 시간 초과: {str(e)}")
    except Exception as e:
        raise NaverBlogPostError(f"본문 입력 중 오류: {str(e)}")


async def publish_post(
    page: Page, wait_for_completion: bool = True, timeout: int = 30000
) -> Dict[str, Any]:
    """
    블로그 글을 발행합니다.

    Args:
        page: Playwright Page 객체
        wait_for_completion: 발행 완료를 기다릴지 여부
        timeout: 발행 완료 대기 시간 (ms)

    Returns:
        발행 결과 딕셔너리
        {
            "success": bool,
            "message": str,
            "post_url": str (발행된 글 URL, 성공 시)
        }

    Raises:
        NaverBlogPostError: 발행 실패 시
    """
    try:
        # 1. 발행 버튼 찾기 (대체 셀렉터 시도)
        publish_clicked = False
        if isinstance(POST_WRITE_PUBLISH_BTN, list):
            for selector in POST_WRITE_PUBLISH_BTN:
                try:
                    await page.click(selector, timeout=5000)
                    publish_clicked = True
                    print(f"✅ 발행 버튼 클릭: {selector}")
                    break
                except PlaywrightTimeout:
                    continue
        else:
            await page.click(POST_WRITE_PUBLISH_BTN)
            publish_clicked = True
            print(f"✅ 발행 버튼 클릭")

        if not publish_clicked:
            raise NaverBlogPostError("발행 버튼을 찾을 수 없습니다.")

        # 2. 발행 완료 대기 (옵션)
        if wait_for_completion:
            try:
                # 발행 후 글 보기 페이지로 리다이렉트되는지 확인
                # URL 패턴: https://blog.naver.com/{blog_id}/{post_id}
                await page.wait_for_url("**/blog.naver.com/*/**", timeout=timeout)
                post_url = page.url

                # PostView 페이지인지 확인 (본문 영역이 있는지)
                # 글쓰기 페이지가 아닌 글 보기 페이지인지 체크
                if "postwrite" not in post_url and "PostView" not in post_url:
                    # URL이 {blog_id}/{post_id} 형태인지 확인
                    print(f"✅ 발행 완료: {post_url}")
                    return {
                        "success": True,
                        "message": "글이 성공적으로 발행되었습니다.",
                        "post_url": post_url,
                    }
                else:
                    raise NaverBlogPostError("발행 후 페이지 이동에 실패했습니다.")

            except PlaywrightTimeout:
                raise NaverBlogPostError("발행 완료 대기 시간 초과")
        else:
            return {
                "success": True,
                "message": "발행 요청을 전송했습니다.",
                "post_url": None,
            }

    except Exception as e:
        raise NaverBlogPostError(f"발행 중 오류: {str(e)}")


async def create_blog_post(
    page: Page,
    title: str,
    content: str,
    blog_id: Optional[str] = None,
    use_html: bool = False,
    wait_for_completion: bool = True,
) -> Dict[str, Any]:
    """
    네이버 블로그에 새 글을 작성하고 발행하는 전체 프로세스.

    Args:
        page: Playwright Page 객체 (로그인된 상태여야 함)
        title: 글 제목
        content: 글 본문
        blog_id: 블로그 ID (옵션)
        use_html: HTML 모드로 본문 입력할지 여부
        wait_for_completion: 발행 완료를 기다릴지 여부

    Returns:
        발행 결과 딕셔너리
        {
            "success": bool,
            "message": str,
            "post_url": str,
            "title": str,
        }

    Raises:
        NaverBlogPostError: 글 작성 실패 시
    """
    try:
        # 1. 글쓰기 페이지로 이동
        await navigate_to_post_write_page(page, blog_id)

        # 2. 제목 입력
        await fill_post_title(page, title)

        # 3. 본문 입력
        await fill_post_content(page, content, use_html)

        # 4. 발행
        result = await publish_post(page, wait_for_completion)

        result["title"] = title
        return result

    except NaverBlogPostError:
        raise
    except Exception as e:
        raise NaverBlogPostError(f"글 작성 중 오류: {str(e)}")
