"""네이버 블로그 카테고리 목록 조회 기능 테스트."""
import asyncio
import sys
from pathlib import Path

# Windows 콘솔 인코딩 설정
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# 프로젝트 루트 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from playwright.async_api import async_playwright
from naver_blog_mcp.config import config
from naver_blog_mcp.services.session_manager import SessionManager
from naver_blog_mcp.mcp.tools import handle_list_categories


async def test_list_categories():
    """카테고리 목록 조회 기능을 테스트합니다."""

    print("=" * 80)
    print("네이버 블로그 카테고리 목록 조회 테스트")
    print("=" * 80)

    # 환경 변수 확인
    config.validate()

    async with async_playwright() as p:
        # 브라우저 실행
        browser = await p.chromium.launch(headless=False)

        # 세션 관리자
        session_manager = SessionManager(
            user_id=config.NAVER_BLOG_ID,
            password=config.NAVER_BLOG_PASSWORD
        )
        context = await session_manager.get_or_create_session(browser)
        page = await context.new_page()

        try:
            print("\n[테스트] 카테고리 목록 조회...")

            # handle_list_categories 함수 호출
            result = await handle_list_categories(page)

            # 결과 출력
            print(f"\n성공 여부: {result['success']}")
            print(f"메시지: {result['message']}")
            print(f"\n총 {len(result['categories'])}개의 카테고리:")
            print("-" * 80)

            if result['categories']:
                for idx, cat in enumerate(result['categories'], 1):
                    print(f"\n{idx}. {cat['name']}")
                    print(f"   URL: {cat['url']}")
                    print(f"   카테고리 번호: {cat['categoryNo']}")
            else:
                print("카테고리가 없습니다.")

            print("-" * 80)

            # 검증
            if result['success']:
                print("\n✅ 테스트 성공!")
                return True
            else:
                print(f"\n❌ 테스트 실패: {result['message']}")
                return False

        except Exception as e:
            print(f"\n❌ 테스트 중 예외 발생: {e}")
            import traceback
            traceback.print_exc()
            return False

        finally:
            await context.close()
            await browser.close()


if __name__ == "__main__":
    success = asyncio.run(test_list_categories())
    sys.exit(0 if success else 1)
