"""네이버 블로그 카테고리 UI 구조 조사 스크립트."""
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


async def research_category_ui():
    """카테고리 UI 구조를 조사합니다."""

    print("=" * 80)
    print("네이버 블로그 카테고리 UI 구조 조사")
    print("=" * 80)

    # 환경 변수 확인
    config.validate()

    async with async_playwright() as p:
        # 브라우저 실행
        browser = await p.chromium.launch(
            headless=False,
            slow_mo=500
        )

        # 세션 관리자
        session_manager = SessionManager(
            user_id=config.NAVER_BLOG_ID,
            password=config.NAVER_BLOG_PASSWORD
        )
        context = await session_manager.get_or_create_session(browser)
        page = await context.new_page()

        try:
            # 1. 내 블로그로 이동
            print("\n[1단계] 내 블로그로 이동...")
            blog_url = f"https://blog.naver.com/{config.NAVER_BLOG_ID}"
            await page.goto(blog_url, wait_until="networkidle")
            await asyncio.sleep(2)

            print(f"현재 URL: {page.url}")

            # 2. 모든 링크 찾기 (카테고리 관련)
            print("\n[2단계] 모든 링크 찾기...")

            all_links = await page.query_selector_all("a")
            print(f"총 {len(all_links)}개의 링크 발견")

            # "카테고리" 또는 "PostList" 포함된 링크만 필터링
            category_related_links = []
            for link in all_links[:50]:  # 최대 50개만 확인
                try:
                    text = await link.text_content()
                    href = await link.get_attribute("href")

                    if not href:
                        continue

                    # 카테고리 관련 링크 판별
                    if ("PostList" in href or
                        "category" in href.lower() or
                        (text and len(text.strip()) > 0 and len(text.strip()) < 30)):

                        class_name = await link.get_attribute("class") or ""
                        category_related_links.append({
                            "text": text.strip() if text else "",
                            "href": href,
                            "class": class_name
                        })
                except:
                    continue

            if category_related_links:
                print(f"\n✓ 카테고리 관련 링크 {len(category_related_links)}개 발견:")
                for idx, link in enumerate(category_related_links[:10]):
                    print(f"\n  [{idx+1}] 텍스트: '{link['text']}'")
                    print(f"      URL: {link['href'][:100]}")
                    print(f"      클래스: {link['class']}")
            else:
                print("\n⚠️  카테고리 관련 링크를 찾지 못했습니다")
                print("   iframe 내부를 확인합니다...")

                # iframe 찾기
                iframe_element = await page.query_selector("iframe#mainFrame")
                if not iframe_element:
                    iframe_element = await page.query_selector("iframe")

                if iframe_element:
                    main_frame = await iframe_element.content_frame()
                    print(f"\n✓ iframe 발견, 내부 확인 중...")

                    # iframe 내부의 모든 링크
                    iframe_links = await main_frame.query_selector_all("a")
                    print(f"   iframe 내부 링크: {len(iframe_links)}개")

                    for link in iframe_links[:20]:
                        try:
                            text = await link.text_content()
                            href = await link.get_attribute("href")
                            if href and text:
                                print(f"   - '{text.strip()[:30]}': {href[:80]}")
                        except:
                            continue

            # 3. 분석 완료
            print("\n[3단계] 분석 완료")

            # 4. iframe 확인
            print("\n[4단계] iframe 구조 확인...")
            frames = page.frames
            print(f"총 {len(frames)}개의 프레임")
            for idx, frame in enumerate(frames):
                print(f"  프레임 #{idx}: {frame.name} - {frame.url[:80]}")

            # 5. 사용자 확인
            print("\n" + "=" * 80)
            print("브라우저에서 카테고리를 직접 확인해보세요.")
            print("F12 개발자 도구로 DOM 구조를 살펴볼 수 있습니다.")
            print("=" * 80)
            input("\n계속하려면 Enter를 누르세요...")

        finally:
            await context.close()
            await browser.close()

    print("\n✅ 조사 완료")


if __name__ == "__main__":
    asyncio.run(research_category_ui())
