# 네이버 블로그 MCP 서버 아키텍처 설계서

## 1. 개요

### 1.1 프로젝트 목적
본 프로젝트는 Model Context Protocol(MCP)을 활용하여 네이버 블로그에 글을 작성할 수 있는 서버를 구축하는 것을 목표로 합니다. AI 어시스턴트가 MCP를 통해 네이버 블로그와 상호작용할 수 있도록 표준화된 인터페이스를 제공합니다.

### 1.2 시스템 개요
- **프로토콜**: Model Context Protocol (MCP)
- **통신 방식**: JSON-RPC 2.0 over stdio
- **자동화 방식**: Playwright (웹 브라우저 자동화)
- **언어**: Python 3.13
- **주요 라이브러리**: `mcp[cli]` v1.20.0+, `playwright` v1.40.0+

## 2. 네이버 블로그 API 현황 및 대안

### 2.1 공식 API 종료

#### 종료된 API
- **종료일**: 2020년 5월 6일
- **종료 대상**:
  - REST 기반 글쓰기 API
  - MetaWeblog XML-RPC API
- **종료 사유**: 광고성 글 대량 작성 악용 방지
- **현재 상태**: ❌ 복구 계획 없음, 영구 종료

#### 현재 사용 가능한 네이버 API (읽기 전용)
- **검색 API**: 블로그 글 검색/조회만 가능
- **로그인 API**: OAuth 인증만 제공

### 2.2 선택된 해결 방안: Playwright 웹 자동화

#### 왜 Playwright인가?

##### 비교: Selenium vs Playwright

| 항목 | Playwright | Selenium | 선택 |
|------|-----------|----------|------|
| **성능** | 30% 더 빠름 (WebSocket) | 느림 (HTTP) | ✅ Playwright |
| **자동 대기** | 내장 (Auto-wait) | 수동 설정 필요 | ✅ Playwright |
| **비동기 지원** | 네이티브 async/await | 제한적 | ✅ Playwright |
| **MCP 호환성** | 완벽 (비동기 구조) | 보통 | ✅ Playwright |
| **디버깅** | Inspector, Trace Viewer | 기본적 로깅 | ✅ Playwright |
| **브라우저 관리** | 자동 설치/업데이트 | 수동 ChromeDriver 관리 | ✅ Playwright |
| **안정성** | 높음 (자동 재시도) | 중간 (수동 처리) | ✅ Playwright |
| **학습 곡선** | 낮음 (간단한 API) | 높음 | ✅ Playwright |
| **커뮤니티** | 빠르게 성장 중 | 성숙함 | Selenium |
| **레거시 지원** | 제한적 (IE 미지원) | 광범위 | Selenium |

**결론**: Playwright가 모든 주요 측면에서 우월

#### Playwright의 핵심 장점

##### 1. 자동 대기 메커니즘
```python
# Selenium - 수동 대기 필요
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

wait = WebDriverWait(driver, 10)
element = wait.until(EC.element_to_be_clickable((By.ID, "title")))
element.send_keys("제목")

# Playwright - 자동 대기 (간결함)
await page.fill("#title", "제목")  # 자동으로 요소가 준비될 때까지 대기
```

##### 2. 비동기 네이티브 지원 (MCP와 완벽한 궁합)
```python
# MCP 서버는 비동기 구조
@server.tool()
async def naver_blog_create_post(title: str, content: str):
    async with async_playwright() as p:
        # 자연스러운 비동기 플로우
        browser = await p.chromium.launch()
        page = await browser.new_page()
        # ...
```

##### 3. 컨텍스트 격리 (여러 계정 동시 관리)
```python
# 각각 다른 네이버 계정으로 동시 포스팅 가능
context1 = await browser.new_context()  # 계정 1
context2 = await browser.new_context()  # 계정 2
```

##### 4. 강력한 디버깅
- **Playwright Inspector**: 실시간 단계별 실행
- **Trace Viewer**: 모든 액션의 스크린샷/네트워크 기록
- **자동 스크린샷/비디오**: 에러 발생 시 자동 캡처

##### 5. 네이버 자동화 감지 우회
```python
# Stealth 모드 설정
browser = await p.chromium.launch(
    headless=False,
    args=[
        '--disable-blink-features=AutomationControlled',
        '--disable-dev-shm-usage'
    ]
)
# Selenium보다 감지 회피가 용이함
```

### 2.3 네이버 블로그 UI 구조

#### 스마트에디터 ONE
- **현재 버전**: 스마트에디터 ONE (2018년 출시)
- **기술**: contenteditable 기반 WYSIWYG 에디터
- **구조**:
  - 상단 툴바: 텍스트 서식, 미디어 삽입
  - 본문 영역: 컴포넌트 기반 (텍스트, 이미지, 동영상 등)
  - 하단: 카테고리, 태그, 발행 설정

#### 주요 URL 패턴
```
로그인: https://nid.naver.com/nidlogin.login
블로그 메인: https://blog.naver.com/{user_id}
글쓰기: https://blog.naver.com/PostWriteForm.naver
글수정: https://blog.naver.com/PostUpdateForm.naver?blogId={user_id}&logNo={post_id}
```

#### 주요 DOM 셀렉터 (Playwright용)
```python
SELECTORS = {
    # 로그인
    "login_id": "#id",
    "login_pw": "#pw",
    "login_btn": ".btn_login",

    # 글쓰기
    "title_input": "input[placeholder*='제목']",
    "content_frame": "iframe.se-iframe",
    "content_body": ".se-component-content",
    "category_select": ".blog2_series",
    "tag_input": "input[placeholder*='태그']",
    "publish_btn": "button:has-text('발행')",
}
```

## 3. MCP 서버 아키텍처

### 3.1 시스템 아키텍처

```
┌─────────────────────────────────────────────────────────────┐
│                        AI Assistant                          │
│                    (Claude, ChatGPT, etc.)                   │
└────────────────────────┬────────────────────────────────────┘
                         │ MCP Protocol (JSON-RPC 2.0)
                         │ stdio/transport
┌────────────────────────▼────────────────────────────────────┐
│                   MCP Server (Python)                        │
│  ┌───────────────────────────────────────────────────────┐  │
│  │              MCP Protocol Handler                     │  │
│  │  - Tool Discovery                                     │  │
│  │  - Tool Execution                                     │  │
│  │  - Resource Management                                │  │
│  └───────────────────────┬───────────────────────────────┘  │
│  ┌───────────────────────▼───────────────────────────────┐  │
│  │            Business Logic Layer                       │  │
│  │  - Post Manager                                       │  │
│  │  - Category Manager                                   │  │
│  │  - Media Manager                                      │  │
│  │  - Session Manager (인증/세션)                        │  │
│  └───────────────────────┬───────────────────────────────┘  │
│  ┌───────────────────────▼───────────────────────────────┐  │
│  │       Playwright Automation Layer                     │  │
│  │  - Browser Manager                                    │  │
│  │  - Page Controller                                    │  │
│  │  - Element Locator                                    │  │
│  │  - Action Executor                                    │  │
│  │  - Error Handler & Retry Logic                        │  │
│  └───────────────────────┬───────────────────────────────┘  │
└────────────────────────┬─────────────────────────────────────┘
                         │ Browser Automation
┌────────────────────────▼────────────────────────────────────┐
│              Chromium Browser (Playwright)                   │
│           https://blog.naver.com (스마트에디터 ONE)          │
└──────────────────────────────────────────────────────────────┘
```

### 3.2 레이어별 책임

#### 3.2.1 MCP Protocol Handler
- **책임**: MCP 프로토콜 메시지 처리
- **기능**:
  - Tool 목록 제공 (`tools/list`)
  - Tool 실행 요청 처리 (`tools/call`)
  - Resource 목록 제공 (`resources/list`)
  - Resource 조회 (`resources/read`)
  - 초기화 및 연결 관리

#### 3.2.2 Business Logic Layer
- **책임**: 비즈니스 로직 및 데이터 변환
- **구성요소**:
  - **PostManager**: 포스트 작성, 조회, 삭제, 수정 로직
  - **CategoryManager**: 카테고리 관리
  - **MediaManager**: 이미지/미디어 업로드 처리
  - **SessionManager**: 로그인 세션 관리, 인증 상태 유지

#### 3.2.3 Playwright Automation Layer
- **책임**: 브라우저 자동화 실행
- **구성요소**:
  - **BrowserManager**: 브라우저 인스턴스 생명주기 관리
  - **PageController**: 페이지 네비게이션 및 상태 관리
  - **ElementLocator**: DOM 요소 찾기 (셀렉터 관리)
  - **ActionExecutor**: 클릭, 입력, 스크롤 등 액션 실행
  - **ErrorHandler**: 에러 감지, 재시도, 복구

### 3.3 디렉토리 구조

```
naver-blog-mcp/
├── src/
│   ├── naver_blog_mcp/
│   │   ├── __init__.py
│   │   ├── server.py              # MCP 서버 메인 엔트리포인트
│   │   ├── config.py              # 설정 관리
│   │   │
│   │   ├── mcp/                   # MCP 프로토콜 레이어
│   │   │   ├── __init__.py
│   │   │   ├── handlers.py        # MCP 메시지 핸들러
│   │   │   └── tools.py           # MCP Tool 정의
│   │   │
│   │   ├── services/              # 비즈니스 로직 레이어
│   │   │   ├── __init__.py
│   │   │   ├── post_manager.py   # 포스트 관리
│   │   │   ├── category_manager.py
│   │   │   ├── media_manager.py
│   │   │   └── session_manager.py # 세션/인증 관리
│   │   │
│   │   ├── automation/            # Playwright 자동화 레이어
│   │   │   ├── __init__.py
│   │   │   ├── browser_manager.py # 브라우저 관리
│   │   │   ├── page_controller.py # 페이지 컨트롤
│   │   │   ├── selectors.py       # DOM 셀렉터 정의
│   │   │   ├── actions.py         # 액션 실행기
│   │   │   └── error_handler.py   # 에러 처리
│   │   │
│   │   ├── models/                # 데이터 모델
│   │   │   ├── __init__.py
│   │   │   ├── post.py
│   │   │   ├── category.py
│   │   │   ├── media.py
│   │   │   └── session.py
│   │   │
│   │   └── utils/                 # 유틸리티
│   │       ├── __init__.py
│   │       ├── validators.py
│   │       ├── converters.py      # Markdown -> HTML
│   │       └── stealth.py         # 자동화 감지 우회
│   │
├── tests/                         # 테스트
│   ├── unit/
│   ├── integration/
│   └── fixtures/
│
├── docs/                          # 문서
│   ├── architecture.md
│   ├── api-reference.md
│   └── development-guide.md
│
├── playwright-state/              # 브라우저 상태 저장
│   └── auth.json                  # 로그인 세션 저장
│
├── main.py                        # CLI 엔트리포인트
├── pyproject.toml
└── README.md
```

## 4. MCP Tools 정의

### 4.1 Tool 목록

#### 4.1.1 `naver_blog_create_post`
새로운 블로그 글을 작성합니다.

**Input Schema**:
```json
{
  "type": "object",
  "properties": {
    "title": {
      "type": "string",
      "description": "글 제목"
    },
    "content": {
      "type": "string",
      "description": "글 내용 (Markdown 또는 HTML)"
    },
    "category": {
      "type": "string",
      "description": "카테고리명 (선택사항)"
    },
    "tags": {
      "type": "array",
      "items": {"type": "string"},
      "description": "태그 목록"
    },
    "publish": {
      "type": "boolean",
      "description": "즉시 발행 여부 (true: 발행, false: 임시저장)",
      "default": true
    }
  },
  "required": ["title", "content"]
}
```

**Output**:
```json
{
  "success": true,
  "post_url": "https://blog.naver.com/userid/223123456789",
  "post_id": "223123456789",
  "message": "글이 성공적으로 발행되었습니다.",
  "screenshot": "base64_encoded_image (선택사항)"
}
```

**Playwright 구현 플로우**:
```python
async def create_post(page, title, content, category, tags, publish):
    # 1. 글쓰기 페이지 이동
    await page.goto("https://blog.naver.com/PostWriteForm.naver")

    # 2. 제목 입력 (자동 대기)
    await page.fill("input[placeholder*='제목']", title)

    # 3. 본문 입력 (iframe 처리)
    content_frame = page.frame_locator("iframe.se-iframe")
    await content_frame.locator(".se-component-content").fill(content)

    # 4. 카테고리 선택
    if category:
        await page.select_option(".blog2_series", label=category)

    # 5. 태그 입력
    if tags:
        for tag in tags:
            await page.fill("input[placeholder*='태그']", tag)
            await page.press("input[placeholder*='태그']", "Enter")

    # 6. 발행/임시저장
    if publish:
        await page.click("button:has-text('발행')")
    else:
        await page.click("button:has-text('임시저장')")

    # 7. URL 추출
    await page.wait_for_url("**/PostView.naver*")
    post_url = page.url

    return post_url
```

#### 4.1.2 `naver_blog_delete_post`
기존 블로그 글을 삭제합니다.

**Input Schema**:
```json
{
  "type": "object",
  "properties": {
    "post_url": {
      "type": "string",
      "description": "삭제할 글의 URL"
    }
  },
  "required": ["post_url"]
}
```

#### 4.1.3 `naver_blog_update_post`
기존 글을 수정합니다.

**Input Schema**:
```json
{
  "type": "object",
  "properties": {
    "post_url": {
      "type": "string",
      "description": "수정할 글의 URL"
    },
    "title": {
      "type": "string",
      "description": "새로운 제목"
    },
    "content": {
      "type": "string",
      "description": "새로운 내용"
    },
    "category": {
      "type": "string",
      "description": "카테고리명"
    },
    "tags": {
      "type": "array",
      "items": {"type": "string"},
      "description": "태그 목록"
    }
  },
  "required": ["post_url", "title", "content"]
}
```

#### 4.1.4 `naver_blog_list_categories`
블로그의 카테고리 목록을 조회합니다.

**Output**:
```json
{
  "categories": [
    {"name": "일상", "post_count": 15},
    {"name": "기술", "post_count": 23}
  ]
}
```

#### 4.1.5 `naver_blog_get_recent_posts`
최근 작성한 글 목록을 조회합니다.

**Input Schema**:
```json
{
  "type": "object",
  "properties": {
    "count": {
      "type": "integer",
      "description": "조회할 글 개수",
      "default": 10,
      "minimum": 1,
      "maximum": 50
    }
  }
}
```

#### 4.1.6 `naver_blog_upload_image`
이미지를 업로드하고 URL을 반환합니다.

**Input Schema**:
```json
{
  "type": "object",
  "properties": {
    "image_path": {
      "type": "string",
      "description": "로컬 이미지 파일 경로"
    },
    "alt_text": {
      "type": "string",
      "description": "이미지 설명 (선택사항)"
    }
  },
  "required": ["image_path"]
}
```

## 5. 데이터 모델

### 5.1 Post Model
```python
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List

@dataclass
class Post:
    title: str
    content: str
    category: Optional[str] = None
    tags: List[str] = None
    publish: bool = True
    post_url: Optional[str] = None
    post_id: Optional[str] = None
    created_at: Optional[datetime] = None
    screenshot_path: Optional[str] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []
```

### 5.2 Session Model
```python
@dataclass
class NaverSession:
    user_id: str
    password: str
    is_authenticated: bool = False
    storage_state_path: Optional[str] = None
    last_login: Optional[datetime] = None

    def is_valid(self) -> bool:
        """세션 유효성 검사"""
        if not self.is_authenticated:
            return False
        if not self.last_login:
            return False
        # 24시간 이내 로그인만 유효
        return (datetime.now() - self.last_login).hours < 24
```

## 6. 인증 및 세션 관리

### 6.1 Playwright 세션 저장

```python
# 로그인 후 세션 저장
async def login_and_save_session(page, user_id, password):
    # 로그인 수행
    await page.goto("https://nid.naver.com/nidlogin.login")
    await page.fill("#id", user_id)
    await page.fill("#pw", password)
    await page.click(".btn_login")

    # 로그인 완료 대기
    await page.wait_for_url("**/blog.naver.com/**")

    # 세션 저장 (쿠키, localStorage 등)
    storage_state = await page.context.storage_state(
        path="playwright-state/auth.json"
    )

    return storage_state

# 저장된 세션으로 재사용
async def reuse_session(browser):
    context = await browser.new_context(
        storage_state="playwright-state/auth.json"
    )
    page = await context.new_page()
    return page
```

### 6.2 환경 변수 관리

```bash
# .env
NAVER_BLOG_ID=your_naver_id
NAVER_BLOG_PASSWORD=your_password

# 선택사항
HEADLESS=false  # 디버깅용
SLOW_MO=100     # 액션 속도 조절 (ms)
```

### 6.3 보안 고려사항

1. **비밀번호 저장**
   - 환경 변수 또는 안전한 설정 파일
   - Git에 커밋하지 않음 (.gitignore)
   - 가능하면 시스템 키체인 활용

2. **세션 관리**
   - `playwright-state/auth.json`을 `.gitignore`에 추가
   - 주기적 재로그인 (24시간마다)
   - 세션 만료 감지 및 자동 재인증

3. **자동화 감지 우회**
   ```python
   # Stealth 설정
   browser = await playwright.chromium.launch(
       headless=False,  # 헤드리스 감지 회피
       args=[
           '--disable-blink-features=AutomationControlled',
           '--disable-dev-shm-usage',
           '--no-sandbox',
       ]
   )

   # User-Agent 설정
   context = await browser.new_context(
       user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) ...',
       viewport={'width': 1920, 'height': 1080}
   )
   ```

## 7. 에러 처리 전략

### 7.1 에러 분류

```python
class NaverBlogError(Exception):
    """네이버 블로그 기본 에러"""
    pass

class LoginFailedError(NaverBlogError):
    """로그인 실패"""
    pass

class PostNotFoundError(NaverBlogError):
    """글을 찾을 수 없음"""
    pass

class ElementNotFoundError(NaverBlogError):
    """페이지 요소를 찾을 수 없음"""
    pass

class TimeoutError(NaverBlogError):
    """작업 시간 초과"""
    pass

class CaptchaDetectedError(NaverBlogError):
    """CAPTCHA 감지됨"""
    pass
```

### 7.2 Playwright 자동 재시도

```python
# Playwright의 내장 재시도 활용
await page.click(
    "button:has-text('발행')",
    timeout=30000,  # 30초 대기
    # 자동으로 요소가 보이고 클릭 가능할 때까지 재시도
)

# 커스텀 재시도 로직
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
async def post_with_retry(page, post_data):
    try:
        return await create_post(page, **post_data)
    except TimeoutError:
        # 페이지 새로고침 후 재시도
        await page.reload()
        raise
```

### 7.3 스크린샷 기반 디버깅

```python
async def create_post_with_debug(page, title, content):
    try:
        await page.fill("#title", title)
        # 각 단계마다 스크린샷
        await page.screenshot(path=f"debug/step1_title.png")

        await fill_content(page, content)
        await page.screenshot(path=f"debug/step2_content.png")

        await page.click("button:has-text('발행')")
        await page.screenshot(path=f"debug/step3_publish.png")

    except Exception as e:
        # 에러 발생 시 전체 페이지 스크린샷
        await page.screenshot(path=f"debug/error_{datetime.now()}.png")
        raise
```

## 8. 성능 최적화

### 8.1 브라우저 재사용

```python
class BrowserManager:
    def __init__(self):
        self._browser = None
        self._context = None

    async def get_browser(self):
        """싱글톤 브라우저 인스턴스"""
        if self._browser is None:
            playwright = await async_playwright().start()
            self._browser = await playwright.chromium.launch()
        return self._browser

    async def get_context(self):
        """재사용 가능한 컨텍스트"""
        if self._context is None:
            browser = await self.get_browser()
            self._context = await browser.new_context(
                storage_state="playwright-state/auth.json"
            )
        return self._context
```

### 8.2 병렬 처리

```python
# 여러 글 동시 작성 (독립적인 컨텍스트 사용)
async def create_posts_parallel(posts: List[Post]):
    browser = await get_browser()

    tasks = []
    for post in posts:
        context = await browser.new_context()
        page = await context.new_page()
        task = create_post(page, post)
        tasks.append(task)

    results = await asyncio.gather(*tasks)
    return results
```

### 8.3 네트워크 최적화

```python
# 불필요한 리소스 차단 (속도 향상)
async def block_unnecessary_resources(page):
    await page.route("**/*.{png,jpg,jpeg,gif,svg,woff,woff2}",
                     lambda route: route.abort())
    await page.route("**/analytics/**",
                     lambda route: route.abort())
```

## 9. 테스트 전략

### 9.1 Playwright 테스트 도구

```python
# Playwright의 강력한 테스트 기능
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
    page = await browser.new_page()

    # 1. 로그인
    await login(page, "test_id", "test_pw")

    # 2. 글 작성
    result = await create_post(page, "테스트 제목", "테스트 내용")

    # 3. 검증
    assert result["success"] == True
    assert "blog.naver.com" in result["post_url"]
```

### 9.2 Trace Viewer 활용

```python
# 모든 액션 기록
context = await browser.new_context()
await context.tracing.start(screenshots=True, snapshots=True)

# 테스트 실행
page = await context.new_page()
await create_post(page, "제목", "내용")

# Trace 저장
await context.tracing.stop(path="trace.zip")
# playwright show-trace trace.zip 명령으로 시각화
```

## 10. 배포 및 운영

### 10.1 MCP 서버 실행

```bash
# 직접 실행
python -m naver_blog_mcp.server

# uv를 통한 실행
uv run naver-blog-mcp

# Playwright 브라우저 설치 (최초 1회)
playwright install chromium
```

### 10.2 Claude Desktop 설정

```json
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
        "NAVER_BLOG_ID": "your_blog_id",
        "NAVER_BLOG_PASSWORD": "your_password",
        "HEADLESS": "true"
      }
    }
  }
}
```

### 10.3 의존성 관리

```toml
[project]
name = "naver-blog-mcp"
version = "0.1.0"
requires-python = ">=3.13"
dependencies = [
    "mcp[cli]>=1.20.0",
    "playwright>=1.40.0",
    "httpx>=0.25.0",
    "tenacity>=8.2.0",
    "pydantic>=2.5.0",
    "python-dotenv>=1.0.0",
    "aiofiles>=23.0.0",
    "markdown>=3.5.0",      # Markdown -> HTML 변환
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-asyncio>=0.21.0",
    "pytest-playwright>=0.4.0",
    "pytest-cov>=4.1.0",
    "black>=23.0.0",
    "ruff>=0.1.0",
    "mypy>=1.7.0"
]
```

## 11. 향후 확장 가능성

### 11.1 추가 기능
- **예약 발행**: 특정 시간에 자동 발행 (cron 연동)
- **통계 조회**: 조회수, 댓글 수 크롤링
- **댓글 관리**: 댓글 조회 및 답글 작성
- **멀티 계정**: 여러 네이버 계정 동시 관리

### 11.2 Playwright 고급 기능 활용
- **Video Recording**: 전체 작업 과정 녹화
- **HAR 파일**: 네트워크 요청 분석
- **모바일 에뮬레이션**: 모바일 블로그 앱 시뮬레이션
- **지역화**: 다국어 블로그 지원

### 11.3 다른 플랫폼 지원
- 티스토리
- Medium
- WordPress
- 통합 블로그 관리 MCP 서버

## 12. 주의사항 및 제약

### 12.1 네이버 이용약관 준수
- 과도한 자동화 사용 자제
- 스팸성 콘텐츠 게시 금지
- 정상적인 사용 패턴 유지 (Rate Limiting)

### 12.2 기술적 제약
- **CAPTCHA**: 자동화 감지 시 수동 개입 필요
- **UI 변경**: 네이버 UI 변경 시 셀렉터 업데이트 필요
- **성능**: Selenium보다 빠르지만 API보다는 느림
- **리소스**: 브라우저 실행으로 인한 메모리/CPU 사용

### 12.3 권장 사용 패턴
```python
# Good: 적절한 딜레이
await page.fill("#title", title)
await asyncio.sleep(1)  # 인간적인 타이핑 속도
await page.fill("#content", content)

# Bad: 너무 빠른 자동화 (감지 위험)
await page.fill("#title", title)
await page.fill("#content", content)  # 즉시 실행
```

## 13. 참고 자료

### 13.1 공식 문서
- [Playwright Python 문서](https://playwright.dev/python/)
- [MCP Specification](https://modelcontextprotocol.io/)
- [네이버 블로그 고객센터](https://help.naver.com/service/5628/contents/17698)

### 13.2 Playwright 리소스
- [Playwright Inspector](https://playwright.dev/python/docs/debug)
- [Trace Viewer](https://playwright.dev/python/docs/trace-viewer)
- [Best Practices](https://playwright.dev/python/docs/best-practices)
