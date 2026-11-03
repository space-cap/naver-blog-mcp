"""힘내라 응원글 블로그 포스팅 테스트."""
import asyncio
import sys
from pathlib import Path
from datetime import datetime

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
from naver_blog_mcp.automation.post_actions import create_blog_post


async def test_cheer_up_post():
    """힘내라 응원글 블로그 포스팅."""

    print("=" * 80)
    print("힘내라 응원글 블로그 포스팅 테스트")
    print("=" * 80)

    # 환경 변수 확인
    config.validate()

    # 힘내라 응원글 (5줄)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    title = "힘내세요, 당신은 해낼 수 있습니다"
    content = f"""오늘 하루도 고생 많으셨습니다.

때로는 힘들고 지칠 때가 있지만, 그럴 때일수록 한 발짝만 더 내딛어 보세요.
당신이 걸어온 길을 돌아보면, 이미 많은 어려움을 극복해왔다는 것을 알게 될 거예요.
지금의 힘든 순간도 언젠가는 성장의 발판이 되어줄 것입니다.
당신은 생각보다 훨씬 강하고, 충분히 해낼 수 있는 사람입니다.
힘내세요, 응원합니다!

---
작성 시각: {timestamp}
"""

    async with async_playwright() as p:
        # 브라우저 실행
        browser = await p.chromium.launch(
            headless=False,
            slow_mo=100
        )

        # 세션 관리자
        session_manager = SessionManager(
            user_id=config.NAVER_BLOG_ID,
            password=config.NAVER_BLOG_PASSWORD
        )
        context = await session_manager.get_or_create_session(browser, headless=False)
        page = await context.new_page()

        try:
            print("\n[1단계] 블로그 글 작성 시작...")
            print(f"제목: {title}")
            print(f"\n본문:")
            print(content)

            # 글 작성
            result = await create_blog_post(
                page=page,
                title=title,
                content=content,
                use_html=False,
                wait_for_completion=True,
            )

            print("\n[2단계] 작성 완료!")
            print(f"성공 여부: {result['success']}")
            print(f"메시지: {result['message']}")

            if result.get('post_url'):
                print(f"글 URL: {result['post_url']}")

            # 스크린샷 저장
            await page.screenshot(path="playwright-state/cheer_up_post_success.png")
            print("\n스크린샷 저장: playwright-state/cheer_up_post_success.png")

            if result['success']:
                print("\n[테스트 성공]")
                return True
            else:
                print("\n[테스트 실패]")
                return False

        except Exception as e:
            print(f"\n[오류 발생]: {e}")
            import traceback
            traceback.print_exc()

            # 에러 스크린샷
            try:
                await page.screenshot(path="playwright-state/cheer_up_post_error.png")
                print("에러 스크린샷 저장: playwright-state/cheer_up_post_error.png")
            except:
                pass

            return False

        finally:
            await context.close()
            await browser.close()


if __name__ == "__main__":
    success = asyncio.run(test_cheer_up_post())
    sys.exit(0 if success else 1)
