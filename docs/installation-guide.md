# 설치 및 설정 가이드

네이버 블로그 MCP 서버의 설치 및 설정 방법을 안내합니다.

## 목차

1. [시스템 요구사항](#시스템-요구사항)
2. [사전 준비](#사전-준비)
3. [설치 방법](#설치-방법)
4. [환경 설정](#환경-설정)
5. [실행 및 테스트](#실행-및-테스트)
6. [MCP 클라이언트 연동](#mcp-클라이언트-연동)
7. [문제 해결](#문제-해결)

---

## 시스템 요구사항

### 필수 요구사항
- **Python**: 3.13 이상
- **운영체제**: Windows, macOS, Linux
- **메모리**: 최소 2GB RAM
- **디스크 공간**: 최소 500MB (Chromium 브라우저 포함)

### 선택 요구사항
- **MCP 클라이언트**: Claude Desktop, Continue 등
- **네이버 계정**: 블로그가 개설된 네이버 계정

---

## 사전 준비

### 1. Python 설치 확인

```bash
python --version
```

Python 3.13 이상이 설치되어 있어야 합니다. 설치가 안 되어 있다면:
- **Windows**: [python.org](https://www.python.org/downloads/)에서 다운로드
- **macOS**: `brew install python@3.13`
- **Linux**: `sudo apt install python3.13`

### 2. uv 패키지 매니저 설치

```bash
# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

설치 후 터미널을 재시작하고 확인:
```bash
uv --version
```

---

## 설치 방법

### 방법 1: Git Clone (권장)

```bash
# 1. 저장소 복제
git clone https://github.com/YOUR_USERNAME/naver-blog-mcp.git
cd naver-blog-mcp

# 2. 의존성 설치
uv sync

# 3. Playwright 브라우저 설치
uv run playwright install chromium
```

### 방법 2: PyPI에서 설치 (배포 후)

```bash
# 1. 패키지 설치
uv pip install naver-blog-mcp

# 2. Playwright 브라우저 설치
uv run playwright install chromium
```

---

## 환경 설정

### 1. .env 파일 생성

프로젝트 루트 디렉토리에 `.env` 파일을 생성합니다:

```bash
# Windows
copy .env.example .env

# macOS/Linux
cp .env.example .env
```

### 2. .env 파일 편집

```env
# 네이버 계정 정보 (필수)
NAVER_BLOG_ID=your_naver_id
NAVER_BLOG_PASSWORD=your_password

# Playwright 설정 (선택)
HEADLESS=false              # true로 설정 시 브라우저 숨김
SLOW_MO=100                 # 자동화 속도 조절 (ms)

# 로깅 설정 (선택)
LOG_LEVEL=INFO              # DEBUG, INFO, WARNING, ERROR
```

### 3. 환경 변수 설명

| 변수명 | 필수 | 기본값 | 설명 |
|--------|------|--------|------|
| `NAVER_BLOG_ID` | ✅ | - | 네이버 아이디 |
| `NAVER_BLOG_PASSWORD` | ✅ | - | 네이버 비밀번호 |
| `HEADLESS` | ❌ | `false` | 브라우저 표시 여부 |
| `SLOW_MO` | ❌ | `100` | 자동화 속도 (0~1000ms) |
| `LOG_LEVEL` | ❌ | `INFO` | 로그 레벨 |

### 4. 보안 주의사항

⚠️ **중요**: `.env` 파일은 절대 Git에 커밋하지 마세요!

- `.env` 파일에 실제 계정 정보 입력
- `.gitignore`에 `.env` 포함 확인
- 공개 저장소에 업로드 금지

---

## 실행 및 테스트

### 1. 독립 실행 모드

```bash
# MCP 서버 직접 실행
uv run naver-blog-mcp
```

### 2. 기능 테스트

```bash
# 이미지 업로드 테스트
uv run python tests/test_image_upload.py

# 에러 처리 테스트
uv run python tests/test_error_handling.py

# 글 작성 테스트
uv run python tests/test_post_write.py
```

### 3. 로그 확인

실행 중 로그는 콘솔에 출력됩니다:

```
[INFO] 네이버 로그인 시작
[INFO] 세션 저장됨: playwright-state/auth.json
[INFO] 글 작성 페이지 접근 성공
[INFO] 제목 입력 완료: 테스트 제목
[INFO] 본문 입력 완료
[INFO] 글 작성 완료
```

---

## MCP 클라이언트 연동

### Claude Desktop 연동

#### 1. Claude Desktop 설정 파일 열기

- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

#### 2. MCP 서버 설정 추가

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
        "NAVER_BLOG_ID": "your_naver_id",
        "NAVER_BLOG_PASSWORD": "your_password",
        "HEADLESS": "true",
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

⚠️ **주의**: `--directory` 경로를 실제 프로젝트 경로로 변경하세요.

#### 3. Claude Desktop 재시작

설정 파일 저장 후 Claude Desktop을 완전히 종료하고 재시작합니다.

#### 4. 연결 확인

Claude Desktop에서:
```
네이버 블로그 카테고리 목록을 보여줘
```

성공적으로 카테고리가 표시되면 연동 완료!

### Continue (VS Code) 연동

#### 1. Continue 설정 파일 열기

VS Code에서 `Ctrl/Cmd + Shift + P` → "Continue: Open config.json"

#### 2. MCP 서버 설정 추가

```json
{
  "mcpServers": [
    {
      "name": "naver-blog",
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/naver-blog-mcp",
        "run",
        "naver-blog-mcp"
      ],
      "env": {
        "NAVER_BLOG_ID": "your_naver_id",
        "NAVER_BLOG_PASSWORD": "your_password"
      }
    }
  ]
}
```

---

## 문제 해결

### 1. "uv: command not found"

**원인**: uv가 설치되지 않았거나 PATH에 추가되지 않음

**해결**:
```bash
# uv 재설치
curl -LsSf https://astral.sh/uv/install.sh | sh

# 터미널 재시작 후 확인
uv --version
```

### 2. "Playwright 브라우저를 찾을 수 없습니다"

**원인**: Chromium 브라우저가 설치되지 않음

**해결**:
```bash
uv run playwright install chromium
```

### 3. "로그인 실패" 또는 "인증 오류"

**원인**: 네이버 계정 정보가 잘못되었거나 2단계 인증 활성화됨

**해결**:
1. `.env` 파일의 아이디/비밀번호 확인
2. 네이버 2단계 인증 비활성화
3. 네이버 계정 보안 설정에서 "자동 로그인 방지" 해제

### 4. "iframe을 찾을 수 없습니다"

**원인**: 네이버 블로그 UI가 변경됨

**해결**:
```bash
# 디버그 모드로 실행하여 UI 구조 확인
HEADLESS=false LOG_LEVEL=DEBUG uv run naver-blog-mcp
```

브라우저가 열리면 수동으로 확인 후 `src/automation/selectors.py` 업데이트

### 5. "이미지 업로드 실패"

**원인**:
- 이미지 파일 경로가 잘못됨
- 이미지 크기가 10MB 초과
- 지원하지 않는 파일 형식

**해결**:
```bash
# 이미지 정보 확인
uv run python -c "from PIL import Image; img = Image.open('image.jpg'); print(f'크기: {img.size}, 포맷: {img.format}')"
```

지원 형식: JPG, PNG, GIF, BMP, HEIC, HEIF, WebP

### 6. MCP 클라이언트 연결 실패

**원인**: 설정 파일 경로나 JSON 형식 오류

**해결**:
1. 설정 파일 경로 확인
2. JSON 형식 검증 (쉼표, 중괄호 확인)
3. Claude Desktop 로그 확인:
   - **Windows**: `%APPDATA%\Claude\logs\`
   - **macOS**: `~/Library/Logs/Claude/`

### 7. 속도가 너무 느림

**원인**: `SLOW_MO` 값이 너무 높음

**해결**:
```env
# .env 파일 수정
SLOW_MO=0  # 0으로 설정하면 최고 속도
```

---

## 추가 리소스

- [사용자 가이드](user-guide.md) - MCP Tool 사용법
- [아키텍처 문서](architecture.md) - 기술 구조 이해
- [진행 상황](progress.md) - 구현 현황
- [GitHub Issues](https://github.com/YOUR_USERNAME/naver-blog-mcp/issues) - 버그 제보

---

## 다음 단계

설치가 완료되었다면:

1. ✅ [사용자 가이드](user-guide.md)에서 기본 사용법 확인
2. ✅ 테스트 글을 작성해보기
3. ✅ MCP 클라이언트에서 실제 사용해보기

---

**문서 버전**: 1.0
**최종 업데이트**: 2025-11-04
