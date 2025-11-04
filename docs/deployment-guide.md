# 네이버 블로그 MCP 서버 배포 가이드

이 문서는 네이버 블로그 MCP 서버를 다른 사용자에게 배포하고 설치하는 방법을 안내합니다.

## 📋 목차

### Part A: 개발자용 (배포 방법)
1. [배포 방식 개요](#배포-방식-개요)
2. [방식 1: GitHub 공개 저장소 (권장)](#방식-1-github-공개-저장소-권장)
3. [방식 2: PyPI 패키지 배포](#방식-2-pypi-패키지-배포)
4. [방식 3: Docker 컨테이너](#방식-3-docker-컨테이너)
5. [방식 4: MCP Registry 등록](#방식-4-mcp-registry-등록)
6. [유지보수 및 업데이트](#유지보수-및-업데이트)

### Part B: 사용자용 (설치 및 사용)
7. [사전 요구사항](#사전-요구사항)
8. [설치 방법](#설치-방법)
9. [Claude Desktop 연동](#claude-desktop-연동)
10. [사용 가능한 기능](#사용-가능한-기능)
11. [문제 해결](#문제-해결)
12. [보안 고려사항](#보안-고려사항)

---

# Part A: 개발자용 (배포 방법)

## 배포 방식 개요

네이버 블로그 MCP 서버를 배포하는 4가지 주요 방식:

| 방식 | 난이도 | 사용자 편의성 | 유지보수 | 권장도 |
|------|--------|--------------|---------|--------|
| GitHub 공개 저장소 | ⭐ 쉬움 | ⭐⭐⭐ 보통 | ⭐⭐⭐⭐ 쉬움 | ✅ **권장** |
| PyPI 패키지 | ⭐⭐⭐ 어려움 | ⭐⭐⭐⭐⭐ 매우 쉬움 | ⭐⭐⭐ 보통 | 🔥 **최고** |
| Docker 컨테이너 | ⭐⭐ 보통 | ⭐⭐⭐⭐ 쉬움 | ⭐⭐⭐⭐ 쉬움 | 🚀 추천 |
| MCP Registry | ⭐⭐ 보통 | ⭐⭐⭐⭐⭐ 매우 쉬움 | ⭐⭐⭐⭐⭐ 매우 쉬움 | 🎯 미래 |

**현재 상태**: 방식 1 (GitHub) 사용 중

---

## 방식 1: GitHub 공개 저장소 (권장)

### 장점
- ✅ 설정이 간단함
- ✅ 버전 관리가 용이함
- ✅ 이슈 트래킹 및 커뮤니티 활용
- ✅ GitHub Actions로 CI/CD 자동화 가능
- ✅ 무료

### 단점
- ⚠️ 사용자가 Git과 Python 환경 설정 필요
- ⚠️ 의존성 설치 과정이 복잡할 수 있음

### 배포 체크리스트

#### 1. 저장소 공개 설정
```bash
# GitHub에서 저장소 설정
# Settings > General > Danger Zone > Change visibility > Public
```

#### 2. 필수 파일 확인
- ✅ `README.md` - 프로젝트 소개
- ✅ `LICENSE` - 라이선스 (MIT 권장)
- ✅ `.gitignore` - 민감 정보 제외
- ✅ `pyproject.toml` - 의존성 정의
- ✅ `docs/deployment-guide.md` - 배포 가이드
- ✅ `.env.example` - 환경 변수 템플릿

#### 3. 릴리스 생성
```bash
# 버전 태그 생성
git tag -a v1.0.0 -m "첫 번째 공식 릴리스"
git push origin v1.0.0

# GitHub에서 Release 생성
# Releases > Create a new release
# - Tag: v1.0.0
# - Title: 네이버 블로그 MCP v1.0.0
# - Description: 주요 기능 설명
# - Assets: 소스 코드 ZIP (자동 생성)
```

#### 4. README 배지 추가
```markdown
[![GitHub release](https://img.shields.io/github/v/release/space-cap/naver-blog-mcp)](https://github.com/space-cap/naver-blog-mcp/releases)
[![Downloads](https://img.shields.io/github/downloads/space-cap/naver-blog-mcp/total)](https://github.com/space-cap/naver-blog-mcp/releases)
[![Stars](https://img.shields.io/github/stars/space-cap/naver-blog-mcp)](https://github.com/space-cap/naver-blog-mcp)
```

#### 5. GitHub Topics 설정
```
Settings > General > Topics
추가: mcp, claude, naver-blog, playwright, automation, python
```

---

## 방식 2: PyPI 패키지 배포

Python 패키지로 배포하면 사용자가 `pip install`로 간단히 설치 가능합니다.

### 장점
- ✅ 사용자가 `pip install naver-blog-mcp`로 한 줄로 설치
- ✅ 의존성 자동 해결
- ✅ 버전 관리 용이
- ✅ 전문적인 인상

### 단점
- ⚠️ PyPI 계정 필요
- ⚠️ 패키지 이름 중복 불가
- ⚠️ 빌드 및 배포 과정 필요

### 배포 단계

#### 1. 패키지 준비

**pyproject.toml 확인:**
```toml
[project]
name = "naver-blog-mcp"
version = "1.0.0"
description = "Playwright-based MCP server for Naver Blog automation"
authors = [
    {name = "Your Name", email = "your.email@example.com"}
]
readme = "README.md"
requires-python = ">=3.13"
license = {text = "MIT"}
keywords = ["mcp", "claude", "naver", "blog", "automation", "playwright"]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3.13",
    "Topic :: Software Development :: Libraries :: Python Modules",
]

[project.urls]
Homepage = "https://github.com/space-cap/naver-blog-mcp"
Documentation = "https://github.com/space-cap/naver-blog-mcp/blob/main/docs/deployment-guide.md"
Repository = "https://github.com/space-cap/naver-blog-mcp"
Issues = "https://github.com/space-cap/naver-blog-mcp/issues"

[project.scripts]
naver-blog-mcp = "naver_blog_mcp.server:main"
```

#### 2. 빌드

```bash
# 빌드 도구 설치
pip install build twine

# 패키지 빌드
python -m build

# 결과 확인
ls dist/
# naver_blog_mcp-1.0.0-py3-none-any.whl
# naver_blog_mcp-1.0.0.tar.gz
```

#### 3. PyPI 업로드

```bash
# TestPyPI에 먼저 업로드 (테스트용)
twine upload --repository testpypi dist/*

# 테스트 설치
pip install --index-url https://test.pypi.org/simple/ naver-blog-mcp

# 정상 작동 확인 후 실제 PyPI에 업로드
twine upload dist/*
```

#### 4. 사용자 설치 방법

```bash
# PyPI에서 설치
pip install naver-blog-mcp

# Playwright 브라우저 설치
playwright install chromium

# 실행
naver-blog-mcp
```

### 자동 배포 (GitHub Actions)

`.github/workflows/publish.yml`:
```yaml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.13'
      - name: Install dependencies
        run: |
          pip install build twine
      - name: Build package
        run: python -m build
      - name: Publish to PyPI
        env:
          TWINE_USERNAME: __token__
          TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
        run: twine upload dist/*
```

---

## 방식 3: Docker 컨테이너

Docker를 사용하면 환경 차이로 인한 문제를 완전히 제거할 수 있습니다.

### 장점
- ✅ 환경 일관성 보장
- ✅ 의존성 문제 없음
- ✅ 쉬운 배포 및 실행
- ✅ 격리된 환경

### 단점
- ⚠️ Docker 설치 필요
- ⚠️ 이미지 크기가 큼 (Playwright 포함)
- ⚠️ GUI 브라우저 실행 복잡 (Headless 모드 필요)

### Dockerfile 작성

```dockerfile
FROM python:3.13-slim

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 의존성 설치
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성 설치
COPY pyproject.toml uv.lock ./
RUN pip install uv && uv sync --frozen

# Playwright 브라우저 설치
RUN uv run playwright install chromium --with-deps

# 애플리케이션 코드 복사
COPY src/ ./src/
COPY .env.example ./.env

# 포트 노출 (stdin/stdout 사용하므로 실제로는 불필요)
EXPOSE 3000

# 실행
CMD ["uv", "run", "naver-blog-mcp"]
```

### Docker Compose

`docker-compose.yml`:
```yaml
version: '3.8'

services:
  naver-blog-mcp:
    build: .
    container_name: naver-blog-mcp
    environment:
      - NAVER_BLOG_ID=${NAVER_BLOG_ID}
      - NAVER_BLOG_PASSWORD=${NAVER_BLOG_PASSWORD}
      - HEADLESS=true
      - LOG_LEVEL=INFO
    volumes:
      - ./playwright-state:/app/playwright-state
    stdin_open: true
    tty: true
```

### 사용 방법

```bash
# 이미지 빌드
docker build -t naver-blog-mcp:latest .

# Docker Hub에 푸시
docker tag naver-blog-mcp:latest spacecap/naver-blog-mcp:latest
docker push spacecap/naver-blog-mcp:latest

# 사용자가 다운로드 및 실행
docker pull spacecap/naver-blog-mcp:latest
docker run -it --rm \
  -e NAVER_BLOG_ID=your_id \
  -e NAVER_BLOG_PASSWORD=your_password \
  spacecap/naver-blog-mcp:latest
```

---

## 방식 4: MCP Registry 등록

Anthropic의 공식 MCP Registry에 등록하면 Claude Desktop에서 자동으로 검색 가능합니다.

### 현재 상태
- 🚧 MCP Registry는 아직 개발 중
- 📅 2025년 중 출시 예정
- 📝 현재는 수동 설정 필요

### 미래 계획

#### 1. MCP Registry 사전 준비

**mcp-manifest.json 작성:**
```json
{
  "name": "naver-blog-mcp",
  "displayName": "네이버 블로그",
  "description": "Playwright 기반 네이버 블로그 자동화 MCP 서버",
  "version": "1.0.0",
  "author": {
    "name": "space-cap",
    "url": "https://github.com/space-cap"
  },
  "repository": {
    "type": "git",
    "url": "https://github.com/space-cap/naver-blog-mcp"
  },
  "license": "MIT",
  "keywords": ["blog", "naver", "automation", "korea"],
  "server": {
    "command": "uv",
    "args": ["run", "naver-blog-mcp"],
    "env": {
      "PYTHONIOENCODING": "utf-8"
    }
  },
  "tools": [
    {
      "name": "naver_blog_create_post",
      "description": "네이버 블로그에 글을 작성합니다",
      "parameters": {
        "title": {"type": "string", "required": true},
        "content": {"type": "string", "required": true},
        "images": {"type": "array", "required": false}
      }
    },
    {
      "name": "naver_blog_list_categories",
      "description": "블로그 카테고리 목록을 조회합니다",
      "parameters": {}
    }
  ],
  "configuration": {
    "required": [
      "NAVER_BLOG_ID",
      "NAVER_BLOG_PASSWORD"
    ],
    "optional": [
      "HEADLESS",
      "SLOW_MO",
      "LOG_LEVEL"
    ]
  }
}
```

#### 2. 등록 절차 (출시 후)

1. MCP Registry 웹사이트 접속
2. GitHub 계정으로 로그인
3. "Submit New Server" 클릭
4. 저장소 URL 입력
5. manifest.json 자동 검증
6. 카테고리 및 태그 선택
7. 제출 및 승인 대기

#### 3. 사용자 경험

Registry 등록 후:
```
Claude Desktop > Settings > MCP Servers > Browse Registry
> 검색: "naver blog"
> "네이버 블로그" 선택
> "Install" 클릭
> 자동 설치 및 설정 완료
```

---

## 유지보수 및 업데이트

### 버전 관리 전략

**Semantic Versioning (SemVer) 사용:**
- `MAJOR.MINOR.PATCH` (예: 1.2.3)
- **MAJOR**: 호환성이 깨지는 변경
- **MINOR**: 새로운 기능 추가 (호환 유지)
- **PATCH**: 버그 수정

### 릴리스 프로세스

#### 1. 버전 업데이트

```bash
# pyproject.toml 버전 수정
version = "1.1.0"

# CHANGELOG.md 업데이트
## [1.1.0] - 2025-11-06
### Added
- 새로운 기능 추가
### Fixed
- 버그 수정
### Changed
- 변경 사항
```

#### 2. 태그 및 릴리스

```bash
# Git 태그 생성
git tag -a v1.1.0 -m "Release v1.1.0: 새 기능 추가"
git push origin v1.1.0

# GitHub Release 생성
# - Release notes 자동 생성
# - 변경 사항 요약
# - 다운로드 링크
```

#### 3. 자동 테스트 (GitHub Actions)

`.github/workflows/test.yml`:
```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
        python-version: ['3.13']
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}
      - name: Install dependencies
        run: |
          pip install uv
          uv sync
          uv run playwright install chromium
      - name: Run tests
        run: |
          uv run pytest tests/ -v
```

### 이슈 관리

#### GitHub Issues 템플릿

**버그 리포트 템플릿** (`.github/ISSUE_TEMPLATE/bug_report.md`):
```markdown
---
name: 버그 리포트
about: 버그를 발견하셨나요?
---

**버그 설명**
발생한 버그를 명확하고 간결하게 설명해주세요.

**재현 방법**
1. '...'로 이동
2. '...'를 클릭
3. '...'까지 스크롤
4. 오류 발생

**예상 동작**
어떤 동작을 기대하셨나요?

**실제 동작**
실제로 어떤 일이 발생했나요?

**환경:**
 - OS: [예: Windows 10]
 - Python 버전: [예: 3.13.0]
 - 버전: [예: v1.0.0]

**추가 컨텍스트**
버그에 대한 추가 정보가 있다면 작성해주세요.
```

**기능 요청 템플릿** (`.github/ISSUE_TEMPLATE/feature_request.md`):
```markdown
---
name: 기능 요청
about: 새로운 기능을 제안해주세요
---

**해결하려는 문제**
어떤 문제를 해결하고 싶으신가요?

**제안하는 해결책**
어떤 기능을 추가하면 좋을까요?

**고려한 대안**
다른 해결 방법을 고려하셨나요?

**추가 컨텍스트**
관련 정보나 스크린샷이 있다면 첨부해주세요.
```

### 커뮤니티 운영

#### 1. Discussions 활성화
```
Settings > General > Features > Discussions ✅
```

카테고리:
- 📢 Announcements (공지사항)
- 💡 Ideas (아이디어)
- 🙏 Q&A (질문과 답변)
- 🎉 Show and tell (사용 사례)

#### 2. Contributing 가이드

**CONTRIBUTING.md 작성:**
```markdown
# 기여 가이드

## 버그 리포트
- GitHub Issues 사용
- 재현 가능한 예제 제공
- 환경 정보 포함

## Pull Request
1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 코드 스타일
- Black formatter 사용
- Ruff linter 통과
- Type hints 사용

## 테스트
- 새 기능에는 테스트 추가
- 모든 테스트가 통과해야 함
```

### 모니터링

#### 다운로드 추적
- GitHub Insights > Traffic
- Release 다운로드 수
- Clone 통계

#### 사용자 피드백
- GitHub Issues
- Discussions
- Star 및 Fork 수

---

# Part B: 사용자용 (설치 및 사용)

---

## 사전 요구사항

### 필수 소프트웨어

1. **Python 3.13 이상**
   - [Python 공식 사이트](https://www.python.org/downloads/)에서 다운로드
   - 설치 시 "Add Python to PATH" 옵션 체크 필수

2. **uv (Python 패키지 매니저)**
   ```bash
   # Windows (PowerShell)
   powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

   # macOS/Linux
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

3. **Claude Desktop**
   - [Claude 공식 사이트](https://claude.ai/download)에서 다운로드
   - 데스크톱 앱 설치 필요

4. **네이버 블로그 계정**
   - 네이버 계정 필요
   - 블로그가 활성화되어 있어야 함

### 권장 사양

- **운영체제**: Windows 10/11, macOS 10.15+, Ubuntu 20.04+
- **RAM**: 최소 4GB (8GB 권장)
- **디스크**: 최소 1GB 여유 공간

---

## 설치 방법

### 1단계: 프로젝트 다운로드

#### 방법 A: Git 사용 (권장)

```bash
# Git으로 클론
git clone https://github.com/space-cap/naver-blog-mcp.git
cd naver-blog-mcp
```

#### 방법 B: ZIP 다운로드

1. [GitHub 릴리스 페이지](https://github.com/space-cap/naver-blog-mcp/releases)에서 최신 버전 다운로드
2. ZIP 파일 압축 해제
3. 터미널에서 압축 해제된 폴더로 이동

### 2단계: 의존성 설치

```bash
# Python 패키지 설치
uv sync

# Playwright 브라우저 설치
uv run playwright install chromium
```

> **참고**: Playwright 브라우저 다운로드는 약 240MB이며, 초기 설치 시에만 필요합니다.

### 3단계: 환경 변수 설정

프로젝트 루트에 `.env` 파일을 생성하고 다음 내용을 입력하세요:

```env
# 네이버 블로그 계정 정보
NAVER_BLOG_ID=your_naver_id
NAVER_BLOG_PASSWORD=your_password

# Playwright 설정 (선택)
HEADLESS=false                    # 브라우저를 보이게 할지 여부
SLOW_MO=100                       # 자동화 속도 조절 (ms)

# 로깅 설정 (선택)
LOG_LEVEL=INFO                    # DEBUG, INFO, WARNING, ERROR
```

> ⚠️ **보안 주의사항**: `.env` 파일은 절대 Git에 커밋하지 마세요. 이미 `.gitignore`에 포함되어 있습니다.

### 4단계: 설치 확인

```bash
# MCP 서버 실행 테스트
uv run naver-blog-mcp --version

# 간단한 테스트 (선택)
uv run python tests/test_category_list.py
```

---

## Claude Desktop 연동

### 1단계: 설정 파일 위치 확인

운영체제별로 Claude Desktop 설정 파일 위치가 다릅니다:

#### Windows
```
%APPDATA%\Claude\claude_desktop_config.json
```
실제 경로: `C:\Users\[사용자명]\AppData\Roaming\Claude\claude_desktop_config.json`

#### macOS
```
~/Library/Application Support/Claude/claude_desktop_config.json
```

#### Linux
```
~/.config/Claude/claude_desktop_config.json
```

### 2단계: 설정 파일 수정

설정 파일을 열고 다음 내용을 추가하세요:

#### Windows

```json
{
  "mcpServers": {
    "naver-blog": {
      "command": "uv",
      "args": [
        "run",
        "naver-blog-mcp"
      ],
      "cwd": "C:\\workdir\\space-cap\\naver-blog-mcp",
      "env": {
        "PYTHONIOENCODING": "utf-8"
      }
    }
  }
}
```

#### macOS/Linux

```json
{
  "mcpServers": {
    "naver-blog": {
      "command": "uv",
      "args": [
        "run",
        "naver-blog-mcp"
      ],
      "cwd": "/path/to/naver-blog-mcp"
    }
  }
}
```

> ⚠️ **중요**: `cwd` 경로를 실제 프로젝트 경로로 변경하세요!

### 3단계: Claude Desktop 재시작

설정 파일을 저장한 후 Claude Desktop을 완전히 종료하고 다시 시작하세요.

### 4단계: 연결 확인

Claude Desktop에서 다음과 같이 테스트하세요:

```
네이버 블로그의 카테고리 목록을 보여줘
```

정상적으로 작동하면 카테고리 목록이 표시됩니다.

---

## 사용 가능한 기능

### 1. 블로그 글 작성 (`naver_blog_create_post`)

```
네이버 블로그에 글을 작성해줘.

제목: "AI 시대의 개발자"
내용: |
  AI가 코드를 작성하는 시대가 왔습니다.
  하지만 개발자의 역할은 더욱 중요해졌습니다.

  창의성과 문제 해결 능력은
  여전히 사람만이 가진 강점입니다.
```

**지원 기능:**
- ✅ 제목 및 본문 작성
- ✅ 이미지 첨부 (파일 경로 지정)
- ✅ 즉시 발행 또는 임시 저장
- ✅ 자동 로그인 및 세션 관리

**매개변수:**
- `title` (필수): 글 제목
- `content` (필수): 글 본문
- `category` (선택): 카테고리 이름
- `tags` (선택): 태그 목록 (배열)
- `images` (선택): 이미지 파일 경로 목록 (배열)
- `publish` (선택): 즉시 발행 여부 (기본값: true)

### 2. 카테고리 목록 조회 (`naver_blog_list_categories`)

```
네이버 블로그의 카테고리 목록을 보여줘
```

**반환 정보:**
- 카테고리 이름
- 카테고리 URL
- 카테고리 번호

---

## 문제 해결

### 문제 1: "Server failed to start" 오류

**원인:**
- Python이나 uv가 설치되지 않음
- 경로가 잘못됨

**해결 방법:**
```bash
# Python 버전 확인
python --version  # Python 3.13 이상이어야 함

# uv 설치 확인
uv --version

# 프로젝트 경로 확인
cd /path/to/naver-blog-mcp
pwd
```

### 문제 2: "로그인 실패" 오류

**원인:**
- `.env` 파일의 계정 정보가 잘못됨
- CAPTCHA 발생

**해결 방법:**
1. `.env` 파일에서 계정 정보 재확인
2. `HEADLESS=false`로 설정하여 브라우저 표시
3. CAPTCHA가 나타나면 수동으로 해결

### 문제 3: "인코딩 오류" (Windows)

**원인:**
- Windows 콘솔 인코딩 문제

**해결 방법:**
- 이미 해결됨 (최신 버전 사용)
- 설정 파일에 `"PYTHONIOENCODING": "utf-8"` 포함 확인

### 문제 4: Tool이 Claude Desktop에 표시되지 않음

**원인:**
- 설정 파일 오류
- Claude Desktop 재시작 필요

**해결 방법:**
1. 설정 파일 JSON 형식 확인 ([JSONLint](https://jsonlint.com/)에서 검증)
2. `cwd` 경로 확인 (역슬래시 `\\` 또는 슬래시 `/` 사용)
3. Claude Desktop 완전히 종료 후 재시작
4. Claude Desktop 로그 확인:
   - Windows: `%APPDATA%\Claude\logs`
   - macOS: `~/Library/Logs/Claude`
   - Linux: `~/.config/Claude/logs`

### 문제 5: 세션이 자주 만료됨

**원인:**
- 세션 파일이 오래됨 (24시간 이상)
- 네이버 보안 정책

**해결 방법:**
```bash
# 세션 파일 삭제 후 재로그인
rm -f playwright-state/auth.json  # macOS/Linux
del playwright-state\auth.json    # Windows
```

---

## 보안 고려사항

### 1. 계정 정보 보호

**필수 조치:**
- ✅ `.env` 파일을 Git에 커밋하지 마세요
- ✅ `.env` 파일 권한을 제한하세요 (chmod 600)
- ✅ 공유 컴퓨터에서는 사용하지 마세요

**권장 조치:**
- 네이버 블로그 전용 계정 사용
- 2단계 인증 설정
- 정기적인 비밀번호 변경

### 2. 세션 파일 관리

세션 파일(`playwright-state/auth.json`)에는 로그인 쿠키가 저장됩니다.

**주의사항:**
- 세션 파일을 다른 사람과 공유하지 마세요
- 정기적으로 세션 파일 삭제
- 공용 저장소에 업로드하지 마세요

### 3. 브라우저 자동화 감지

네이버는 자동화를 감지할 수 있습니다.

**안전한 사용:**
- ✅ 적절한 지연 시간 설정 (`SLOW_MO`)
- ✅ Headless 모드보다 일반 모드 사용
- ✅ 과도한 요청 자제
- ⚠️ 스팸성 글 작성 금지

---

## 업데이트

### 최신 버전으로 업데이트

```bash
# Git을 사용하는 경우
git pull origin main
uv sync

# ZIP을 다운로드한 경우
# 1. 새 버전 다운로드
# 2. .env 파일 백업
# 3. 새 파일로 교체
# 4. .env 파일 복원
# 5. uv sync 실행
```

### 버전 확인

```bash
# 현재 버전 확인
uv run naver-blog-mcp --version

# 변경 사항 확인
git log --oneline -10
```

---

## 제한 사항

현재 버전의 알려진 제한 사항:

1. **Markdown 미지원**: 네이버 블로그가 Markdown을 지원하지 않음
2. **글 삭제 비활성화**: 안전을 위해 일부러 비활성화함
3. **CAPTCHA 수동 해결**: 자동 CAPTCHA 해결 불가
4. **단일 계정**: 한 번에 하나의 계정만 사용 가능

---

## 지원 및 문의

### 문서

- [설치 가이드](./installation-guide.md)
- [Claude Desktop 가이드](./claude-desktop-guide.md)
- [사용자 가이드](./user-guide.md)
- [아키텍처 문서](./architecture.md)

### 이슈 보고

버그나 기능 요청은 [GitHub Issues](https://github.com/space-cap/naver-blog-mcp/issues)에 등록해주세요.

### 커뮤니티

- GitHub Discussions (준비 중)
- 블로그 (준비 중)

---

## 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 [LICENSE](../LICENSE) 파일을 참조하세요.

---

## 기여

기여는 언제나 환영합니다!

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

자세한 내용은 [CONTRIBUTING.md](../CONTRIBUTING.md)를 참조하세요 (준비 중).

---

## 감사의 말

- **Anthropic**: Claude 및 MCP 프로토콜 개발
- **Microsoft**: Playwright 브라우저 자동화 도구
- **커뮤니티**: 버그 리포트 및 피드백

---

**마지막 업데이트**: 2025-11-05

**프로젝트 홈페이지**: https://github.com/space-cap/naver-blog-mcp
