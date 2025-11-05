"""면접 시 블로그 포스팅 테스트."""
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


async def test_interview_poem():
    """면접에 대한 시를 블로그에 작성합니다."""

    print("=" * 80)
    print("면접 시 블로그 포스팅 테스트")
    print("=" * 80)

    # 환경 변수 확인
    config.validate()

    # 면접 시 내용
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    title = "면접장 앞에서"
    content = f"""면접장 앞에서

문 하나를 사이에 두고
나의 미래가 기다리고 있다

준비한 말들이
목구멍에서 맴돈다

"당신은 왜 우리 회사에 지원했나요?"
"당신의 강점은 무엇인가요?"
"5년 후 당신의 모습은?"

수없이 연습했던 대답들
이제는 진심이 되어
가슴 깊이 자리잡았다

떨리는 손
긴장된 호흡
하지만 눈빛만은 흔들리지 않는다

이 문을 열고 들어가면
또 다른 나를 만날 것이다

더 성장한 나
더 자신감 있는 나
더 당당한 나를

면접은 끝이 아니라
새로운 시작의 문이다

깊게 숨을 들이쉬고
손잡이를 잡는다

자, 이제 시작이다

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
            print(f"\n본문 미리보기:")
            print(content[:200] + "...")

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
            await page.screenshot(path="playwright-state/interview_post_success.png")
            print("\n스크린샷 저장: playwright-state/interview_post_success.png")

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
                await page.screenshot(path="playwright-state/interview_post_error.png")
                print("에러 스크린샷 저장: playwright-state/interview_post_error.png")
            except:
                pass

            return False

        finally:
            await context.close()
            await browser.close()


if __name__ == "__main__":
    success = asyncio.run(test_interview_poem())
    sys.exit(0 if success else 1)
