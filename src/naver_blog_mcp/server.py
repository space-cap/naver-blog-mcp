"""네이버 블로그 MCP 서버.

이 모듈은 Claude가 네이버 블로그와 상호작용할 수 있도록
MCP (Model Context Protocol) 서버를 제공합니다.
"""

# Windows 콘솔 인코딩 설정 (가장 먼저 실행)
import sys
if sys.platform == "win32":
    # stdout, stderr을 UTF-8로 강제 설정
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8')

import asyncio
import logging
import os
from typing import Optional

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool
from playwright.async_api import async_playwright, Browser, BrowserContext, Page

from .config import get_browser_config, config
from .services.session_manager import SessionManager
from .mcp.tools import (
    TOOLS_METADATA,
    handle_create_post,
    # handle_delete_post,  # 비활성화
    handle_list_categories,
)
from .utils.trace_manager import trace_manager

# 로깅 설정 (UTF-8 인코딩 명시)
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stderr)
    ]
)
# 참고: Claude Desktop이 로그를 파일로 리다이렉트할 때 UTF-8로 저장됩니다.
# sys.stderr이 이미 UTF-8로 설정되어 있으므로 (7-13줄) 로그도 UTF-8로 출력됩니다.

logger = logging.getLogger(__name__)


class NaverBlogMCPServer:
    """네이버 블로그 MCP 서버 클래스."""

    def __init__(self):
        """서버 초기화."""
        self.server = Server("naver-blog")
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None

        # 설정 검증
        config.validate()

        # 세션 관리자 초기화
        self.session_manager = SessionManager(
            user_id=config.NAVER_BLOG_ID,
            password=config.NAVER_BLOG_PASSWORD
        )

        # Tool 등록
        self._register_tools()

    def _register_tools(self):
        """MCP Tool들을 등록합니다."""
        logger.info("Registering MCP tools...")

        # naver_blog_create_post Tool 등록
        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict) -> list[dict]:
            """Tool 호출 핸들러."""
            logger.info(f"Tool called: {name} with arguments: {arguments}")

            try:
                # Trace 시작
                if self.context:
                    await trace_manager.start_trace(self.context, name=name)

                # 페이지 가져오기
                page = await self.get_page()

                # Tool별 핸들러 호출
                if name == "naver_blog_create_post":
                    result = await handle_create_post(
                        page=page,
                        title=arguments["title"],
                        content=arguments["content"],
                        category=arguments.get("category"),
                        tags=arguments.get("tags"),
                        images=arguments.get("images"),
                        publish=arguments.get("publish", True),
                    )
                # elif name == "naver_blog_delete_post":
                #     result = await handle_delete_post(
                #         page=page, post_url=arguments["post_url"]
                #     )
                elif name == "naver_blog_list_categories":
                    result = await handle_list_categories(page=page)
                else:
                    return [
                        {
                            "type": "text",
                            "text": f"알 수 없는 Tool: {name}",
                        }
                    ]

                # Trace 저장 (성공)
                if self.context:
                    await trace_manager.stop_trace(self.context, success=True)

                # 결과를 MCP 형식으로 변환
                import json

                return [
                    {
                        "type": "text",
                        "text": json.dumps(result, ensure_ascii=False, indent=2),
                    }
                ]

            except Exception as e:
                error_msg = str(e)
                logger.error(f"Tool execution error: {e}", exc_info=True)

                # 세션 만료 감지 및 자동 재로그인
                if "세션이 만료" in error_msg or "로그인 페이지로 리다이렉트" in error_msg:
                    logger.warning("세션 만료 감지. 자동 재로그인을 시도합니다...")
                    try:
                        # 기존 컨텍스트 닫기
                        if self.context:
                            await self.context.close()

                        # 세션 파일 삭제
                        import os
                        session_path = "playwright-state/auth.json"
                        if os.path.exists(session_path):
                            os.remove(session_path)
                            logger.info(f"세션 파일 삭제: {session_path}")

                        # 새 세션 생성 (자동 로그인)
                        self.context = await self.session_manager.get_or_create_session(self.browser)
                        logger.info("재로그인 완료. Tool을 다시 실행해주세요.")

                        return [
                            {
                                "type": "text",
                                "text": "세션이 만료되어 자동으로 재로그인했습니다. 요청을 다시 시도해주세요.",
                            }
                        ]
                    except Exception as re_login_error:
                        logger.error(f"재로그인 실패: {re_login_error}")
                        return [
                            {
                                "type": "text",
                                "text": f"재로그인 실패: {str(re_login_error)}. MCP 서버를 재시작해주세요.",
                            }
                        ]

                # Trace 저장 (실패)
                if self.context:
                    await trace_manager.stop_trace(self.context, success=False)

                return [
                    {
                        "type": "text",
                        "text": f"오류 발생: {error_msg}",
                    }
                ]

        # list_tools 핸들러 등록
        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            """사용 가능한 Tool 목록을 반환합니다."""
            # dict를 Tool 객체로 변환
            return [
                Tool(
                    name=tool_data["name"],
                    description=tool_data["description"],
                    inputSchema=tool_data["inputSchema"]
                )
                for tool_data in TOOLS_METADATA.values()
            ]

        logger.info(f"Registered {len(TOOLS_METADATA)} tools")

    async def initialize(self):
        """브라우저 및 세션 초기화."""
        logger.info("Initializing Naver Blog MCP Server...")

        # Playwright 시작
        self.playwright = await async_playwright().start()

        # 브라우저 설정 가져오기
        browser_config = get_browser_config()

        # 브라우저 실행
        self.browser = await self.playwright.chromium.launch(**browser_config)
        logger.info(f"Browser launched (headless={browser_config.get('headless', True)})")

        # 세션 복원 또는 새 컨텍스트 생성
        self.context = await self.session_manager.get_or_create_session(self.browser)
        logger.info("Browser context initialized")

    async def cleanup(self):
        """리소스 정리."""
        logger.info("Cleaning up resources...")

        if self.context:
            await self.context.close()
            logger.info("Browser context closed")

        if self.browser:
            await self.browser.close()
            logger.info("Browser closed")

        if self.playwright:
            await self.playwright.stop()
            logger.info("Playwright stopped")

    async def get_page(self) -> Page:
        """새 페이지를 생성하거나 기존 페이지를 반환합니다.

        Returns:
            Playwright Page 객체

        Raises:
            RuntimeError: 브라우저 컨텍스트가 초기화되지 않은 경우
        """
        if not self.context:
            raise RuntimeError("Browser context not initialized. Call initialize() first.")

        # 기존 페이지가 있으면 재사용, 없으면 새로 생성
        pages = self.context.pages
        if pages:
            return pages[0]
        else:
            return await self.context.new_page()

    async def run(self):
        """MCP 서버 실행."""
        try:
            # 브라우저 초기화
            await self.initialize()

            # stdio를 통해 MCP 서버 실행
            async with stdio_server() as (read_stream, write_stream):
                logger.info("MCP Server started successfully")
                await self.server.run(
                    read_stream,
                    write_stream,
                    self.server.create_initialization_options()
                )
        except Exception as e:
            logger.error(f"Server error: {e}", exc_info=True)
            raise
        finally:
            # 리소스 정리
            await self.cleanup()


async def async_main():
    """비동기 서버 엔트리포인트."""
    server = NaverBlogMCPServer()
    await server.run()


def main():
    """동기 서버 엔트리포인트 (CLI 진입점)."""
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
