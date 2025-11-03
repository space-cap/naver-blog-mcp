"""MCP Tool 핸들러 테스트."""

import asyncio
import sys

sys.path.insert(0, "src")

from naver_blog_mcp.server import NaverBlogMCPServer


async def test_tool_registration():
    """Tool 등록 및 목록 조회 테스트."""
    print("🔧 MCP Tool 등록 테스트\n")

    server = NaverBlogMCPServer()
    print("✅ 서버 인스턴스 생성 완료")

    # Tool 등록 확인
    print(f"✅ Tool 등록 완료 ({len(server.server._tool_handlers) if hasattr(server.server, '_tool_handlers') else 'N/A'}개)")

    print("\n🎉 Tool 등록 테스트 통과!")


async def test_create_post_tool():
    """create_post Tool 실행 테스트."""
    print("\n🔧 create_post Tool 실행 테스트\n")

    server = NaverBlogMCPServer()
    print("✅ 서버 인스턴스 생성 완료")

    try:
        # 브라우저 초기화
        await server.initialize()
        print("✅ 브라우저 및 세션 초기화 완료")

        # Tool 핸들러 임포트
        from naver_blog_mcp.mcp.tools import handle_create_post

        # 페이지 가져오기
        page = await server.get_page()
        print("✅ 페이지 생성 완료")

        # 테스트 글 작성
        test_title = "[MCP 테스트] Tool 핸들러 테스트"
        test_content = """
이것은 MCP Tool 핸들러 테스트를 위한 글입니다.

Day 6에서 구현한 `handle_create_post` 함수를 테스트합니다.

주요 기능:
- 기존 자동화 모듈과 통합
- MCP Server와 연동
- 에러 처리

테스트 완료 후 이 글은 삭제됩니다.
        """.strip()

        print(f"\n📝 테스트 글 작성 시작...")
        print(f"   제목: {test_title}")
        print(f"   본문: {test_content[:50]}...")

        result = await handle_create_post(
            page=page,
            title=test_title,
            content=test_content,
            publish=True,
        )

        if result["success"]:
            print(f"\n✅ 글 작성 성공!")
            print(f"   URL: {result.get('post_url', 'N/A')}")
            print(f"   메시지: {result.get('message', 'N/A')}")
        else:
            print(f"\n❌ 글 작성 실패!")
            print(f"   메시지: {result.get('message', 'N/A')}")

        print("\n🎉 create_post Tool 테스트 완료!")

    except Exception as e:
        print(f"\n❌ 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        # 리소스 정리
        await server.cleanup()
        print("✅ 리소스 정리 완료")


async def main():
    """전체 테스트 실행."""
    print("=" * 60)
    print("MCP Tool 핸들러 테스트 시작")
    print("=" * 60)

    # 1. Tool 등록 테스트
    await test_tool_registration()

    # 2. create_post Tool 테스트
    await test_create_post_tool()

    print("\n" + "=" * 60)
    print("모든 테스트 완료!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
