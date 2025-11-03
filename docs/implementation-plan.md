# 네이버 블로그 MCP 서버 구현 계획서 (Playwright 기반)

## 1. 프로젝트 개요

### 1.1 목표
Playwright 웹 브라우저 자동화를 활용하여 Model Context Protocol(MCP) 서버를 구현하고, AI 어시스턴트가 네이버 블로그에 글을 작성할 수 있도록 지원합니다.

### 1.2 핵심 요구사항
- ✅ 네이버 블로그에 글 작성 (제목, 내용, 카테고리, 태그)
- ✅ 작성된 글 수정
- ✅ 작성된 글 삭제
- ✅ 카테고리 목록 조회
- ✅ 최근 글 목록 조회
- ✅ 이미지 업로드 및 본문 삽입
- ✅ MCP 프로토콜 표준 준수
- ✅ 세션 관리 (로그인 상태 유지)

### 1.3 개발 기간
- **Phase 1 (Week 1-2)**: Playwright 기본 자동화 + 핵심 기능 구현
- **Phase 2 (Week 3)**: 고급 기능 및 안정성 개선
- **Phase 3 (Week 4)**: 테스트, 문서화, 배포

### 1.4 기술 선택 근거: Playwright vs Selenium

| 항목 | Playwright | Selenium |
|------|-----------|----------|
| 성능 | ✅ 30% 더 빠름 | ❌ 느림 |
| 자동 대기 | ✅ 내장 | ❌ 수동 설정 |
| MCP 호환성 | ✅ 비동기 네이티브 | ⚠️ 제한적 |
| 디버깅 | ✅ Inspector/Trace Viewer | ❌ 기본적 |
| 안정성 | ✅ 높음 | ⚠️ 중간 |

**결론**: Playwright 선택

## 2. 기술 스택

### 2.1 핵심 기술

```yaml
언어: Python 3.13

핵심 라이브러리:
  - mcp[cli] >= 1.20.0        # MCP SDK
  - playwright >= 1.40.0       # 브라우저 자동화
  - pydantic >= 2.5.0          # 데이터 검증
  - python-dotenv >= 1.0.0     # 환경 변수 관리
  - tenacity >= 8.2.0          # 재시도 로직
  - aiofiles >= 23.0.0         # 비동기 파일 I/O
  - markdown >= 3.5.0          # Markdown -> HTML 변환

개발 도구:
  - pytest >= 7.4.0            # 테스트 프레임워크
  - pytest-asyncio >= 0.21.0   # 비동기 테스트
  - pytest-playwright >= 0.4.0 # Playwright 테스트
  - pytest-cov >= 4.1.0        # 커버리지
  - black >= 23.0.0            # 코드 포매터
  - ruff >= 0.1.0              # 린터
  - mypy >= 1.7.0              # 타입 체커

패키지 관리:
  - uv                          # 고속 파이썬 패키지 매니저
```

### 2.2 Playwright 선택 이유

#### 1. 비동기 네이티브 지원
```python
# MCP 서버는 비동기 구조 - Playwright와 완벽한 호환
@server.tool()
async def naver_blog_create_post(title: str, content: str):
    async with async_playwright() as p:
        # 자연스러운 비동기 플로우
        browser = await p.chromium.launch()
        # ...
```

#### 2. 자동 대기 (코드 간결성)
```python
# Playwright - 간결하고 안정적
await page.fill("#title", "제목")  # 자동으로 요소 준비 대기

# Selenium - 복잡한 대기 로직 필요
wait = WebDriverWait(driver, 10)
element = wait.until(EC.element_to_be_clickable((By.ID, "title")))
```

#### 3. 강력한 디버깅 도구
- **Playwright Inspector**: 단계별 실행 및 디버깅
- **Trace Viewer**: 모든 액션의 시각적 기록
- **자동 스크린샷**: 에러 시 자동 캡처

#### 4. 세션 관리 용이성
```python
# 로그인 세션 저장 및 재사용
await page.context.storage_state(path="auth.json")

# 다음 실행 시 로그인 없이 재사용
context = await browser.new_context(storage_state="auth.json")
```

## 3. 구현 단계별 계획

### Phase 1: Playwright 기본 자동화 + 핵심 기능 (Week 1-2)

#### 1.1 프로젝트 초기 설정 (Day 1)

```bash
# 작업 내용
1. pyproject.toml 업데이트
2. Playwright 설치 및 브라우저 다운로드
3. 프로젝트 구조 생성
4. 환경 변수 설정

# 실행 명령어
uv add "playwright>=1.40.0"
uv run playwright install chromium

# 체크리스트
□ pyproject.toml 의존성 추가
□ Playwright 브라우저 설치 확인
□ src/naver_blog_mcp/ 디렉토리 구조 생성
□ .env.example 파일 생성
□ playwright-state/ 디렉토리 생성 (.gitignore 추가)
```

#### 1.2 Playwright 기본 자동화 구현 (Day 2-4)

**Day 2: 로그인 자동화**
```python
# 파일: src/naver_blog_mcp/automation/login.py

작업 내용:
1. 네이버 로그인 페이지 자동화
2. 세션 저장 기능
3. 저장된 세션 재사용

주요 코드:
async def login_to_naver(page, user_id, password):
    await page.goto("https://nid.naver.com/nidlogin.login")
    await page.fill("#id", user_id)
    await page.fill("#pw", password)
    await page.click(".btn_login")
    await page.wait_for_url("**/naver.com**", timeout=10000)

    # 세션 저장
    storage_state = await page.context.storage_state(
        path="playwright-state/auth.json"
    )
    return storage_state

테스트:
- 정상 로그인 성공
- 잘못된 비밀번호 에러 처리
- CAPTCHA 감지 및 알림
- 세션 저장/불러오기
```

**Day 3: 글쓰기 페이지 자동화**
```python
# 파일: src/naver_blog_mcp/automation/post_actions.py

작업 내용:
1. 글쓰기 페이지 네비게이션
2. 제목/내용 입력 자동화
3. iframe 처리 (스마트에디터)
4. 발행 버튼 클릭

주요 도전 과제:
- iframe 내부 에디터 접근
- 동적 로딩 대기
- 발행 완료 확인

구현:
async def fill_post_content(page, title, content):
    # 제목 입력
    await page.fill("input[placeholder*='제목']", title)

    # iframe 내부 에디터 접근
    frame = page.frame_locator("iframe.se-iframe")
    await frame.locator(".se-component-content").fill(content)

    # 발행
    await page.click("button:has-text('발행')")
    await page.wait_for_url("**/PostView.naver**")

테스트:
- 간단한 텍스트 글 작성
- 긴 내용 작성 (1000자+)
- 특수문자 포함 내용
```

**Day 4: DOM 셀렉터 정리 및 안정화**
```python
# 파일: src/naver_blog_mcp/automation/selectors.py

작업 내용:
1. 모든 DOM 셀렉터를 중앙 관리
2. 대체 셀렉터 정의 (UI 변경 대비)
3. 셀렉터 검증 유틸리티

SELECTORS = {
    "login": {
        "id_input": "#id",
        "pw_input": "#pw",
        "login_btn": [".btn_login", "button[type='submit']"],  # 대체 셀렉터
    },
    "post": {
        "title_input": ["input[placeholder*='제목']", "#title"],
        "content_frame": "iframe.se-iframe",
        "content_body": ".se-component-content",
        "publish_btn": ["button:has-text('발행')", ".publish-button"],
    }
}

테스트:
- 모든 셀렉터 유효성 검증
- 대체 셀렉터 우선순위 테스트
```

#### 1.3 MCP 서버 기본 구현 (Day 5-7)

**Day 5: MCP 서버 구조 설정**
```python
# 파일: src/naver_blog_mcp/server.py

작업 내용:
1. MCP 서버 초기화
2. Playwright 브라우저 인스턴스 관리
3. 세션 관리자 구현

from mcp.server import Server
from playwright.async_api import async_playwright

class NaverBlogMCPServer:
    def __init__(self):
        self.server = Server("naver-blog")
        self.browser = None
        self.context = None

    async def initialize(self):
        """브라우저 초기화 및 세션 복원"""
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(
            headless=os.getenv("HEADLESS", "true") == "true"
        )

        # 저장된 세션 복원
        if os.path.exists("playwright-state/auth.json"):
            self.context = await self.browser.new_context(
                storage_state="playwright-state/auth.json"
            )
        else:
            # 최초 로그인 필요
            await self.login()
```

**Day 6: 핵심 Tool 구현**
```python
# 파일: src/naver_blog_mcp/mcp/tools.py

구현 Tool:
1. naver_blog_create_post
2. naver_blog_delete_post
3. naver_blog_list_categories

@server.tool()
async def naver_blog_create_post(
    title: str,
    content: str,
    category: str = None,
    tags: list[str] = None,
    publish: bool = True
) -> dict:
    """네이버 블로그에 글 작성"""
    page = await get_page()

    # 글쓰기 페이지로 이동
    await page.goto("https://blog.naver.com/PostWriteForm.naver")

    # 제목, 내용 입력
    await page.fill("input[placeholder*='제목']", title)

    frame = page.frame_locator("iframe.se-iframe")
    await frame.locator(".se-component-content").fill(content)

    # 카테고리, 태그 설정
    if category:
        await page.select_option(".blog2_series", label=category)

    if tags:
        for tag in tags:
            await page.fill("input[placeholder*='태그']", tag)
            await page.press("input[placeholder*='태그']", "Enter")

    # 발행/임시저장
    if publish:
        await page.click("button:has-text('발행')")
    else:
        await page.click("button:has-text('임시저장')")

    # 완료 대기 및 URL 추출
    await page.wait_for_url("**/PostView.naver**")
    post_url = page.url

    return {
        "success": True,
        "post_url": post_url,
        "message": "글이 성공적으로 발행되었습니다."
    }
```

**Day 7: 통합 테스트**
```bash
테스트 시나리오:
1. MCP 서버 시작
2. 글 작성 Tool 호출
3. 실제 네이버 블로그에 글 게시 확인
4. 글 삭제 Tool 호출
5. 삭제 확인

체크리스트:
□ MCP 서버 정상 시작
□ Tool 등록 확인
□ 실제 블로그 포스팅 성공
□ 에러 처리 검증
```

#### 1.4 에러 처리 및 재시도 로직 (Day 8-10)

**Day 8: 에러 분류 및 처리**
```python
# 파일: src/naver_blog_mcp/automation/error_handler.py

작업 내용:
1. 커스텀 예외 정의
2. Playwright TimeoutError 처리
3. 네이버 UI 변경 감지
4. CAPTCHA 감지

class NaverBlogError(Exception):
    """기본 에러"""
    pass

class LoginFailedError(NaverBlogError):
    """로그인 실패 (비밀번호 오류, CAPTCHA 등)"""
    pass

class ElementNotFoundError(NaverBlogError):
    """페이지 요소를 찾을 수 없음 (UI 변경 가능성)"""
    pass

async def handle_playwright_error(error, page):
    """Playwright 에러 처리"""
    if "Timeout" in str(error):
        # 스크린샷 저장
        await page.screenshot(path=f"error_{datetime.now()}.png")
        # 재시도 또는 알림
    elif "locator" in str(error):
        # 셀렉터 문제 - 대체 셀렉터 시도
        raise ElementNotFoundError("UI가 변경되었을 수 있습니다.")
```

**Day 9: 재시도 로직**
```python
# tenacity를 활용한 재시도

from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
async def create_post_with_retry(page, post_data):
    try:
        return await create_post(page, **post_data)
    except TimeoutError:
        # 페이지 새로고침
        await page.reload()
        raise
    except ElementNotFoundError:
        # 대체 셀렉터 시도
        await try_alternative_selectors(page)
        raise

테스트:
- 네트워크 지연 시뮬레이션
- 요소 로딩 지연
- 3회 재시도 후 실패 확인
```

**Day 10: 스크린샷 및 디버깅 도구**
```python
# Trace Viewer 활용

async def create_post_with_trace(page, title, content):
    # Tracing 시작
    await page.context.tracing.start(
        screenshots=True,
        snapshots=True,
        sources=True
    )

    try:
        result = await create_post(page, title, content)
    finally:
        # Trace 저장 (성공/실패 무관)
        await page.context.tracing.stop(
            path=f"traces/post_{datetime.now()}.zip"
        )

    return result

# 나중에 분석: playwright show-trace traces/post_*.zip
```

### Phase 2: 고급 기능 및 안정성 개선 (Week 3)

#### 2.1 이미지 업로드 (Day 11-12)

**Day 11: Playwright File Upload**
```python
# 파일: src/naver_blog_mcp/automation/media_actions.py

async def upload_image_to_post(page, image_path):
    """
    스마트에디터에 이미지 업로드

    방법:
    1. 이미지 버튼 클릭
    2. 파일 선택 다이얼로그 처리
    3. 업로드 완료 대기
    """
    # 이미지 버튼 클릭
    await page.click("button[aria-label='사진']")

    # 파일 업로드
    async with page.expect_file_chooser() as fc_info:
        await page.click("input[type='file']")
    file_chooser = await fc_info.value
    await file_chooser.set_files(image_path)

    # 업로드 완료 대기
    await page.wait_for_selector(".uploaded-image", timeout=10000)

    # 업로드된 이미지 URL 추출
    img_url = await page.locator(".uploaded-image").get_attribute("src")
    return img_url

테스트:
- JPEG, PNG, GIF 업로드
- 다중 이미지 업로드
- 대용량 이미지 (5MB+)
```

**Day 12: 이미지 + 텍스트 통합**
```python
# Markdown에서 이미지 자동 업로드

import re
from pathlib import Path

async def process_markdown_with_images(page, markdown_content):
    """
    Markdown에서 로컬 이미지 경로를 찾아서 업로드
    ![alt](./images/photo.jpg) -> ![alt](업로드된 URL)
    """
    # 이미지 패턴 찾기
    image_pattern = r'!\[([^\]]*)\]\(([^\)]+)\)'
    matches = re.findall(image_pattern, markdown_content)

    for alt_text, image_path in matches:
        if not image_path.startswith("http"):
            # 로컬 파일 업로드
            uploaded_url = await upload_image_to_post(page, image_path)
            # Markdown 내용 교체
            markdown_content = markdown_content.replace(
                f'![{alt_text}]({image_path})',
                f'![{alt_text}]({uploaded_url})'
            )

    return markdown_content
```

#### 2.2 Markdown 지원 (Day 13-14)

**Day 13: Markdown -> HTML 변환**
```python
# 파일: src/naver_blog_mcp/utils/converters.py

import markdown
from markdown.extensions import fenced_code, tables, nl2br

def convert_markdown_to_html(md_content: str) -> str:
    """Markdown을 네이버 블로그 호환 HTML로 변환"""
    html = markdown.markdown(
        md_content,
        extensions=[
            'fenced_code',  # 코드 블록
            'tables',       # 테이블
            'nl2br',        # 줄바꿈
            'codehilite',   # 코드 하이라이팅
        ]
    )

    # 네이버 블로그 스타일 적용
    html = apply_naver_blog_styles(html)

    return html

def apply_naver_blog_styles(html: str) -> str:
    """네이버 블로그 스타일 적용"""
    # 코드 블록 스타일
    html = html.replace(
        '<pre>',
        '<pre style="background:#f5f5f5;padding:10px;border-radius:5px;">'
    )
    return html
```

**Day 14: 스마트에디터에 HTML 삽입**
```python
async def insert_html_to_editor(page, html_content):
    """스마트에디터에 HTML 삽입"""
    frame = page.frame_locator("iframe.se-iframe")

    # HTML 모드로 전환 (필요 시)
    await page.click("button[aria-label='HTML']")

    # HTML 삽입
    await frame.locator(".se-content").evaluate(
        f"el => el.innerHTML = `{html_content}`"
    )
```

#### 2.3 세션 관리 개선 (Day 15)

```python
# 파일: src/naver_blog_mcp/services/session_manager.py

class SessionManager:
    def __init__(self, storage_path="playwright-state/auth.json"):
        self.storage_path = storage_path
        self.last_login_time = None

    async def is_session_valid(self, context) -> bool:
        """세션 유효성 검사"""
        # 1. 파일 존재 여부
        if not os.path.exists(self.storage_path):
            return False

        # 2. 24시간 이내 로그인 확인
        if self.last_login_time:
            elapsed = datetime.now() - self.last_login_time
            if elapsed.total_seconds() > 86400:  # 24시간
                return False

        # 3. 실제 네이버 페이지 접속 테스트
        page = await context.new_page()
        await page.goto("https://blog.naver.com")

        # 로그인 상태 확인
        is_logged_in = await page.locator(".my_nick").count() > 0
        await page.close()

        return is_logged_in

    async def refresh_session_if_needed(self, browser):
        """필요 시 세션 갱신"""
        context = await browser.new_context(
            storage_state=self.storage_path if os.path.exists(self.storage_path) else None
        )

        if not await self.is_session_valid(context):
            # 재로그인
            await self.login(context)
            self.last_login_time = datetime.now()

        return context
```

#### 2.4 자동화 감지 우회 (Day 16)

```python
# 파일: src/naver_blog_mcp/utils/stealth.py

async def launch_stealth_browser(playwright):
    """자동화 감지 우회 브라우저 실행"""
    browser = await playwright.chromium.launch(
        headless=False,  # 헤드리스 감지 회피
        args=[
            '--disable-blink-features=AutomationControlled',
            '--disable-dev-shm-usage',
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-web-security',
        ]
    )

    context = await browser.new_context(
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        viewport={'width': 1920, 'height': 1080},
        locale='ko-KR',
        timezone_id='Asia/Seoul',
    )

    # navigator.webdriver 속성 제거
    await context.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });
    """)

    return browser, context

테스트:
- 네이버 자동화 감지 테스트 페이지 접속
- navigator.webdriver 값 확인
- 연속 작업 시 차단 여부 확인
```

#### 2.5 성능 최적화 (Day 17)

```python
# 브라우저 재사용

class BrowserPool:
    """브라우저 인스턴스 풀"""
    def __init__(self):
        self._browser = None
        self._contexts = {}

    async def get_browser(self):
        """싱글톤 브라우저"""
        if self._browser is None:
            playwright = await async_playwright().start()
            self._browser, _ = await launch_stealth_browser(playwright)
        return self._browser

    async def get_context(self, user_id: str):
        """사용자별 독립적인 컨텍스트"""
        if user_id not in self._contexts:
            browser = await self.get_browser()
            self._contexts[user_id] = await browser.new_context(
                storage_state=f"playwright-state/auth_{user_id}.json"
            )
        return self._contexts[user_id]

# 네트워크 최적화
async def optimize_page_load(page):
    """불필요한 리소스 차단"""
    await page.route("**/*.{png,jpg,jpeg,gif}", lambda route: route.abort())
    await page.route("**/analytics/**", lambda route: route.abort())
    await page.route("**/advertisement/**", lambda route: route.abort())
```

### Phase 3: 테스트, 문서화, 배포 (Week 4)

#### 3.1 종합 테스트 (Day 18-19)

**Day 18: 단위 테스트**
```python
# tests/unit/test_post_manager.py

import pytest
from playwright.async_api import async_playwright

@pytest.fixture
async def browser():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        yield browser
        await browser.close()

@pytest.mark.asyncio
async def test_create_post(browser):
    """글 작성 테스트"""
    context = await browser.new_context(
        storage_state="tests/fixtures/auth.json"
    )
    page = await context.new_page()

    result = await create_post(
        page,
        title="테스트 제목",
        content="테스트 내용"
    )

    assert result["success"] == True
    assert "blog.naver.com" in result["post_url"]

@pytest.mark.asyncio
async def test_create_post_with_images(browser):
    """이미지 포함 글 작성 테스트"""
    # ...

테스트 커버리지 목표: 80% 이상
```

**Day 19: 통합 테스트 및 E2E 테스트**
```python
# tests/integration/test_mcp_server.py

@pytest.mark.asyncio
async def test_full_workflow():
    """전체 워크플로우 테스트"""
    # 1. MCP 서버 시작
    server = NaverBlogMCPServer()
    await server.start()

    # 2. 글 작성 Tool 호출
    result = await server.call_tool(
        "naver_blog_create_post",
        {
            "title": "통합 테스트",
            "content": "# 제목\n\n내용",
            "tags": ["테스트", "MCP"]
        }
    )

    # 3. 실제 블로그 확인
    assert result["success"]
    post_url = result["post_url"]

    # 4. 글 삭제
    delete_result = await server.call_tool(
        "naver_blog_delete_post",
        {"post_url": post_url}
    )

    assert delete_result["success"]
```

#### 3.2 문서 작성 (Day 20-21)

```markdown
작성할 문서:

1. README.md
   - 프로젝트 소개
   - 빠른 시작 가이드
   - Playwright 설치 방법
   - 환경 변수 설정
   - MCP 서버 실행

2. docs/api-reference.md
   - 모든 Tool 상세 설명
   - Playwright 코드 예제
   - 입력/출력 스키마

3. docs/playwright-guide.md (신규)
   - Playwright 기본 사용법
   - 네이버 블로그 DOM 구조
   - 셀렉터 업데이트 방법
   - 디버깅 팁 (Inspector, Trace Viewer)

4. docs/troubleshooting.md
   - CAPTCHA 발생 시 대처
   - 로그인 실패 해결
   - UI 변경 시 대응
   - 성능 문제 해결

5. CHANGELOG.md
   - 버전별 변경사항
```

#### 3.3 코드 품질 개선 (Day 22)

```bash
작업 내용:

1. 타입 힌팅 완성
# 모든 함수에 타입 힌트 추가
async def create_post(
    page: Page,
    title: str,
    content: str,
    category: Optional[str] = None,
    tags: Optional[List[str]] = None
) -> Dict[str, Any]:
    ...

2. 독스트링 추가
async def create_post(...):
    """
    네이버 블로그에 글을 작성합니다.

    Args:
        page: Playwright Page 객체
        title: 글 제목
        content: 글 내용 (Markdown 또는 HTML)
        category: 카테고리명 (선택)
        tags: 태그 목록 (선택)

    Returns:
        작성 결과 딕셔너리
        {
            "success": bool,
            "post_url": str,
            "message": str
        }

    Raises:
        LoginFailedError: 로그인 실패
        TimeoutError: 작업 시간 초과
    """

3. 린팅 및 포매팅
uv run black src/ tests/
uv run ruff check src/ tests/ --fix
uv run mypy src/

기준:
□ Black 100% 준수
□ Ruff 경고 0개
□ Mypy strict 모드 통과
```

#### 3.4 배포 준비 (Day 23-24)

```bash
# Day 23: 패키지 빌드 및 설정

1. pyproject.toml 최종 점검
[project]
name = "naver-blog-mcp"
version = "0.1.0"
description = "Naver Blog MCP server using Playwright automation"
readme = "README.md"
requires-python = ">=3.13"
dependencies = [
    "mcp[cli]>=1.20.0",
    "playwright>=1.40.0",
    "pydantic>=2.5.0",
    "python-dotenv>=1.0.0",
    "tenacity>=8.2.0",
    "aiofiles>=23.0.0",
    "markdown>=3.5.0",
]

[project.scripts]
naver-blog-mcp = "naver_blog_mcp.server:main"

2. .gitignore 업데이트
playwright-state/
*.pyc
__pycache__/
.env
*.zip
traces/
screenshots/

3. LICENSE 파일 추가
MIT License

4. 빌드 테스트
uv build
```

**Day 24: Claude Desktop 통합 테스트**
```json
# Claude Desktop 설정 파일

{
  "mcpServers": {
    "naver-blog": {
      "command": "uv",
      "args": [
        "--directory",
        "C:/workdir/space-cap/naver-blog-mcp",
        "run",
        "naver-blog-mcp"
      ],
      "env": {
        "NAVER_BLOG_ID": "your_id",
        "NAVER_BLOG_PASSWORD": "your_password",
        "HEADLESS": "true"
      }
    }
  }
}

테스트:
1. Claude Desktop 재시작
2. MCP 서버 연결 확인
3. 글 작성 요청
4. 실제 네이버 블로그에 게시 확인
```

#### 3.5 최종 검증 (Day 25)

```bash
검증 항목:

□ 기능 검증
  □ 글 작성 (텍스트만)
  □ 글 작성 (이미지 포함)
  □ 글 작성 (Markdown)
  □ 글 수정
  □ 글 삭제
  □ 카테고리 조회
  □ 최근 글 목록 조회

□ 비기능 검증
  □ 세션 유지 (재시작 후에도)
  □ 에러 처리 (재시도)
  □ 성능 (3초 이내 응답)
  □ 안정성 (10회 연속 작업)

□ 문서 검증
  □ README 따라하기 가능
  □ API 문서 정확성
  □ 예제 코드 동작 확인

□ 배포 검증
  □ 깨끗한 환경 설치 테스트
  □ Claude Desktop 통합 테스트
  □ Windows/macOS/Linux 확인
```

## 4. 개발 워크플로우

### 4.1 일일 개발 루틴

```bash
# 1. 작업 시작
git checkout -b feature/task-name
uv sync

# 2. Playwright 디버그 모드 개발
HEADLESS=false SLOW_MO=100 uv run python -m naver_blog_mcp.server

# 3. 테스트
uv run pytest tests/ -v

# 4. Playwright Trace 확인 (에러 시)
playwright show-trace traces/latest.zip

# 5. 린팅 및 포매팅
uv run black src/ tests/
uv run ruff check src/ tests/

# 6. 커밋
git add .
git commit -m "feat: add feature"
```

### 4.2 Playwright 디버깅 팁

```python
# 1. Playwright Inspector 사용
PWDEBUG=1 uv run python script.py

# 2. 느린 모드 (액션 사이 딜레이)
browser = await playwright.chromium.launch(slow_mo=500)

# 3. 스크린샷 + Trace 동시 사용
await page.screenshot(path="debug.png")
await context.tracing.start(screenshots=True)

# 4. 콘솔 로그 확인
page.on("console", lambda msg: print(f"Browser: {msg.text}"))

# 5. 네트워크 모니터링
page.on("request", lambda req: print(f"Request: {req.url}"))
page.on("response", lambda res: print(f"Response: {res.url} {res.status}"))
```

## 5. 구현 우선순위

### 높음 (Must Have) - Week 1-2
1. ✅ Playwright 로그인 자동화
2. ✅ 세션 저장/복원
3. ✅ 글 작성 (제목, 내용)
4. ✅ 글 삭제
5. ✅ MCP Tool 등록
6. ✅ 기본 에러 처리

### 중간 (Should Have) - Week 3
1. ✅ 이미지 업로드
2. ✅ 글 수정
3. ✅ Markdown 지원
4. ✅ 카테고리/태그
5. ✅ 재시도 로직
6. ✅ 자동화 감지 우회

### 낮음 (Nice to Have) - 선택사항
1. ⬜ 임시저장
2. ⬜ 예약 발행 (cron)
3. ⬜ 통계 조회 (크롤링)
4. ⬜ 댓글 관리
5. ⬜ 멀티 계정

## 6. 리스크 관리

### 6.1 기술적 리스크

#### R1: 네이버 UI 변경
- **확률**: 높음
- **영향**: 높음
- **대응**:
  - 셀렉터 중앙 관리 (selectors.py)
  - 대체 셀렉터 정의
  - 버전별 셀렉터 분리
  - 자동 알림 시스템

#### R2: CAPTCHA 발생
- **확률**: 중간
- **영향**: 높음
- **대응**:
  - Stealth 모드 활성화
  - 적절한 딜레이 추가 (인간적인 속도)
  - CAPTCHA 감지 시 사용자 알림
  - 헤드리스 모드 대신 헤드 모드 사용

#### R3: Playwright 버전 호환성
- **확률**: 낮음
- **영향**: 중간
- **대응**:
  - 버전 고정 (`playwright==1.40.0`)
  - 정기적인 업데이트 테스트
  - 변경사항 문서화

### 6.2 일정 리스크

#### R4: Playwright 학습 곡선
- **확률**: 낮음 (API가 간단함)
- **영향**: 낮음
- **대응**:
  - 공식 문서 활용
  - 예제 코드 참고
  - Inspector로 디버깅

## 7. 성공 지표

### 7.1 기능적 지표
- ✅ 모든 필수 Tool 구현 완료
- ✅ 네이버 블로그에 실제 포스팅 성공
- ✅ MCP 프로토콜 표준 준수
- ✅ Claude Desktop 정상 작동

### 7.2 기술적 지표
- ✅ 테스트 커버리지 > 80%
- ✅ 글 작성 성공률 > 95%
- ✅ 평균 응답 시간 < 5초
- ✅ 타입 체킹 에러 0개

### 7.3 안정성 지표
- ✅ 10회 연속 작업 성공
- ✅ 세션 24시간 유지
- ✅ 에러 발생 시 자동 복구
- ✅ CAPTCHA 발생률 < 5%

### 7.4 사용성 지표
- ✅ 설치 5분 이내 완료
- ✅ README 따라 첫 포스팅 성공
- ✅ 명확한 에러 메시지
- ✅ 디버깅 도구 제공 (Trace Viewer)

## 8. 개발 환경 설정

### 8.1 필수 도구

```bash
# Python 3.13 설치
# Windows/macOS/Linux 각 OS별 방법

# uv 설치
curl -LsSf https://astral.sh/uv/install.sh | sh

# Git
# 각 OS별 공식 방법
```

### 8.2 프로젝트 설정

```bash
# 1. 저장소 클론
git clone https://github.com/your-username/naver-blog-mcp.git
cd naver-blog-mcp

# 2. 가상환경 및 의존성
uv sync

# 3. Playwright 브라우저 설치 ⭐ 중요!
uv run playwright install chromium

# 4. 환경 변수 설정
cp .env.example .env
# .env 파일 편집

# 5. 첫 실행 (디버그 모드)
HEADLESS=false uv run python -m naver_blog_mcp.server
```

### 8.3 VS Code 설정 (권장)

```json
// .vscode/settings.json
{
  "python.defaultInterpreterPath": ".venv/bin/python",
  "python.testing.pytestEnabled": true,
  "python.testing.pytestArgs": ["tests"],
  "[python]": {
    "editor.defaultFormatter": "ms-python.black-formatter",
    "editor.formatOnSave": true
  },
  "playwright.env": {
    "HEADLESS": "false",
    "SLOW_MO": "100"
  }
}
```

### 8.4 Playwright Extension (선택사항)

```bash
# VS Code에서 Playwright Test for VSCode 확장 설치
# 테스트 실행 및 디버깅이 GUI로 가능
```

## 9. 체크리스트

### Phase 1 체크리스트 (Week 1-2)
- [ ] Playwright 설치 및 브라우저 다운로드
- [ ] 네이버 로그인 자동화 성공
- [ ] 세션 저장/복원 구현
- [ ] 글쓰기 페이지 자동화 (iframe 처리)
- [ ] MCP 서버 기본 구조
- [ ] `naver_blog_create_post` Tool 구현
- [ ] `naver_blog_delete_post` Tool 구현
- [ ] 에러 처리 및 재시도 로직
- [ ] 기본 테스트 작성

### Phase 2 체크리스트 (Week 3)
- [ ] 이미지 업로드 구현
- [ ] Markdown -> HTML 변환
- [ ] 세션 관리 개선 (24시간 자동 갱신)
- [ ] 자동화 감지 우회 (Stealth 모드)
- [ ] 성능 최적화 (브라우저 재사용)
- [ ] Trace Viewer 디버깅 활용
- [ ] 모든 기능 통합 테스트

### Phase 3 체크리스트 (Week 4)
- [ ] 단위 테스트 커버리지 80%
- [ ] 통합 테스트 완료
- [ ] README.md 작성
- [ ] API 문서 작성
- [ ] Playwright 가이드 작성
- [ ] 트러블슈팅 문서 작성
- [ ] 코드 품질 기준 충족
- [ ] Claude Desktop 통합 테스트
- [ ] 최종 검증 완료

### 릴리스 체크리스트
- [ ] 버전 번호 결정 (v0.1.0)
- [ ] CHANGELOG 작성
- [ ] LICENSE 파일 확인
- [ ] Git 태그 생성
- [ ] GitHub Release 생성
- [ ] (선택) PyPI 배포

## 10. 참고 자료

### 10.1 Playwright 공식 문서
- [Playwright Python 문서](https://playwright.dev/python/)
- [API Reference](https://playwright.dev/python/docs/api/class-playwright)
- [Best Practices](https://playwright.dev/python/docs/best-practices)
- [Debugging Guide](https://playwright.dev/python/docs/debug)
- [Trace Viewer](https://playwright.dev/python/docs/trace-viewer)

### 10.2 네이버 블로그 관련
- [스마트에디터 ONE 소개](https://smartstudio.tech/)
- [네이버 블로그 고객센터](https://help.naver.com/service/5628/)

### 10.3 MCP 문서
- [MCP Specification](https://modelcontextprotocol.io/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)

### 10.4 커뮤니티 리소스
- [Playwright Discord](https://discord.gg/playwright)
- [Stack Overflow - Playwright](https://stackoverflow.com/questions/tagged/playwright)

## 11. 마무리

이 구현 계획서는 Playwright를 활용한 네이버 블로그 MCP 서버 구축의 로드맵을 제시합니다.

### 핵심 포인트
1. **Playwright 선택 이유**: 비동기 네이티브, 자동 대기, 강력한 디버깅
2. **단계별 접근**: 로그인 → 글쓰기 → MCP 통합 → 고급 기능
3. **안정성 우선**: 에러 처리, 재시도, 세션 관리
4. **디버깅 도구**: Inspector, Trace Viewer, 스크린샷
5. **문서화**: Playwright 가이드, 트러블슈팅

### 예상 결과
- 안정적인 네이버 블로그 자동화
- Claude와의 자연스러운 통합
- 유지보수 가능한 코드베이스
- 명확한 문서 및 디버깅 도구

### 다음 단계
Phase 1부터 시작하여 단계별로 구현하면 됩니다! 🚀
