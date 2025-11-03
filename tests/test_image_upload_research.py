"""네이버 블로그 이미지 업로드 구조 조사."""

import asyncio
import sys

sys.path.insert(0, "src")

from naver_blog_mcp.server import NaverBlogMCPServer


async def research_image_upload():
    """이미지 업로드 UI 구조를 조사합니다."""
    print("=" * 60)
    print("네이버 블로그 이미지 업로드 구조 조사")
    print("=" * 60)
    print()

    server = NaverBlogMCPServer()
    print("✅ 서버 인스턴스 생성 완료")

    try:
        # 브라우저 초기화
        await server.initialize()
        print("✅ 브라우저 및 세션 초기화 완료")

        # 페이지 가져오기
        page = await server.get_page()
        print("✅ 페이지 생성 완료")

        # 글쓰기 페이지로 이동
        await page.goto("https://blog.naver.com")
        await asyncio.sleep(2)

        # 글쓰기 버튼 찾기
        write_btn_selectors = [
            "a[href*='postwrite']",
            "a:has-text('글쓰기')",
            "button:has-text('글쓰기')",
        ]

        for selector in write_btn_selectors:
            count = await page.locator(selector).count()
            if count > 0:
                element = page.locator(selector).first
                href = await element.get_attribute("href")
                if href:
                    if href.startswith("/"):
                        url = f"https://blog.naver.com{href}"
                    elif href.startswith("http"):
                        url = href
                    else:
                        url = f"https://blog.naver.com/{href}"
                    await page.goto(url, wait_until="load")
                    print(f"✅ 글쓰기 페이지 이동: {url}")
                    break

        await asyncio.sleep(3)

        # iframe 확인
        print()
        print("🔍 iframe 확인...")
        print("-" * 60)

        iframe_selectors = ["iframe#mainFrame", "iframe[name='mainFrame']"]
        main_frame = None

        for selector in iframe_selectors:
            count = await page.locator(selector).count()
            if count > 0:
                print(f"✅ iframe 발견: {selector}")
                frame_element = await page.wait_for_selector(selector, timeout=5000)
                main_frame = await frame_element.content_frame()
                if main_frame:
                    print(f"✅ iframe 접근 성공")
                    # iframe 내부 URL 출력
                    frame_url = main_frame.url
                    print(f"   Frame URL: {frame_url}")
                    break

        if not main_frame:
            print("❌ iframe을 찾을 수 없거나 접근 실패")
            await server.cleanup()
            return

        # iframe 로딩 대기
        await asyncio.sleep(3)

        print()
        print("🔍 iframe 내부 이미지 업로드 UI 요소 검색 중...")
        print("-" * 60)

        # 1. 이미지 버튼 찾기 (iframe 내부)
        image_button_selectors = [
            "button[aria-label*='사진']",
            "button[aria-label*='이미지']",
            "button[title*='사진']",
            "button[title*='이미지']",
            "button:has-text('사진')",
            "button:has-text('이미지')",
            ".se-toolbar-group button[data-name='image']",
            ".se-toolbar-group button[data-name='photo']",
            "button.se-toolbar-button-image",
            "[class*='image'][class*='button']",
        ]

        found_buttons = []
        for selector in image_button_selectors:
            try:
                count = await main_frame.locator(selector).count()
                if count > 0:
                    element = main_frame.locator(selector).first
                    # 요소 정보 수집
                    tag = await element.evaluate("el => el.tagName")
                    classes = await element.get_attribute("class") or ""
                    aria_label = await element.get_attribute("aria-label") or ""
                    title = await element.get_attribute("title") or ""
                    data_name = await element.get_attribute("data-name") or ""

                    info = {
                        "selector": selector,
                        "tag": tag,
                        "classes": classes,
                        "aria_label": aria_label,
                        "title": title,
                        "data_name": data_name,
                    }
                    found_buttons.append(info)
                    print(f"\n✅ 발견: {selector}")
                    print(f"   Tag: {tag}")
                    if classes:
                        print(f"   Classes: {classes}")
                    if aria_label:
                        print(f"   Aria-Label: {aria_label}")
                    if title:
                        print(f"   Title: {title}")
                    if data_name:
                        print(f"   Data-Name: {data_name}")
            except Exception as e:
                continue

        print()
        print("-" * 60)

        if not found_buttons:
            print("❌ 이미지 버튼을 찾을 수 없습니다.")
            print()
            print("📸 iframe 스크린샷 저장 중...")
            await page.screenshot(path="playwright-state/screenshots/iframe_page.png", full_page=True)
            print("✅ 스크린샷 저장: playwright-state/screenshots/iframe_page.png")

            # iframe HTML 저장
            print()
            print("📄 iframe HTML 저장 중...")
            from pathlib import Path
            html_dir = Path("playwright-state/html")
            html_dir.mkdir(parents=True, exist_ok=True)
            content = await main_frame.content()
            html_path = html_dir / "iframe_content.html"
            html_path.write_text(content, encoding="utf-8")
            print(f"✅ HTML 저장: {html_path}")

            print()
            print("🔍 iframe 내부의 모든 버튼 찾기...")
            all_buttons = await main_frame.locator("button").all()
            print(f"   총 {len(all_buttons)}개의 버튼 발견")

            # 처음 30개 버튼의 텍스트 출력
            print()
            print("처음 30개 버튼:")
            for i, btn in enumerate(all_buttons[:30]):
                try:
                    text = await btn.inner_text()
                    aria_label = await btn.get_attribute("aria-label")
                    title = await btn.get_attribute("title")
                    classes = await btn.get_attribute("class")

                    if text or aria_label or title:
                        print(f"   [{i+1}] Text: '{text}' | Aria: '{aria_label}' | Title: '{title}'")
                        if classes and len(classes) < 100:
                            print(f"       Classes: {classes[:100]}")
                except:
                    continue

        else:
            print(f"✅ 총 {len(found_buttons)}개의 이미지 버튼 발견!")
            print()
            print("🎯 권장 셀렉터:")
            if found_buttons:
                best = found_buttons[0]
                print(f"   {best['selector']}")

            # 이미지 버튼 클릭 시도 (toolbar의 사진 버튼)
            print()
            print("🖱️  툴바의 '사진' 버튼 클릭 시도...")
            try:
                # data-name='image' 버튼 우선 시도
                photo_btn_selector = "button[data-name='image']"
                await main_frame.locator(photo_btn_selector).first.click()
                print(f"✅ 사진 버튼 클릭 성공: {photo_btn_selector}")
                await asyncio.sleep(2)

                # 파일 업로드 input 찾기 (iframe 내부)
                print()
                print("🔍 iframe 내부 파일 업로드 input 찾기...")
                file_input_selectors = [
                    "input[type='file']",
                    "input[accept*='image']",
                    "input[name*='file']",
                    "input[name*='image']",
                    "input[name*='upload']",
                ]

                found_file_input = False
                for selector in file_input_selectors:
                    count = await main_frame.locator(selector).count()
                    if count > 0:
                        print(f"✅ 발견: {selector} ({count}개)")
                        # 첫 번째 요소의 속성 출력
                        element = main_frame.locator(selector).first
                        accept = await element.get_attribute("accept") or ""
                        name = await element.get_attribute("name") or ""
                        id_attr = await element.get_attribute("id") or ""
                        print(f"   Accept: {accept}")
                        print(f"   Name: {name}")
                        print(f"   ID: {id_attr}")
                        found_file_input = True

                if not found_file_input:
                    # 전체 페이지에서도 찾아보기
                    print()
                    print("🔍 전체 페이지에서 파일 input 찾기...")
                    for selector in file_input_selectors:
                        count = await page.locator(selector).count()
                        if count > 0:
                            print(f"✅ 발견 (메인 페이지): {selector} ({count}개)")

                # 스크린샷
                await page.screenshot(path="playwright-state/screenshots/upload_dialog.png", full_page=True)
                print()
                print("✅ 업로드 다이얼로그 스크린샷 저장")

            except Exception as e:
                print(f"⚠️  버튼 클릭 실패: {e}")
                import traceback
                traceback.print_exc()

        print()
        print("=" * 60)
        print("조사 완료!")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ 조사 실패: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        # 리소스 정리
        await asyncio.sleep(5)  # 확인할 시간
        await server.cleanup()
        print("\n✅ 리소스 정리 완료")


if __name__ == "__main__":
    asyncio.run(research_image_upload())
