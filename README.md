# 네이버 블로그 MCP 서버

[![Python](https://img.shields.io/badge/Python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![Playwright](https://img.shields.io/badge/Playwright-1.55.0-green.svg)](https://playwright.dev/)
[![MCP](https://img.shields.io/badge/MCP-1.20.0+-orange.svg)](https://modelcontextprotocol.io/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Playwright 기반 네이버 블로그 자동화를 위한 Model Context Protocol (MCP) 서버입니다. Claude가 네이버 블로그에 글을 작성하고 관리할 수 있도록 합니다.

## 📋 프로젝트 개요

네이버 블로그의 공식 API가 2020년에 종료됨에 따라, Playwright 웹 브라우저 자동화를 활용하여 MCP (Model Context Protocol) 서버를 구현합니다. AI 어시스턴트(Claude 등)가 네이버 블로그에 글을 작성할 수 있도록 지원합니다.

## ✨ 주요 기능

- ✅ **네이버 로그인 자동화** (세션 저장/재사용)
- ✅ **MCP 서버 구현** (Claude Desktop 연동)
- ✅ **네이버 블로그 글 작성** (제목, 본문, 발행)
- ✅ **세션 관리** (자동 로그인 유지)
- 🚧 이미지 업로드 (Phase 2)
- 🚧 Markdown 지원 (Phase 2)
- 🚧 카테고리 및 태그 관리 (Phase 2)

## 🛠️ 기술 스택

- **Python 3.13**
- **Playwright 1.55.0** - 웹 브라우저 자동화
- **MCP SDK** - Model Context Protocol
- **Pydantic** - 데이터 검증
- **Tenacity** - 재시도 로직

## 📦 설치

### 1. 저장소 클론

```bash
git clone https://github.com/space-cap/naver-blog-mcp.git
cd naver-blog-mcp
```

### 2. 의존성 설치

```bash
# uv를 사용하여 의존성 설치
uv sync

# Playwright 브라우저 다운로드 (필수!)
uv run playwright install chromium
```

### 3. 환경 변수 설정

```bash
# .env.example을 .env로 복사
cp .env.example .env

# .env 파일 편집
# NAVER_BLOG_ID와 NAVER_BLOG_PASSWORD를 입력하세요
```

`.env` 파일 예시:

```env
# 네이버 블로그 계정 정보
NAVER_BLOG_ID=your_naver_id
NAVER_BLOG_PASSWORD=your_password

# Playwright 설정
HEADLESS=false  # 디버깅 시 false로 설정
SLOW_MO=100     # 액션 사이 딜레이 (ms)

# 로깅 레벨
LOG_LEVEL=INFO
```

## 🚀 사용 방법

### 방법 1: Claude Desktop과 연동 (권장)

Claude Desktop 설정 파일(`claude_desktop_config.json`)에 다음 추가:

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

Claude Desktop 재시작 후 다음과 같이 사용:

```
네이버 블로그에 글을 작성해줘.
제목: MCP 테스트
내용: Claude가 작성한 첫 번째 글!
```

### 방법 2: 직접 실행

```bash
# MCP 서버 실행
uv run naver-blog-mcp
```

### 방법 3: 테스트 스크립트

```bash
# 서버 초기화 테스트
uv run python tests/test_server.py

# Tool 핸들러 테스트 (실제 글 작성)
uv run python tests/test_tools.py

# 통합 테스트 (전체)
uv run python tests/test_integration.py
```

## 📁 프로젝트 구조

```
naver-blog-mcp/
├── src/
│   └── naver_blog_mcp/
│       ├── server.py              # ✅ MCP 서버 메인
│       ├── config.py              # ✅ 설정 관리
│       ├── automation/            # Playwright 자동화
│       │   ├── login.py          # ✅ 로그인 자동화
│       │   ├── post_actions.py   # ✅ 글쓰기 자동화
│       │   └── selectors.py      # ✅ DOM 셀렉터
│       ├── services/              # 비즈니스 로직
│       │   └── session_manager.py # ✅ 세션 관리
│       ├── mcp/                   # MCP 프로토콜
│       │   └── tools.py          # ✅ Tool 정의 및 핸들러
│       ├── models/                # 데이터 모델
│       └── utils/                 # 유틸리티
├── tests/
│   ├── test_server.py            # ✅ 서버 초기화 테스트
│   ├── test_tools.py             # ✅ Tool 핸들러 테스트
│   └── test_integration.py       # ✅ 통합 테스트
├── docs/
│   ├── architecture.md           # 아키텍처 설계서
│   ├── implementation-plan.md    # 구현 계획서
│   ├── progress.md               # 진행 상황
│   └── user-guide.md             # ✅ 사용자 가이드
└── playwright-state/             # 세션 저장 (Git 무시)
```

## 📊 개발 진행 상황

**Phase 1 진행 중: 50% (Day 7/14 완료)**

```
Phase 1 (Week 1-2): ███████░░░░░░░ 50%
Phase 2 (Week 3):   ░░░░░░░░░░░░░░  0%
Phase 3 (Week 4):   ░░░░░░░░░░░░░░  0%

전체 프로젝트:     ███████░░░░░░░ 28%
```

### 완료된 마일스톤
- ✅ **Day 1-3**: 프로젝트 초기 설정 및 기본 자동화
  - 로그인 자동화, 글쓰기 자동화, DOM 셀렉터 정리
- ✅ **Day 5**: MCP 서버 구조 설정
  - 서버 초기화, Tool 메타데이터 정의
- ✅ **Day 6**: 핵심 Tool 구현
  - create_post Tool 완전 구현, 기존 자동화 통합
- ✅ **Day 7**: 통합 테스트 ✅
  - 전체 시스템 검증, Claude Desktop 설정, 사용자 가이드 작성

### 다음 단계
- 🚧 **Day 8-10**: 에러 처리 및 재시도 로직
- 🚧 **Day 11-14**: 이미지 업로드 및 Markdown 지원

자세한 진행 상황은 [docs/progress.md](docs/progress.md)를 참고하세요.

## 🔧 개발

### 테스트 실행

```bash
# 모든 테스트
uv run pytest tests/ -v

# 로그인 테스트
uv run python tests/test_login.py

# 글쓰기 테스트
uv run python tests/test_post_write.py
```

### 코드 포매팅

```bash
# Black 포매팅
uv run black src/ tests/

# Ruff 린팅
uv run ruff check src/ tests/

# Mypy 타입 체킹
uv run mypy src/
```

### Playwright 디버깅

```bash
# Inspector 모드
PWDEBUG=1 uv run python tests/test_post_write.py

# 헤드 모드 (브라우저 보이기)
HEADLESS=false uv run python tests/test_post_write.py

# 느린 모드 (액션 사이 딜레이)
SLOW_MO=500 uv run python tests/test_post_write.py
```

## ⚠️ 주의사항

### CAPTCHA
- 헤드리스 모드에서 CAPTCHA가 발생할 수 있습니다
- `HEADLESS=false`로 설정하면 수동으로 CAPTCHA를 풀 수 있습니다

### 네이버 이용약관
- 과도한 자동화 사용 자제
- 스팸성 콘텐츠 게시 금지
- 정상적인 사용 패턴 유지

### 세션 관리
- 세션은 최대 24시간 유효
- `playwright-state/` 폴더는 절대 Git에 커밋하지 마세요
- `.env` 파일도 Git에 커밋하지 마세요

## 📚 문서

- [아키텍처 설계서](docs/architecture.md) - 상세 시스템 아키텍처
- [구현 계획서](docs/implementation-plan.md) - 4주 구현 로드맵
- [진행 상황](docs/progress.md) - 프로젝트 진행 현황
- [사용자 가이드](docs/user-guide.md) - 완전한 사용 가이드

## 🎯 사용 예시

### 예시 1: 간단한 글 작성

Claude에게 다음과 같이 요청:

```
네이버 블로그에 글을 써줘.
제목: 오늘의 개발 일지
내용: MCP 서버를 사용해서 자동으로 글을 작성했다. 정말 편리하다!
```

### 예시 2: 기술 블로그 작성

```
Playwright의 장점에 대한 기술 블로그를 작성해줘.
제목은 "Playwright로 웹 자동화 시작하기"로 하고,
Selenium과의 비교, 코드 예제를 포함해줘.
```

### 예시 3: 마크다운 형식

```
다음 마크다운을 네이버 블로그 글로 작성해줘:

제목: Python asyncio 입문

# asyncio란?
Python의 비동기 프로그래밍 라이브러리입니다.

## 주요 개념
- Event Loop
- Coroutines
- Tasks
```

## 🤝 기여

이슈 및 PR을 환영합니다!

## 📄 라이선스

MIT License

## 📞 문의

GitHub Issues를 통해 문의해주세요.

---

**🤖 Generated with [Claude Code](https://claude.com/claude-code)**
