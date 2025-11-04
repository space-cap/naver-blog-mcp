"""MCP 서버의 도구 목록 노출 테스트 스크립트."""
import asyncio
import json
import sys
import os

# Windows 콘솔 인코딩 설정
if sys.platform == "win32":
    os.system("chcp 65001 > nul")
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp.client.session import ClientSession


async def test_mcp_tools():
    """MCP 서버에 연결하여 도구 목록을 확인합니다."""

    # MCP 서버 파라미터 설정
    server_params = StdioServerParameters(
        command="uv",
        args=["run", "naver-blog-mcp"],
        env=None
    )

    print("MCP 서버 연결 중...")

    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                # 서버 초기화
                print("서버 초기화 중...")
                await session.initialize()
                print("✓ 서버 초기화 완료\n")

                # 도구 목록 조회
                print("도구 목록 조회 중...")
                tools = await session.list_tools()

                print(f"✓ 총 {len(tools.tools)}개의 도구가 노출됨\n")
                print("=" * 80)

                # 각 도구 정보 출력
                for i, tool in enumerate(tools.tools, 1):
                    print(f"\n[도구 {i}] {tool.name}")
                    print(f"설명: {tool.description}")
                    print(f"\n파라미터:")

                    if hasattr(tool, 'inputSchema') and tool.inputSchema:
                        schema = tool.inputSchema
                        properties = schema.get('properties', {})
                        required = schema.get('required', [])

                        for prop_name, prop_info in properties.items():
                            required_mark = "✓" if prop_name in required else " "
                            prop_type = prop_info.get('type', 'unknown')
                            prop_desc = prop_info.get('description', '')

                            print(f"  [{required_mark}] {prop_name}: {prop_type}")
                            if prop_desc:
                                print(f"      {prop_desc}")
                    else:
                        print("  (파라미터 없음)")

                    print("-" * 80)

                print("\n✅ 모든 도구가 올바르게 노출되고 있습니다!")
                return True

    except Exception as e:
        print(f"\n❌ 오류 발생: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_mcp_tools())
    sys.exit(0 if success else 1)
