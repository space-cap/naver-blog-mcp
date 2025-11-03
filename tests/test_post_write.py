"""네이버 블로그 글쓰기 테스트 스크립트.

사용법:
    # .env 파일 설정 후
    uv run python tests/test_post_write.py
"""

import asyncio
import os
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from playwright.async_api import async_playwright

# 프로젝트 루트 경로에서 .env 로드
project_root = Path(__file__).parent.parent
load_dotenv(project_root / ".env")

# 임포트 경로 추가
import sys

sys.path.insert(0, str(project_root / "src"))

from naver_blog_mcp.automation.post_actions import (
    create_blog_post,
    navigate_to_post_write_page,
    fill_post_title,
    fill_post_content,
    publish_post,
    NaverBlogPostError,
)
from naver_blog_mcp.services.session_manager import SessionManager


async def test_post_write_full():
    """전체 글쓰기 프로세스 테스트."""
    print("\n" + "=" * 50)
    print("🧪 테스트 1: 전체 글쓰기 프로세스")
    print("=" * 50)

    user_id = os.getenv("NAVER_BLOG_ID")
    password = os.getenv("NAVER_BLOG_PASSWORD")
    headless = os.getenv("HEADLESS", "false").lower() == "true"

    if not user_id or not password:
        print("❌ .env 파일에 NAVER_BLOG_ID와 NAVER_BLOG_PASSWORD를 설정해주세요.")
        return

    # 테스트용 글 제목과 내용
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    test_title = f"[테스트] Playwright 자동화 테스트 - {timestamp}"
    test_content = f"""
안녕하세요!

이 글은 Playwright 기반 네이버 블로그 MCP 서버의 자동화 테스트입니다.

작성 시각: {timestamp}

주요 기능:
1. 자동 로그인 및 세션 관리
2. 글 제목 입력
3. iframe 내부 본문 입력
4. 자동 발행

테스트가 성공적으로 완료되었습니다! ✅
""".strip()

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
            # 1. 세션 가져오기 (자동 로그인 또는 재사용)
            print("\n1️⃣ 세션 확인 중...")
            context = await session_manager.get_or_create_session(browser, headless)

            # 2. 새 페이지 열기
            page = await context.new_page()

            # 3. 글 작성 및 발행
            print("\n2️⃣ 블로그 글 작성 시작...")
            result = await create_blog_post(
                page=page,
                title=test_title,
                content=test_content,
                use_html=False,  # 텍스트 모드
                wait_for_completion=True,
            )

            print(f"\n✅ {result['message']}")
            print(f"   제목: {result['title']}")
            if result.get("post_url"):
                print(f"   URL: {result['post_url']}")

            # 스크린샷 저장
            await page.screenshot(path="playwright-state/test_post_success.png")
            print("   스크린샷 저장: playwright-state/test_post_success.png")

        except NaverBlogPostError as e:
            print(f"\n❌ 글쓰기 실패: {e}")
            # 에러 스크린샷 저장
            try:
                await page.screenshot(path="playwright-state/error_post_write.png")
                print("   에러 스크린샷 저장: playwright-state/error_post_write.png")
            except:
                pass

        except Exception as e:
            print(f"\n❌ 예상치 못한 오류: {e}")

        finally:
            await context.close()
            await browser.close()


async def test_post_write_step_by_step():
    """단계별 글쓰기 테스트."""
    print("\n" + "=" * 50)
    print("🧪 테스트 2: 단계별 글쓰기")
    print("=" * 50)

    user_id = os.getenv("NAVER_BLOG_ID")
    password = os.getenv("NAVER_BLOG_PASSWORD")
    headless = os.getenv("HEADLESS", "false").lower() == "true"

    if not user_id or not password:
        print("❌ .env 파일에 NAVER_BLOG_ID와 NAVER_BLOG_PASSWORD를 설정해주세요.")
        return

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    test_title = f"[단계별 테스트] {timestamp}"
    test_content = "단계별 테스트 본문입니다."

    session_manager = SessionManager(
        user_id=user_id,
        password=password,
        storage_path="playwright-state/test_auth.json",
    )

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=headless)

        try:
            context = await session_manager.get_or_create_session(browser, headless)
            page = await context.new_page()

            # 1. 글쓰기 페이지 이동
            print("\n1️⃣ 글쓰기 페이지로 이동...")
            await navigate_to_post_write_page(page)

            # 2. 제목 입력
            print("\n2️⃣ 제목 입력...")
            await fill_post_title(page, test_title)

            # 3. 본문 입력
            print("\n3️⃣ 본문 입력...")
            await fill_post_content(page, test_content, use_html=False)

            # 4. 발행하지 않고 대기 (수동 확인용)
            print("\n⏸️  발행하지 않고 대기 중 (10초)...")
            print("   브라우저에서 내용을 확인하세요.")
            await asyncio.sleep(10)

            # 5. 발행
            print("\n4️⃣ 발행...")
            result = await publish_post(page, wait_for_completion=True)

            print(f"\n✅ {result['message']}")
            if result.get("post_url"):
                print(f"   URL: {result['post_url']}")

        except NaverBlogPostError as e:
            print(f"\n❌ 단계별 테스트 실패: {e}")

        finally:
            await context.close()
            await browser.close()


async def main():
    """메인 테스트 함수."""
    print("\n" + "🔧 네이버 블로그 글쓰기 자동화 테스트" + "\n")

    # 테스트 선택
    print("실행할 테스트를 선택하세요:")
    print("1. 전체 글쓰기 프로세스 테스트 (권장)")
    print("2. 단계별 글쓰기 테스트")
    print("3. 모두 실행")

    # 자동으로 테스트 1 실행 (CI/CD 환경 고려)
    test_mode = os.getenv("TEST_MODE", "1")

    if test_mode == "1":
        await test_post_write_full()
    elif test_mode == "2":
        await test_post_write_step_by_step()
    elif test_mode == "3":
        await test_post_write_full()
        await test_post_write_step_by_step()
    else:
        print("❌ 잘못된 선택입니다. TEST_MODE 환경 변수를 1, 2, 3 중 하나로 설정하세요.")

    print("\n" + "=" * 50)
    print("✅ 테스트 완료!")
    print("=" * 50 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
