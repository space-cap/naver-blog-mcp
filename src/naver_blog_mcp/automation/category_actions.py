"""네이버 블로그 카테고리 관련 자동화 기능."""

import logging
import re
from typing import Dict, Any, List, Optional
from playwright.async_api import Page

from ..utils.exceptions import NaverBlogError
from ..utils.error_handler import handle_playwright_error

logger = logging.getLogger(__name__)


async def get_categories(
    page: Page,
    blog_id: Optional[str] = None
) -> Dict[str, Any]:
    """네이버 블로그의 카테고리 목록을 가져옵니다.

    Args:
        page: Playwright Page 객체
        blog_id: 블로그 아이디 (None이면 현재 로그인한 블로그)

    Returns:
        {
            "success": bool,
            "message": str,
            "categories": [
                {
                    "name": str,           # 카테고리명
                    "url": str,            # 카테고리 URL
                    "categoryNo": str,     # 카테고리 번호
                },
                ...
            ]
        }

    Raises:
        NaverBlogError: 카테고리 조회 실패 시
    """
    try:
        logger.info("카테고리 목록 조회 시작")

        # 1. 블로그 메인 페이지로 이동
        # blog_id가 없으면 현재 페이지의 URL에서 추출하거나 config에서 가져오기
        if not blog_id:
            # 현재 URL에서 blog_id 추출 시도
            current_url = page.url
            if "blog.naver.com" in current_url:
                # URL에서 blogId 파라미터 찾기
                match = re.search(r'blogId=([^&]+)', current_url)
                if match:
                    blog_id = match.group(1)
                else:
                    # URL 경로에서 blogId 추출 (예: /blogid/...)
                    match = re.search(r'blog\.naver\.com/([^/?]+)', current_url)
                    if match:
                        extracted_id = match.group(1)
                        # "PostList", "MyBlog" 등의 경로가 아닌 경우에만 blog_id로 사용
                        if extracted_id not in ["PostList", "MyBlog", "PostView"]:
                            blog_id = extracted_id

            # 여전히 blog_id가 없으면 config에서 가져오기
            if not blog_id:
                from ..config import config as app_config
                blog_id = app_config.NAVER_BLOG_ID
                logger.info(f"config에서 blog_id 가져옴: {blog_id}")

        blog_url = f"https://blog.naver.com/{blog_id}"
        await page.goto(blog_url, wait_until="networkidle")
        logger.info(f"블로그 페이지 접근: {blog_url}")

        # 2. iframe 접근
        try:
            iframe_element = await page.wait_for_selector(
                "iframe#mainFrame",
                timeout=10000
            )
            main_frame = await iframe_element.content_frame()
            logger.info("iframe#mainFrame 접근 성공")
        except Exception as e:
            logger.error(f"iframe 접근 실패: {e}")
            return {
                "success": False,
                "message": "블로그 페이지 구조를 찾을 수 없습니다",
                "categories": []
            }

        # 3. 카테고리 링크 찾기
        # PostList 링크는 카테고리 링크를 나타냄
        try:
            category_links = await main_frame.query_selector_all(
                "a[href*='PostList']"
            )
            logger.info(f"PostList 링크 {len(category_links)}개 발견")
        except Exception as e:
            logger.error(f"카테고리 링크 조회 실패: {e}")
            return {
                "success": False,
                "message": f"카테고리 조회 중 오류 발생: {str(e)}",
                "categories": []
            }

        # 4. 카테고리 정보 추출
        categories = []
        seen_names = set()  # 중복 제거용

        for link in category_links:
            try:
                text = await link.text_content()
                href = await link.get_attribute("href")

                if not text or not href:
                    continue

                name = text.strip()

                # 필터링 조건
                # 1. 텍스트가 있어야 함
                # 2. 너무 길지 않아야 함 (카테고리명은 짧음)
                # 3. 숫자만 있는 경우 제외 (페이지 번호)
                # 4. 특정 키워드 제외
                if not name or len(name) > 50:
                    continue

                if name.isdigit():
                    continue

                if name in ["블로그 홈", "전체보기"]:
                    continue

                # blog_id가 알려진 경우 블로그 이름 제외
                if blog_id and name == blog_id:
                    continue

                # 이미 추가한 카테고리명이면 건너뛰기
                if name in seen_names:
                    continue

                # URL에서 categoryNo 추출
                category_no = None
                if "categoryNo=" in href:
                    match = re.search(r'categoryNo=(\d+)', href)
                    if match:
                        category_no = match.group(1)

                # categoryNo가 있는 경우만 추가 (실제 카테고리)
                # categoryNo가 0인 "전체보기"는 제외
                if category_no and category_no != "0":
                    category_info = {
                        "name": name,
                        "url": href if href.startswith("http") else f"https://blog.naver.com{href}",
                        "categoryNo": category_no,
                    }
                    categories.append(category_info)
                    seen_names.add(name)
                    logger.debug(f"카테고리 추가: {name} (categoryNo={category_no})")

            except Exception as e:
                logger.warning(f"카테고리 정보 추출 중 오류: {e}")
                continue

        # 5. 결과 반환
        if categories:
            logger.info(f"카테고리 {len(categories)}개 조회 완료")
            return {
                "success": True,
                "message": f"{len(categories)}개의 카테고리를 찾았습니다",
                "categories": categories
            }
        else:
            logger.info("카테고리가 없습니다")
            return {
                "success": True,
                "message": "카테고리가 없습니다",
                "categories": []
            }

    except Exception as e:
        # Playwright 에러를 커스텀 에러로 변환
        custom_error = await handle_playwright_error(e, page, "get_categories")
        logger.error(f"카테고리 조회 실패: {custom_error}", exc_info=True)

        return {
            "success": False,
            "message": f"카테고리 조회 중 오류 발생: {str(custom_error)}",
            "categories": []
        }
