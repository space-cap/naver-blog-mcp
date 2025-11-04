"""네이버 블로그 글쓰기 자동화."""

import asyncio
import logging
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


logger = logging.getLogger(__name__)


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
        # 방법 1: blog_id가 주어진 경우
        if blog_id:
            url = f"https://blog.naver.com/{blog_id}/postwrite"
        else:
            # 방법 2: 블로그 메인에서 글쓰기 버튼 찾아서 클릭
            # 먼저 블로그 메인으로 이동
            await page.goto("https://blog.naver.com", wait_until="load", timeout=timeout)
            await asyncio.sleep(2)

            # 글쓰기 버튼 찾기 (여러 셀렉터 시도)
            write_btn_selectors = [
                "a[href*='postwrite']",
                "a:has-text('글쓰기')",
                "button:has-text('글쓰기')",
            ]

            write_btn_found = False
            for selector in write_btn_selectors:
                count = await page.locator(selector).count()
                if count > 0:
                    # href 가져오기
                    element = page.locator(selector).first
                    href = await element.get_attribute("href")
                    if href:
                        # 절대 URL로 변환
                        if href.startswith("/"):
                            url = f"https://blog.naver.com{href}"
                        elif href.startswith("http"):
                            url = href
                        else:
                            url = f"https://blog.naver.com/{href}"
                        write_btn_found = True
                        print(f"   글쓰기 버튼 발견: {url}")
                        break

            if not write_btn_found:
                # 기본 URL 사용
                url = "https://blog.naver.com/postwrite"
                print(f"   글쓰기 버튼을 찾지 못했습니다. 기본 URL 사용: {url}")

        await page.goto(url, wait_until="load", timeout=timeout)
        await asyncio.sleep(3)  # 에디터 로딩 충분히 대기

        # 글쓰기 페이지인지 확인
        current_url = page.url
        print(f"   현재 URL: {current_url}")

        # URL에 postwrite, PostWriteForm, Redirect=Write가 포함되어 있으면 성공으로 간주
        if ("postwrite" in current_url.lower() or
            "PostWriteForm" in current_url or
            "Redirect=Write" in current_url):
            logger.info(f"글쓰기 페이지로 이동: {current_url}")
            return

        # 제목 입력란 확인 (추가 검증)
        title_input_exists = False
        if isinstance(POST_WRITE_TITLE, list):
            for selector in POST_WRITE_TITLE:
                count = await page.locator(selector).count()
                if count > 0:
                    title_input_exists = True
                    print(f"   제목 입력란 발견: {selector}")
                    break
        else:
            count = await page.locator(POST_WRITE_TITLE).count()
            title_input_exists = count > 0

        if title_input_exists:
            logger.info(f"글쓰기 페이지로 이동: {url}")
            return

        raise NaverBlogPostError(f"글쓰기 페이지 로딩에 실패했습니다. 현재 URL: {current_url}")

    except PlaywrightTimeout as e:
        raise NaverBlogPostError(f"글쓰기 페이지 이동 시간 초과: {str(e)}")
    except Exception as e:
        import traceback
        traceback.print_exc()
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

        # 방법 1: 일반적인 셀렉터 시도
        if isinstance(POST_WRITE_TITLE, list):
            for selector in POST_WRITE_TITLE:
                try:
                    element_count = await page.locator(selector).count()
                    if element_count > 0:
                        # contenteditable div는 fill 대신 type 사용
                        element = page.locator(selector).first

                        # contenteditable인지 확인
                        is_contenteditable = await element.get_attribute("contenteditable")

                        if is_contenteditable:
                            # contenteditable div: 클릭 후 타이핑
                            await element.click()
                            await asyncio.sleep(0.3)
                            await element.type(title, delay=50)
                        else:
                            # 일반 input: fill 사용
                            await element.fill(title)

                        title_filled = True
                        logger.info(f"제목 입력 완료: {title} (selector: {selector})")
                        break
                except Exception as e:
                    print(f"   셀렉터 {selector} 실패: {e}")
                    continue

        # 방법 2: 제목 영역을 직접 클릭 (좌표 기반)
        if not title_filled:
            try:
                # 제목 영역 대략적인 위치 클릭 (상단 중앙)
                await page.mouse.click(450, 250)
                await asyncio.sleep(0.5)
                await page.keyboard.type(title, delay=50)
                title_filled = True
                logger.info(f"제목 입력 완료 (클릭 방식): {title}")
            except Exception as e:
                print(f"   클릭 방식 실패: {e}")

        # 방법 3: Tab 키로 이동
        if not title_filled:
            try:
                # 페이지 최상단으로 포커스 이동 후 Tab으로 제목까지 이동
                await page.keyboard.press("Tab")
                await asyncio.sleep(0.3)
                await page.keyboard.type(title, delay=50)
                title_filled = True
                logger.info(f"제목 입력 완료 (Tab 방식): {title}")
            except Exception as e:
                print(f"   Tab 방식 실패: {e}")

        if not title_filled:
            raise NaverBlogPostError("제목 입력란을 찾을 수 없습니다.")

        await asyncio.sleep(0.5)

    except Exception as e:
        raise NaverBlogPostError(f"제목 입력 중 오류: {str(e)}")


async def fill_post_content(page: Page, content: str, use_html: bool = False) -> None:
    """
    블로그 글 본문을 입력합니다.
    스마트에디터 ONE은 iframe 없이 직접 contenteditable을 사용합니다.

    Args:
        page: Playwright Page 객체
        content: 글 본문 내용
        use_html: HTML 모드로 입력할지 여부 (기본: False, 텍스트 모드)

    Raises:
        NaverBlogPostError: 본문 입력 실패 시
    """
    try:
        # 팝업이 있으면 먼저 닫기
        try:
            popup_selectors = [
                "button:has-text('확인')",
                "button:has-text('닫기')",
                "button.se-popup-button-confirm",
                ".se-popup-button-confirm",
            ]
            for popup_selector in popup_selectors:
                popup_count = await page.locator(popup_selector).count()
                if popup_count > 0:
                    await page.click(popup_selector, timeout=2000)
                    print(f"   팝업 닫기: {popup_selector}")
                    await asyncio.sleep(0.5)
                    break
        except Exception as e:
            print(f"   팝업 확인 실패 (무시): {e}")

        content_filled = False

        # 방법 1: iframe이 있는 경우 (구형 스마트에디터)
        iframe_selectors = POST_WRITE_CONTENT_FRAME if isinstance(POST_WRITE_CONTENT_FRAME, list) else [POST_WRITE_CONTENT_FRAME]

        for iframe_selector in iframe_selectors:
            try:
                iframe_count = await page.locator(iframe_selector).count()
                if iframe_count > 0:
                    print(f"   iframe 발견: {iframe_selector}")
                    frame_element = await page.wait_for_selector(iframe_selector, timeout=5000)
                    iframe_found = await frame_element.content_frame()

                    if iframe_found:
                        # iframe 내부 팝업 닫기
                        try:
                            iframe_popup_selectors = [
                                "button:has-text('확인')",
                                "button:has-text('닫기')",
                                ".se-popup-button-confirm",
                            ]
                            for popup_sel in iframe_popup_selectors:
                                popup_count = await iframe_found.locator(popup_sel).count()
                                if popup_count > 0:
                                    await iframe_found.locator(popup_sel).click(timeout=2000)
                                    print(f"   iframe 내부 팝업 닫기: {popup_sel}")
                                    await asyncio.sleep(0.5)
                                    break
                        except Exception as e:
                            print(f"   iframe 팝업 닫기 실패 (무시): {e}")

                        # iframe 내부에서 contenteditable 찾기
                        body_selectors = POST_WRITE_CONTENT_BODY if isinstance(POST_WRITE_CONTENT_BODY, list) else [POST_WRITE_CONTENT_BODY]

                        for body_selector in body_selectors:
                            try:
                                content_body = await iframe_found.wait_for_selector(body_selector, timeout=3000)
                                if content_body:
                                    await content_body.click()
                                    await asyncio.sleep(0.5)
                                    await content_body.type(content, delay=10)
                                    content_filled = True
                                    logger.info(f"본문 입력 완료 (iframe 방식, selector: {body_selector})")
                                    break
                            except Exception as e:
                                print(f"   iframe 내부 셀렉터 {body_selector} 실패: {e}")
                                continue

                        if content_filled:
                            # iframe에서 메인 페이지로 포커스 전환
                            await page.evaluate("() => { window.focus(); }")
                            await asyncio.sleep(0.5)
                            break
            except:
                continue

        # 방법 2: iframe 없이 직접 contenteditable (스마트에디터 ONE)
        if not content_filled:
            print("   iframe 없음, 직접 contenteditable 찾기 시도")

            # 본문 영역 찾기 - 여러 방법 시도
            content_selectors = [
                "div[contenteditable='true']:not([data-placeholder='제목'])",  # 제목이 아닌 contenteditable
                "div[contenteditable='true'][role='textbox']",
                "div.se-component",  # 스마트에디터 컴포넌트
                "div:has-text('글감과 함께')",  # 플레이스홀더 텍스트로 찾기
            ]

            for selector in content_selectors:
                try:
                    element_count = await page.locator(selector).count()
                    if element_count > 0:
                        element = page.locator(selector).first
                        await element.click()
                        await asyncio.sleep(0.5)

                        # 기존 플레이스홀더 텍스트 제거
                        await page.keyboard.press("Control+A")
                        await asyncio.sleep(0.2)

                        # 본문 입력
                        await page.keyboard.type(content, delay=10)
                        content_filled = True
                        logger.info(f"본문 입력 완료 (직접 방식, selector: {selector})")
                        break
                except Exception as e:
                    print(f"   셀렉터 {selector} 실패: {e}")
                    continue

        if not content_filled:
            raise NaverBlogPostError("본문 입력 영역을 찾을 수 없습니다.")

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
        # 0. 메인 페이지로 포커스 전환 (iframe에서 나오기)
        # 명시적으로 메인 페이지로 전환
        await page.bring_to_front()
        await page.evaluate("() => { if (window.parent) { window.parent.focus(); } window.focus(); }")
        await asyncio.sleep(1)

        # 페이지가 실제로 로드되었는지 확인
        print(f"   현재 URL: {page.url}")
        print(f"   페이지 타이틀: {await page.title()}")

        # 페이지 내 모든 팝업/모달 닫기 (도움말 팝업 등)
        try:
            # 도움말 팝업 닫기
            popup_close_selectors = [
                "button.se-popup-button-cancel",  # 취소 버튼
                "button:has-text('닫기')",
                "button:has-text('확인')",
                "button.se-popup-close",
                ".se-popup-dim",  # 팝업 배경 클릭
            ]
            for close_sel in popup_close_selectors:
                popup_count = await page.locator(close_sel).count()
                if popup_count > 0:
                    try:
                        await page.locator(close_sel).first.click(timeout=2000)
                        print(f"   페이지 팝업 닫기: {close_sel}")
                        await asyncio.sleep(0.5)
                    except Exception:
                        pass
        except Exception:
            pass

        # 1. 발행 버튼 찾기 (대체 셀렉터 시도)
        publish_clicked = False

        # 추가 발행 버튼 셀렉터
        # 네이버 블로그는 하단 중앙에 "글쓰기" 버튼이 있음 (이것이 발행 버튼)
        publish_selectors = [
            "div.publish_area button:has-text('글쓰기')",  # 하단 중앙 글쓰기 버튼
            "button.publish_btn",
            "a.publish_btn:has-text('글쓰기')",
            "button:has-text('글쓰기'):visible",
            "a:has-text('글쓰기'):visible",
            "button:has-text('발행'):visible",
            "button.se-toolbar-group-button.se-toolbar-publish-button",
            "button:has-text('등록')",
            "button.publish",
            "button.btn_post",
            "a:has-text('발행')",
            "a.btn_submit",
            "button[type='submit']",
        ]

        # 기존 셀렉터와 병합
        if isinstance(POST_WRITE_PUBLISH_BTN, list):
            publish_selectors = POST_WRITE_PUBLISH_BTN + publish_selectors
        else:
            publish_selectors.insert(0, POST_WRITE_PUBLISH_BTN)

        # 1. 모든 iframe에서 발행 버튼 찾기
        all_frames = page.frames
        for idx, frame in enumerate(all_frames):
            try:
                # Frame 내부의 도움말 팝업 닫기
                help_popup_selectors = [
                    "button.se-help-close-btn",
                    "button:has-text('닫기')",
                    ".se-help-close",
                ]
                for help_sel in help_popup_selectors:
                    help_count = await frame.locator(help_sel).count()
                    if help_count > 0:
                        await frame.locator(help_sel).first.click(timeout=2000)
                        await asyncio.sleep(0.5)
                        break

                # 발행 버튼 찾기 (우선순위: 발행 > 글쓰기)
                search_texts = ["발행", "글쓰기"]
                for search_text in search_texts:
                    write_btn_count = await frame.locator(f"button:has-text('{search_text}'):visible").count()
                    if write_btn_count > 0:
                        element = frame.locator(f"button:has-text('{search_text}'):visible").first
                        await element.click(timeout=5000)
                        publish_clicked = True
                        logger.info(f"발행 버튼 클릭 성공 (Frame {idx})")
                        await asyncio.sleep(2)
                        break

                if publish_clicked:
                    break
            except Exception:
                continue

        if not publish_clicked:
            await page.screenshot(path="playwright-state/error_publish_btn.png")
            raise NaverBlogPostError("발행 버튼을 찾을 수 없습니다.")

        # 2. 발행 설정 대화상자에서 최종 "발행" 버튼 클릭
        if publish_clicked:
            try:
                await asyncio.sleep(1)  # 대화상자 로딩 대기

                # 대화상자 내 발행 버튼을 force=True로 클릭 시도
                final_publish_clicked = False
                for idx, frame in enumerate(page.frames):
                    try:
                        dialog_publish_selectors = [
                            ".layer_popup__i0QOY button[class*='confirm']:has-text('발행')",
                            ".layer_popup__i0QOY button:has-text('발행')",
                        ]

                        for selector in dialog_publish_selectors:
                            try:
                                btn_count = await frame.locator(selector).count()
                                if btn_count > 0:
                                    await frame.locator(selector).first.click(force=True, timeout=5000)
                                    final_publish_clicked = True
                                    await asyncio.sleep(2)
                                    break
                            except Exception:
                                continue

                        if final_publish_clicked:
                            break
                    except Exception:
                        continue

                # JavaScript로 대화상자 내 발행 버튼 클릭 (fallback)
                if not final_publish_clicked:
                    for frame in page.frames:
                        try:
                            result = await frame.evaluate("""
                                () => {
                                    const popup = document.querySelector('.layer_popup__i0QOY.is_show__TMSLq');
                                    if (!popup) return 'No popup';

                                    const buttons = popup.querySelectorAll('button');
                                    for (let btn of buttons) {
                                        if ((btn.textContent || '').trim() === '발행') {
                                            btn.click();
                                            return 'Clicked';
                                        }
                                    }
                                    return 'No button';
                                }
                            """)
                            if 'Clicked' in result:
                                await asyncio.sleep(3)
                                break
                        except Exception:
                            continue

            except Exception:
                pass

        # 3. 발행 완료 대기 (옵션)
        if wait_for_completion:
            try:
                # 발행 후 글 보기 페이지로 리다이렉트되는지 확인
                # URL 패턴: https://blog.naver.com/{blog_id}/{post_id}
                await page.wait_for_url("**/blog.naver.com/*/**", timeout=timeout)
                post_url = page.url

                # PostView 페이지인지 확인 (본문 영역이 있는지)
                # 글쓰기 페이지가 아닌 글 보기 페이지인지 체크
                if "postwrite" not in post_url.lower() and "redirect=write" not in post_url.lower():
                    # URL이 {blog_id}/{post_id} 형태인지 확인
                    logger.info(f"발행 완료: {post_url}")
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
