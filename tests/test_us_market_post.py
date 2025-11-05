"""미국 증시 동향 블로그 포스팅 테스트."""
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


async def test_us_market_post():
    """미국 증시 동향 블로그 포스팅 테스트."""

    print("=" * 80)
    print("미국 증시 동향 블로그 포스팅 테스트")
    print("=" * 80)

    # 환경 변수 확인
    config.validate()

    # 미국 증시 동향 내용 (5줄)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    title = "오늘 미국 증시 동향"
    content = f"""오늘 미국 증시 동향 정리

1. S&P 500 지수는 전일 대비 0.5% 상승하며 강세를 보였습니다.
2. 나스닥은 기술주 중심으로 1.2% 상승하며 랠리를 이어갔습니다.
3. 다우존스 산업평균지수는 소폭 0.3% 상승으로 마감했습니다.
4. 엔비디아와 애플 등 빅테크 종목들이 시장을 주도했습니다.
5. 연준의 금리 동결 가능성이 높아지면서 투자 심리가 개선되었습니다.

---
작성 시각: {timestamp}
"""

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
            await page.screenshot(path="playwright-state/us_market_post_success.png")
            print("\n스크린샷 저장: playwright-state/us_market_post_success.png")

            if result['success']:
                print("\n[테스트 성공] 제목과 내용이 모두 정상적으로 게시되었는지 확인해주세요.")
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
                await page.screenshot(path="playwright-state/us_market_post_error.png")
                print("에러 스크린샷 저장: playwright-state/us_market_post_error.png")
            except:
                pass

            return False

        finally:
            await context.close()
            await browser.close()


if __name__ == "__main__":
    success = asyncio.run(test_us_market_post())
    sys.exit(0 if success else 1)
