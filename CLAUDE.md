# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Communication Guidelines

**IMPORTANT**: Always respond in Korean (한글) when communicating with users in this repository.

## Project Overview

Playwright 기반 네이버 블로그 MCP 서버입니다. 네이버 블로그의 공식 API가 2020년에 종료됨에 따라, 웹 브라우저 자동화를 통해 MCP (Model Context Protocol) 서버를 구현했습니다.

**프로젝트 상태**: Day 12까지 완료 (48% 완성)

## Development Setup

This project uses `uv` for Python package management:

```bash
# Install dependencies
uv sync

# Install Playwright browsers
uv run playwright install chromium

# Run MCP server
uv run naver-blog-mcp

# Run tests
uv run python tests/test_image_upload.py
uv run python tests/test_error_handling.py
```

## Project Structure

```
src/naver_blog_mcp/
├── server.py                    # MCP 서버 메인
├── config.py                    # 환경 변수 및 설정
├── automation/                  # Playwright 자동화
│   ├── login.py                # 네이버 로그인 자동화
│   ├── post_actions.py         # 글쓰기 자동화
│   ├── image_upload.py         # 이미지 업로드 (Day 11-12)
│   └── selectors.py            # DOM 셀렉터 정의
├── services/
│   └── session_manager.py      # 세션 저장/복원
├── mcp/
│   └── tools.py                # MCP Tool 정의 및 핸들러
└── utils/
    ├── exceptions.py           # 커스텀 예외 (Day 8)
    ├── error_handler.py        # 에러 핸들러 (Day 8)
    ├── retry.py                # 재시도 로직 (Day 9)
    ├── trace_manager.py        # Playwright Trace (Day 10)
    └── selector_helper.py      # 대체 셀렉터 헬퍼 (Day 10)
```

## Key Technologies

- **Python 3.13+**
- **Playwright 1.55.0** - 웹 브라우저 자동화
- **MCP SDK 1.20.0+** - Model Context Protocol
- **Pydantic** - 데이터 검증
- **Tenacity** - 재시도 로직 (지수 백오프)
- **Pillow** - 이미지 처리 (테스트용)

## Implemented Features

### MCP Tools
1. **`naver_blog_create_post`** - 블로그 글 작성
   - 파라미터: title, content, category, tags, images, publish
   - 이미지 업로드 지원 (파일 경로 배열)

2. **`naver_blog_delete_post`** - 글 삭제
   - 파라미터: post_url

3. **`naver_blog_list_categories`** - 카테고리 목록 조회
   - 파라미터: 없음

### Core Features
- ✅ 네이버 로그인 자동화 (세션 저장/재사용)
- ✅ iframe 기반 에디터 접근
- ✅ 이미지 업로드 (단일/다중, 파일/Base64)
  - 지원 포맷: JPG, PNG, GIF, BMP, HEIC, HEIF, WebP
  - 크기 제한: 10MB
- ✅ 에러 처리 및 자동 재시도
  - 네트워크 에러 자동 재시도 (2s → 4s → 8s)
  - UI 변경 시 대체 셀렉터 자동 전환
- ✅ 디버깅 도구
  - Playwright Trace 자동 기록
  - 에러 발생 시 자동 스크린샷

## Important Implementation Details

### iframe 처리
네이버 블로그 에디터는 `iframe#mainFrame` 내부에 있습니다. 모든 DOM 조작은 iframe 내부에서 수행해야 합니다:

```python
iframe_element = await page.wait_for_selector("iframe#mainFrame")
main_frame = await iframe_element.content_frame()
# main_frame에서 작업 수행
```

### 세션 관리
- 세션은 `playwright-state/auth.json`에 저장
- 로그인 후 자동으로 세션 저장
- 다음 실행 시 세션 재사용 (재로그인 불필요)

### 에러 처리
- 모든 커스텀 예외는 `NaverBlogError`를 상속
- `@retry_on_error` 데코레이터로 자동 재시도
- 재시도 가능: NetworkError, TimeoutError, NavigationError
- 재시도 불가: ElementNotFoundError (대체 셀렉터 사용)

## Environment Variables

`.env` 파일 필요:
```
NAVER_BLOG_ID=your_naver_id
NAVER_BLOG_PASSWORD=your_password
HEADLESS=false
SLOW_MO=100
LOG_LEVEL=INFO
```

## Testing

```bash
# 이미지 업로드 테스트
uv run python tests/test_image_upload.py

# 에러 처리 테스트
uv run python tests/test_error_handling.py

# 이미지 업로드 구조 조사
uv run python tests/test_image_upload_research.py
```

## Limitations

### Markdown 지원 불가 (Day 13-14)
네이버 블로그는 Markdown을 지원하지 않습니다:
- 스마트에디터 ONE으로 통합되면서 HTML 편집 모드 제거됨
- WYSIWYG 에디터만 지원
- Markdown 관련 기능은 구현 불가능

## Documentation

- `docs/architecture.md` - 아키텍처 설계
- `docs/implementation-plan.md` - 원래 계획 (Day 13-14는 불가능)
- `docs/progress.md` - 상세 진행 상황
- `docs/user-guide.md` - 사용자 가이드
- `docs/image-upload-research.md` - 이미지 업로드 조사 결과
