"""MCP 서버 기본 테스트."""

import asyncio
import sys

sys.path.insert(0, "src")

from naver_blog_mcp.server import NaverBlogMCPServer


async def test_server_initialization():
    """서버 초기화 테스트."""
    print("🔧 MCP 서버 초기화 테스트\n")

    server = NaverBlogMCPServer()
    print("✅ 서버 인스턴스 생성 완료")

    try:
        # 브라우저 초기화
        await server.initialize()
        print("✅ 브라우저 및 세션 초기화 완료")

        # 페이지 가져오기 테스트
        page = await server.get_page()
        print(f"✅ 페이지 생성 완료: {page}")

        # 간단한 네비게이션 테스트
        await page.goto("https://blog.naver.com")
        print(f"✅ 네이버 블로그 접속 완료: {page.url}")

        print("\n🎉 모든 테스트 통과!")

    except Exception as e:
        print(f"\n❌ 테스트 실패: {e}")
        raise
    finally:
        # 리소스 정리
        await server.cleanup()
        print("✅ 리소스 정리 완료")


if __name__ == "__main__":
    asyncio.run(test_server_initialization())
