"""네이버 블로그 카테고리 UI 구조 조사 (v2)."""
import asyncio
import sys
from pathlib import Path
import re

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


async def research_categories():
    """카테고리 조회 로직을 테스트합니다."""

    print("=" * 80)
    print("네이버 블로그 카테고리 조회 테스트")
    print("=" * 80)

    config.validate()

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=300)
        session_manager = SessionManager(
            user_id=config.NAVER_BLOG_ID,
            password=config.NAVER_BLOG_PASSWORD
        )
        context = await session_manager.get_or_create_session(browser)
        page = await context.new_page()

        try:
            # 1. 블로그 메인으로 이동
            blog_url = f"https://blog.naver.com/{config.NAVER_BLOG_ID}"
            await page.goto(blog_url, wait_until="networkidle")
            await asyncio.sleep(2)
            print(f"\n블로그 접속: {blog_url}")

            # 2. iframe 찾기
            iframe_element = await page.wait_for_selector("iframe#mainFrame", timeout=10000)
            main_frame = await iframe_element.content_frame()
            print("✓ iframe#mainFrame 접근 성공")

            # 3. 카테고리 링크 찾기
            print("\n[카테고리 링크 찾기]")

            # PostList 링크 찾기 (카테고리 링크는 보통 PostList.naver를 사용)
            category_links = await main_frame.query_selector_all("a[href*='PostList']")
            print(f"PostList 링크 {len(category_links)}개 발견")

            categories = []
            for idx, link in enumerate(category_links):
                text = await link.text_content()
                href = await link.get_attribute("href")
                class_name = await link.get_attribute("class")

                # 텍스트가 있고, 너무 길지 않으면 (카테고리명은 짧음)
                if text and len(text.strip()) > 0 and len(text.strip()) < 50:
                    # URL에서 categoryNo 추출
                    category_no = None
                    if "categoryNo=" in href:
                        match = re.search(r'categoryNo=(\d+)', href)
                        if match:
                            category_no = match.group(1)

                    category_info = {
                        "name": text.strip(),
                        "url": href,
                        "categoryNo": category_no,
                        "class": class_name
                    }

                    # "열정의불꽃" 같은 블로그 이름은 제외
                    if category_info["name"] not in [config.NAVER_BLOG_ID, "블로그 홈"]:
                        categories.append(category_info)

            # 중복 제거 (같은 이름)
            unique_categories = {}
            for cat in categories:
                if cat["name"] not in unique_categories:
                    unique_categories[cat["name"]] = cat

            print(f"\n✅ 발견된 카테고리: {len(unique_categories)}개")
            print("-" * 80)

            for idx, (name, cat) in enumerate(unique_categories.items(), 1):
                print(f"{idx}. {name}")
                print(f"   URL: {cat['url'][:100]}")
                if cat['categoryNo']:
                    print(f"   카테고리 번호: {cat['categoryNo']}")
                print()

            print("-" * 80)

            # 4. 다른 방법: 사이드바에서 찾기
            print("\n[사이드바에서 카테고리 찾기]")

            # 일반적인 사이드바 셀렉터들
            sidebar_selectors = [
                ".area_links",
                ".blog_cate",
                "[class*='cate']",
                ".blog_list",
            ]

            for selector in sidebar_selectors:
                try:
                    elements = await main_frame.query_selector_all(selector)
                    if elements:
                        print(f"✓ {selector} 발견: {len(elements)}개")
                        for elem in elements[:3]:
                            html = await elem.inner_html()
                            print(f"   HTML 일부: {html[:200]}")
                except:
                    continue

        finally:
            await context.close()
            await browser.close()

    print("\n✅ 조사 완료")


if __name__ == "__main__":
    asyncio.run(research_categories())
