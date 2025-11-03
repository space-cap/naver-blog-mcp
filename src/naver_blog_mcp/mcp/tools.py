"""MCP Tool 정의.

이 모듈은 Claude가 호출할 수 있는 네이버 블로그 관련 Tool들을 정의합니다.
"""

from typing import Optional

# Tool 정의는 Day 6에서 구현할 예정입니다.
# 여기서는 구조만 준비합니다.

TOOLS_METADATA = {
    "naver_blog_create_post": {
        "name": "naver_blog_create_post",
        "description": "네이버 블로그에 새 글을 작성합니다.",
        "input_schema": {
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
        "input_schema": {
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
        "input_schema": {
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
