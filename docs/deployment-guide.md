# 네이버 블로그 MCP 서버 배포 가이드

이 문서는 네이버 블로그 MCP 서버를 다른 사용자에게 배포하고 설치하는 방법을 안내합니다.

## 📋 목차

1. [사전 요구사항](#사전-요구사항)
2. [설치 방법](#설치-방법)
3. [Claude Desktop 연동](#claude-desktop-연동)
4. [사용 가능한 기능](#사용-가능한-기능)
5. [문제 해결](#문제-해결)
6. [보안 고려사항](#보안-고려사항)

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
