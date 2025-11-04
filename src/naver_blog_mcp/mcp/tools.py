"""MCP Tool 정의.

이 모듈은 Claude가 호출할 수 있는 네이버 블로그 관련 Tool들을 정의합니다.
"""

import logging
from typing import Optional, Dict, Any

from playwright.async_api import Page

from ..automation.post_actions import create_blog_post, NaverBlogPostError
from ..automation.image_upload import upload_images
from ..automation.category_actions import get_categories
from ..utils.retry import retry_on_error
from ..utils.error_handler import handle_playwright_error
from ..utils.exceptions import NaverBlogError, UploadError

logger = logging.getLogger(__name__)

TOOLS_METADATA = {
    "naver_blog_create_post": {
        "name": "naver_blog_create_post",
        "description": "네이버 블로그에 새 글을 작성합니다. 이미지 첨부도 지원합니다.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "글 제목",
                },
                "content": {
                    "type": "string",
                    "description": "글 본문 내용",
                },
                "category": {
                    "type": "string",
                    "description": "카테고리 이름 (선택)",
                },
                "tags": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "태그 목록 (선택)",
                },
                "images": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "첨부할 이미지 파일 경로 목록 (선택). 본문 작성 전에 이미지를 먼저 업로드합니다.",
                },
                "publish": {
                    "type": "boolean",
                    "description": "즉시 발행 여부 (기본: true, false면 임시저장)",
                    "default": True,
                },
            },
            "required": ["title", "content"],
        },
    },
    "naver_blog_delete_post": {
        "name": "naver_blog_delete_post",
        "description": "네이버 블로그의 글을 삭제합니다.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "post_url": {
                    "type": "string",
                    "description": "삭제할 글의 URL",
                },
            },
            "required": ["post_url"],
        },
    },
    "naver_blog_list_categories": {
        "name": "naver_blog_list_categories",
        "description": "네이버 블로그의 카테고리 목록을 가져옵니다.",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
}


def get_tools_list() -> list[dict]:
    """등록된 Tool 목록을 반환합니다.

    Returns:
        Tool 메타데이터 리스트
    """
    return list(TOOLS_METADATA.values())


# ============================================================================
# Tool Handler Functions
# ============================================================================


@retry_on_error
async def handle_create_post(
    page: Page,
    title: str,
    content: str,
    category: Optional[str] = None,
    tags: Optional[list[str]] = None,
    images: Optional[list[str]] = None,
    publish: bool = True,
) -> Dict[str, Any]:
    """네이버 블로그에 새 글을 작성합니다.

    Args:
        page: Playwright Page 객체 (로그인된 상태)
        title: 글 제목
        content: 글 본문 내용
        category: 카테고리 이름 (선택)
        tags: 태그 목록 (선택)
        images: 첨부할 이미지 파일 경로 목록 (선택)
        publish: 즉시 발행 여부 (기본: True, False면 임시저장)

    Returns:
        작업 결과 딕셔너리
        {
            "success": bool,
            "message": str,
            "post_url": str (발행 시),
            "title": str,
            "images_uploaded": int (업로드된 이미지 수)
        }

    Raises:
        NaverBlogPostError: 글 작성 실패 시
        UploadError: 이미지 업로드 실패 시
    """
    try:
        logger.info(f"글 작성 시작: {title}")
        images_uploaded = 0

        # 1. 이미지 업로드 (본문 작성 전)
        if images:
            logger.info(f"이미지 업로드 시작: {len(images)}개")
            try:
                upload_result = await upload_images(page, images)
                images_uploaded = len(upload_result.get("uploaded", []))

                if upload_result.get("failed"):
                    logger.warning(f"일부 이미지 업로드 실패: {upload_result['failed']}")

                logger.info(f"이미지 업로드 완료: {images_uploaded}/{len(images)}개")

            except UploadError as e:
                logger.error(f"이미지 업로드 실패: {e}")
                return {
                    "success": False,
                    "message": f"이미지 업로드 실패: {str(e)}",
                    "post_url": None,
                    "title": title,
                    "images_uploaded": 0,
                }

        # 2. 본문 작성
        result = await create_blog_post(
            page=page,
            title=title,
            content=content,
            blog_id=None,  # 현재 로그인된 블로그 사용
            use_html=False,
            wait_for_completion=publish,
        )

        # 결과에 이미지 정보 추가
        result["images_uploaded"] = images_uploaded

        logger.info(f"글 작성 완료: {result.get('post_url', 'N/A')} (이미지 {images_uploaded}개)")
        return result

    except NaverBlogPostError as e:
        logger.error(f"글 작성 실패: {e}")
        return {
            "success": False,
            "message": f"글 작성 중 오류가 발생했습니다: {str(e)}",
            "post_url": None,
            "title": title,
            "images_uploaded": images_uploaded,
        }
    except Exception as e:
        # Playwright 에러를 커스텀 에러로 변환
        custom_error = await handle_playwright_error(e, page, "create_post")
        logger.error(f"예상치 못한 오류: {custom_error}", exc_info=True)

        # 재시도 가능한 에러면 다시 발생시켜서 tenacity가 재시도하도록
        if isinstance(custom_error, NaverBlogError):
            raise custom_error

        return {
            "success": False,
            "message": f"예상치 못한 오류: {str(custom_error)}",
            "post_url": None,
            "title": title,
        }


async def handle_delete_post(page: Page, post_url: str) -> Dict[str, Any]:
    """네이버 블로그의 글을 삭제합니다.

    Args:
        page: Playwright Page 객체 (로그인된 상태)
        post_url: 삭제할 글의 URL

    Returns:
        작업 결과 딕셔너리
        {
            "success": bool,
            "message": str,
            "post_url": str
        }
    """
    # TODO: Day 6에서 구현 예정
    logger.warning("handle_delete_post: 아직 구현되지 않았습니다.")
    return {
        "success": False,
        "message": "글 삭제 기능은 아직 구현되지 않았습니다.",
        "post_url": post_url,
    }


async def handle_list_categories(page: Page) -> Dict[str, Any]:
    """네이버 블로그의 카테고리 목록을 가져옵니다.

    Args:
        page: Playwright Page 객체 (로그인된 상태)

    Returns:
        작업 결과 딕셔너리
        {
            "success": bool,
            "message": str,
            "categories": [
                {
                    "name": str,
                    "url": str,
                    "categoryNo": str
                },
                ...
            ]
        }
    """
    logger.info("카테고리 목록 조회 시작")

    try:
        result = await get_categories(page)

        if result["success"]:
            logger.info(f"카테고리 조회 완료: {len(result['categories'])}개")
        else:
            logger.error(f"카테고리 조회 실패: {result['message']}")

        return result

    except Exception as e:
        logger.error(f"카테고리 조회 중 예외 발생: {e}", exc_info=True)
        return {
            "success": False,
            "message": f"카테고리 조회 실패: {str(e)}",
            "categories": []
        }
