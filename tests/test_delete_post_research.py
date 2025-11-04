"""네이버 블로그 글 삭제 UI 구조 조사 스크립트.

이 스크립트는 네이버 블로그의 글 삭제 UI를 조사하여
자동화 구현 가능성을 확인합니다.
"""
import asyncio
import sys
import os
from pathlib import Path

# Windows 콘솔 인코딩 설정
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from playwright.async_api import async_playwright
from naver_blog_mcp.config import config
from naver_blog_mcp.services.session_manager import SessionManager


async def research_delete_ui():
    """글 삭제 UI 구조를 조사합니다."""

    print("=" * 80)
    print("네이버 블로그 글 삭제 UI 구조 조사")
    print("=" * 80)

    # 환경 변수 확인
    config.validate()

    async with async_playwright() as p:
        # 브라우저 실행
        browser = await p.chromium.launch(
            headless=False,  # UI 확인을 위해 브라우저 표시
            slow_mo=100
        )

        # 세션 관리자로 컨텍스트 가져오기
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

            print(f"✓ 블로그 URL: {blog_url}")

            # 2. 첫 번째 글 찾기
            print("\n[2단계] 첫 번째 글 찾기...")

            # 블로그 메인에서 첫 번째 글 링크 찾기
            # 여러 셀렉터 시도
            selectors_to_try = [
                "a.title_link",  # 제목 링크
                ".area_post a[href*='PostView']",  # 글 영역의 PostView 링크
                "a[href*='/PostView.naver']",  # PostView가 포함된 링크
            ]

            first_post_link = None
            for selector in selectors_to_try:
                try:
                    element = await page.wait_for_selector(selector, timeout=5000)
                    if element:
                        first_post_link = await element.get_attribute('href')
                        print(f"✓ 첫 번째 글 찾음 (selector: {selector})")
                        print(f"  링크: {first_post_link}")
                        break
                except Exception as e:
                    print(f"  셀렉터 {selector} 실패: {e}")
                    continue

            if not first_post_link:
                print("❌ 첫 번째 글을 찾을 수 없습니다.")
                print("   블로그에 글이 하나 이상 있는지 확인해주세요.")
                return

            # 3. 글 페이지로 이동
            print(f"\n[3단계] 글 페이지로 이동...")
            await page.goto(first_post_link, wait_until="networkidle")
            await asyncio.sleep(2)

            print(f"✓ 현재 URL: {page.url}")

            # 4. 삭제 버튼/수정 메뉴 찾기
            print("\n[4단계] 삭제 버튼/수정 메뉴 찾기...")

            # 가능한 삭제 관련 셀렉터들
            delete_selectors = [
                # 수정/삭제 메뉴
                "button:has-text('수정')",
                "a:has-text('수정')",
                "button:has-text('삭제')",
                "a:has-text('삭제')",
                ".btn_post_opt",  # 글 옵션 버튼
                ".post_function",  # 글 기능 영역
                "#postOptionMenu",  # 글 옵션 메뉴

                # 더보기 메뉴
                "button:has-text('더보기')",
                ".more_btn",
                ".btn_more",

                # 관리 메뉴
                "a:has-text('관리')",
                ".management",
            ]

            found_elements = []
            for selector in delete_selectors:
                try:
                    elements = await page.query_selector_all(selector)
                    if elements:
                        for idx, elem in enumerate(elements):
                            text = await elem.text_content()
                            tag = await elem.evaluate("el => el.tagName")
                            classes = await elem.get_attribute("class")
                            href = await elem.get_attribute("href")

                            found_elements.append({
                                "selector": selector,
                                "index": idx,
                                "tag": tag,
                                "text": text.strip() if text else "",
                                "class": classes,
                                "href": href
                            })

                            print(f"\n✓ 발견: {selector} (#{idx})")
                            print(f"  태그: {tag}")
                            print(f"  텍스트: '{text.strip() if text else ''}'")
                            print(f"  클래스: {classes}")
                            if href:
                                print(f"  링크: {href}")
                except Exception as e:
                    continue

            if not found_elements:
                print("\n❌ 수정/삭제 관련 요소를 찾지 못했습니다.")

                # 페이지 HTML 일부 출력
                print("\n[디버그] 페이지 소스 일부:")
                body_html = await page.content()
                # "수정" 또는 "삭제" 텍스트 주변 HTML 찾기
                import re
                matches = re.findall(r'.{0,100}(수정|삭제).{0,100}', body_html)
                for match in matches[:5]:  # 최대 5개만 출력
                    print(f"  ...{match}...")
            else:
                print(f"\n✅ 총 {len(found_elements)}개의 관련 요소를 찾았습니다.")

            # 5. iframe 확인
            print("\n[5단계] iframe 구조 확인...")
            frames = page.frames
            print(f"  총 {len(frames)}개의 프레임 발견")
            for idx, frame in enumerate(frames):
                frame_name = frame.name
                frame_url = frame.url
                print(f"  프레임 #{idx}: name='{frame_name}', url='{frame_url}'")

                # mainFrame이 있다면 내부에서도 삭제 버튼 찾기
                if frame_name == "mainFrame":
                    print("\n  [mainFrame 내부 조사]")
                    for selector in delete_selectors[:5]:  # 주요 셀렉터만
                        try:
                            elements = await frame.query_selector_all(selector)
                            if elements:
                                for elem in elements:
                                    text = await elem.text_content()
                                    print(f"    ✓ {selector}: '{text.strip() if text else ''}'")
                        except:
                            continue

            # 6. 사용자 입력 대기 (수동 확인)
            print("\n" + "=" * 80)
            print("브라우저에서 수동으로 삭제 버튼 위치를 확인해주세요.")
            print("확인 후 이 터미널에서 Enter를 누르면 종료됩니다.")
            print("=" * 80)
            input("\n계속하려면 Enter를 누르세요...")

        finally:
            await context.close()
            await browser.close()

    print("\n✅ 조사 완료")


if __name__ == "__main__":
    asyncio.run(research_delete_ui())
