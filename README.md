# Naver Blog MCP Server

Playwright 기반 네이버 블로그 자동화 MCP 서버

## 📋 프로젝트 개요

네이버 블로그의 공식 API가 2020년에 종료됨에 따라, Playwright 웹 브라우저 자동화를 활용하여 MCP (Model Context Protocol) 서버를 구현합니다. AI 어시스턴트(Claude 등)가 네이버 블로그에 글을 작성할 수 있도록 지원합니다.

## ✨ 주요 기능

- ✅ **네이버 로그인 자동화** (세션 저장/재사용)
- ✅ **네이버 블로그 글 작성** (제목, 본문, 발행)
- 🚧 이미지 업로드
- 🚧 Markdown 지원
- 🚧 카테고리 및 태그 관리

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

### 로그인 테스트

```bash
# 네이버 로그인 자동화 테스트
uv run python tests/test_login.py
```

이 테스트는 다음을 수행합니다:
1. 네이버에 자동으로 로그인
2. 세션을 `playwright-state/auth.json`에 저장
3. 세션 재사용 테스트

### 글쓰기 테스트

```bash
# 네이버 블로그 글 작성 테스트
uv run python tests/test_post_write.py
```

이 테스트는 다음을 수행합니다:
1. 저장된 세션으로 자동 로그인
2. 글쓰기 페이지로 이동
3. 제목과 본문 입력 (iframe 처리)
4. 글 발행 및 URL 확인

### MCP 서버 실행 (개발 중)

```bash
uv run naver-blog-mcp
```

## 📁 프로젝트 구조

```
naver-blog-mcp/
├── src/
│   └── naver_blog_mcp/
│       ├── __init__.py
│       ├── config.py              # 설정 관리
│       ├── automation/            # Playwright 자동화
│       │   ├── login.py          # ✅ 로그인 자동화
│       │   ├── post_actions.py   # ✅ 글쓰기 자동화
│       │   └── selectors.py      # ✅ DOM 셀렉터
│       ├── services/              # 비즈니스 로직
│       │   └── session_manager.py # ✅ 세션 관리
│       ├── mcp/                   # MCP 프로토콜
│       ├── models/                # 데이터 모델
│       └── utils/                 # 유틸리티
├── tests/
│   ├── test_login.py              # ✅ 로그인 테스트
│   └── test_post_write.py         # ✅ 글쓰기 테스트
├── docs/
│   ├── architecture.md            # 아키텍처 설계서
│   ├── implementation-plan.md     # 구현 계획서
│   └── progress.md                # 진행 상황
└── playwright-state/              # 세션 저장 (Git 무시)
```

## 📊 개발 진행 상황

**Phase 1 완료: 30% (Day 1-3/25)**

- ✅ Day 1: 프로젝트 초기 설정
- ✅ Day 2: 네이버 로그인 자동화
- ✅ Day 3: 글쓰기 페이지 자동화
- 🚧 Day 4-7: MCP 서버 구현

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

- [아키텍처 설계서](docs/architecture.md)
- [구현 계획서](docs/implementation-plan.md)
- [진행 상황](docs/progress.md)

## 🤝 기여

이슈 및 PR을 환영합니다!

## 📄 라이선스

MIT License

## 📞 문의

GitHub Issues를 통해 문의해주세요.

---

**🤖 Generated with [Claude Code](https://claude.com/claude-code)**
