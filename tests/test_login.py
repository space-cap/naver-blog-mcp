"""네이버 로그인 테스트 스크립트.

사용법:
    # .env 파일 설정 후
    uv run python tests/test_login.py
"""

import asyncio
import os
from pathlib import Path

from dotenv import load_dotenv
from playwright.async_api import async_playwright

# 프로젝트 루트 경로에서 .env 로드
project_root = Path(__file__).parent.parent
load_dotenv(project_root / ".env")

# 임포트 경로 추가
import sys

sys.path.insert(0, str(project_root / "src"))

from naver_blog_mcp.automation.login import login_to_naver, verify_login_session
from naver_blog_mcp.services.session_manager import SessionManager


async def test_login_basic():
    """기본 로그인 테스트."""
    print("\n" + "=" * 50)
    print("🧪 테스트 1: 기본 로그인")
    print("=" * 50)

    user_id = os.getenv("NAVER_BLOG_ID")
    password = os.getenv("NAVER_BLOG_PASSWORD")
    headless = os.getenv("HEADLESS", "false").lower() == "true"

    if not user_id or not password:
        print("❌ .env 파일에 NAVER_BLOG_ID와 NAVER_BLOG_PASSWORD를 설정해주세요.")
        return

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=headless,
            args=[
                "--disable-blink-features=AutomationControlled",
            ],
        )

        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
        )

        page = await context.new_page()

        try:
            result = await login_to_naver(
                page=page,
                user_id=user_id,
                password=password,
                storage_state_path="playwright-state/test_auth.json",
                headless=headless,
            )

            print(f"\n✅ {result['message']}")
            print(f"   세션 저장 경로: {result['storage_state_path']}")

        except Exception as e:
            print(f"\n❌ 로그인 실패: {e}")
            # 에러 스크린샷 저장
            await page.screenshot(path="playwright-state/error_login.png")
            print("   에러 스크린샷 저장: playwright-state/error_login.png")

        finally:
            await browser.close()


async def test_session_manager():
    """세션 매니저 테스트."""
    print("\n" + "=" * 50)
    print("🧪 테스트 2: 세션 매니저")
    print("=" * 50)

    user_id = os.getenv("NAVER_BLOG_ID")
    password = os.getenv("NAVER_BLOG_PASSWORD")
    headless = os.getenv("HEADLESS", "false").lower() == "true"

    if not user_id or not password:
        print("❌ .env 파일에 NAVER_BLOG_ID와 NAVER_BLOG_PASSWORD를 설정해주세요.")
        return

    session_manager = SessionManager(
        user_id=user_id,
        password=password,
        storage_path="playwright-state/test_auth.json",
        session_validity_hours=24,
    )

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=headless,
            args=[
                "--disable-blink-features=AutomationControlled",
            ],
        )

        try:
            # 첫 번째 호출: 새로 로그인 또는 세션 재사용
            print("\n1️⃣ 첫 번째 세션 요청...")
            context = await session_manager.get_or_create_session(browser, headless)

            # 세션 유효성 확인
            is_valid = await session_manager.is_session_valid(context)
            print(f"   세션 유효성: {'✅ 유효' if is_valid else '❌ 무효'}")

            await context.close()

            # 두 번째 호출: 저장된 세션 재사용
            print("\n2️⃣ 두 번째 세션 요청 (재사용 테스트)...")
            context = await session_manager.get_or_create_session(browser, headless)

            is_valid = await session_manager.is_session_valid(context)
            print(f"   세션 유효성: {'✅ 유효' if is_valid else '❌ 무효'}")

            await context.close()

            print("\n✅ 세션 매니저 테스트 완료!")

        except Exception as e:
            print(f"\n❌ 세션 매니저 테스트 실패: {e}")

        finally:
            await browser.close()


async def main():
    """메인 테스트 함수."""
    print("\n" + "🔧 네이버 로그인 자동화 테스트" + "\n")

    # 테스트 1: 기본 로그인
    await test_login_basic()

    # 테스트 2: 세션 매니저
    await test_session_manager()

    print("\n" + "=" * 50)
    print("✅ 모든 테스트 완료!")
    print("=" * 50 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
