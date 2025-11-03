# 네이버 블로그 MCP 서버 사용 가이드

## 📖 목차
1. [개요](#개요)
2. [설치](#설치)
3. [설정](#설정)
4. [Claude Desktop 연동](#claude-desktop-연동)
5. [사용 가능한 Tool](#사용-가능한-tool)
6. [사용 예시](#사용-예시)
7. [문제 해결](#문제-해결)

---

## 개요

네이버 블로그 MCP 서버는 Claude가 네이버 블로그와 상호작용할 수 있도록 하는 [Model Context Protocol](https://modelcontextprotocol.io/) 서버입니다.

### 주요 기능
- ✅ 네이버 블로그 글 작성 및 발행
- ✅ 세션 자동 관리 (로그인 상태 유지)
- ✅ Playwright 기반 안정적인 브라우저 자동화
- 🚧 글 삭제 (향후 지원 예정)
- 🚧 카테고리 관리 (향후 지원 예정)

---

## 설치

### 필수 요구사항
- Python 3.13+
- [uv](https://github.com/astral-sh/uv) 패키지 매니저
- 네이버 블로그 계정

### 1. 저장소 클론
```bash
git clone https://github.com/space-cap/naver-blog-mcp.git
cd naver-blog-mcp
```

### 2. 의존성 설치
```bash
uv sync
```

### 3. Playwright 브라우저 설치
```bash
uv run playwright install chromium
```

---

## 설정

### 1. 환경 변수 설정

`.env.example`을 복사하여 `.env` 파일을 생성합니다:

```bash
cp .env.example .env
```

`.env` 파일을 편집하여 네이버 계정 정보를 입력합니다:

```env
# 네이버 블로그 계정
NAVER_BLOG_ID=your_naver_id
NAVER_BLOG_PASSWORD=your_naver_password

# Playwright 설정
HEADLESS=false              # 브라우저 보이기 (디버깅 시 유용)
SLOW_MO=100                 # 자동화 속도 조절 (ms)

# 로깅 설정
LOG_LEVEL=INFO              # DEBUG, INFO, WARNING, ERROR
```

### 2. 최초 로그인

서버를 처음 실행하면 자동으로 네이버에 로그인하고 세션을 저장합니다:

```bash
uv run python tests/test_server.py
```

로그인이 성공하면 `playwright-state/auth.json`에 세션이 저장되어 이후 자동으로 재사용됩니다.

---

## Claude Desktop 연동

### 1. Claude Desktop 설정 파일 위치

운영체제별 설정 파일 경로:

**Windows:**
```
%APPDATA%\Claude\claude_desktop_config.json
```

**macOS:**
```
~/Library/Application Support/Claude/claude_desktop_config.json
```

**Linux:**
```
~/.config/Claude/claude_desktop_config.json
```

### 2. 설정 추가

`claude_desktop_config.json` 파일을 열고 다음 내용을 추가합니다:

**Windows:**
```json
{
  "mcpServers": {
    "naver-blog": {
      "command": "uv",
      "args": ["run", "naver-blog-mcp"],
      "cwd": "C:\\workdir\\space-cap\\naver-blog-mcp",
      "env": {
        "PYTHONIOENCODING": "utf-8"
      }
    }
  }
}
```

**macOS/Linux:**
```json
{
  "mcpServers": {
    "naver-blog": {
      "command": "uv",
      "args": ["run", "naver-blog-mcp"],
      "cwd": "/path/to/naver-blog-mcp",
      "env": {
        "PYTHONIOENCODING": "utf-8"
      }
    }
  }
}
```

> **주의:** `cwd` 경로를 본인의 프로젝트 경로로 변경하세요!

### 3. Claude Desktop 재시작

설정을 저장한 후 Claude Desktop을 완전히 종료하고 다시 시작합니다.

### 4. 연동 확인

Claude Desktop에서 새 대화를 시작하고 다음과 같이 요청해보세요:

```
네이버 블로그에 글을 작성해줘.
제목: MCP 서버 테스트
내용: Claude가 자동으로 작성한 첫 번째 글입니다!
```

---

## 사용 가능한 Tool

### 1. naver_blog_create_post

네이버 블로그에 새 글을 작성합니다.

**파라미터:**
- `title` (필수): 글 제목
- `content` (필수): 글 본문 내용
- `category` (선택): 카테고리 이름
- `tags` (선택): 태그 목록 (배열)
- `publish` (선택): 즉시 발행 여부 (기본: true, false면 임시저장)

**응답:**
```json
{
  "success": true,
  "message": "글이 성공적으로 발행되었습니다.",
  "post_url": "https://blog.naver.com/your_id/123456789",
  "title": "MCP 서버 테스트"
}
```

### 2. naver_blog_delete_post (향후 지원)

네이버 블로그의 글을 삭제합니다.

**파라미터:**
- `post_url` (필수): 삭제할 글의 URL

### 3. naver_blog_list_categories (향후 지원)

네이버 블로그의 카테고리 목록을 가져옵니다.

**파라미터:** 없음

---

## 사용 예시

### 예시 1: 간단한 글 작성

```
네이버 블로그에 글을 써줘.

제목: 오늘의 일기
내용:
오늘은 MCP 서버를 처음 사용해봤다.
Claude가 자동으로 글을 작성해주니 정말 편리하다!
```

### 예시 2: 마크다운으로 작성

```
다음 내용을 네이버 블로그 글로 작성해줘:

제목: MCP 서버 소개

내용:
# MCP 서버란?

Model Context Protocol 서버는 Claude가 외부 시스템과
상호작용할 수 있게 해주는 표준 프로토콜입니다.

## 주요 장점
- 확장 가능한 Tool 시스템
- 표준화된 인터페이스
- 안정적인 세션 관리
```

### 예시 3: 코드 포함 글 작성

```
다음 Python 코드를 설명하는 블로그 글을 작성해줘:

제목: Python asyncio 입문

내용에 다음 코드를 포함해줘:

```python
import asyncio

async def main():
    print("Hello, async world!")
    await asyncio.sleep(1)
    print("Done!")

asyncio.run(main())
```

코드의 동작 방식과 asyncio의 장점을 설명해줘.
```

---

## 문제 해결

### 1. 로그인 실패

**증상:** "로그인에 실패했습니다" 에러 메시지

**원인:**
- 잘못된 아이디/비밀번호
- CAPTCHA 감지

**해결방법:**
1. `.env` 파일의 아이디/비밀번호 확인
2. `HEADLESS=false`로 설정하여 브라우저를 보면서 디버깅
3. CAPTCHA가 나타나면 수동으로 풀기

### 2. 세션 만료

**증상:** 이전에는 작동했는데 갑자기 로그인 페이지로 리다이렉트됨

**해결방법:**
```bash
# 저장된 세션 삭제
rm playwright-state/auth.json

# 서버 재실행 (자동으로 재로그인)
uv run python tests/test_server.py
```

### 3. 글쓰기 페이지 로딩 실패

**증상:** "글쓰기 페이지로 이동할 수 없습니다" 에러

**원인:**
- 네이버 블로그 UI 변경
- 네트워크 문제

**해결방법:**
1. `SLOW_MO=500`으로 설정하여 속도를 늦춤
2. 네트워크 연결 확인
3. 브라우저를 보면서 어느 단계에서 실패하는지 확인

### 4. MCP 서버 시작 실패

**증상:** Claude Desktop에서 "naver-blog 서버를 시작할 수 없습니다"

**해결방법:**
1. `claude_desktop_config.json`의 `cwd` 경로 확인
2. 터미널에서 직접 실행해보기:
   ```bash
   cd /path/to/naver-blog-mcp
   uv run naver-blog-mcp
   ```
3. 로그 확인:
   - Windows: `%APPDATA%\Claude\logs\`
   - macOS: `~/Library/Logs/Claude/`

### 5. 한글 깨짐

**증상:** 글 내용이나 제목이 깨져서 표시됨

**해결방법:**
- `.env` 파일에 다음 추가:
  ```env
  PYTHONIOENCODING=utf-8
  ```
- `claude_desktop_config.json`에 환경변수 설정 확인

---

## 추가 정보

### 로그 확인

디버깅을 위해 로그 레벨을 높이려면:

```env
LOG_LEVEL=DEBUG
```

### 테스트

개발자 테스트 실행:

```bash
# 서버 초기화 테스트
uv run python tests/test_server.py

# Tool 핸들러 테스트
uv run python tests/test_tools.py

# 통합 테스트
uv run python tests/test_integration.py
```

### 기여

버그 리포트 및 기여는 [GitHub Issues](https://github.com/space-cap/naver-blog-mcp/issues)에서 환영합니다!

---

## 라이선스

MIT License

## 지원

- 📧 Email: space-cap@example.com
- 🐛 Issues: https://github.com/space-cap/naver-blog-mcp/issues
- 📖 Docs: https://github.com/space-cap/naver-blog-mcp/tree/main/docs
