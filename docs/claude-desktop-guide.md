# Claude Desktop 설정 가이드

네이버 블로그 MCP 서버를 Claude Desktop과 연동하는 방법을 상세히 안내합니다.

## 목차

1. [개요](#개요)
2. [사전 준비](#사전-준비)
3. [설정 파일 위치](#설정-파일-위치)
4. [설정 방법](#설정-방법)
5. [실전 사용 예제](#실전-사용-예제)
6. [고급 설정](#고급-설정)
7. [문제 해결](#문제-해결)
8. [보안 고려사항](#보안-고려사항)

---

## 개요

### Claude Desktop이란?

Claude Desktop은 Anthropic의 공식 데스크톱 애플리케이션으로, MCP (Model Context Protocol)를 통해 외부 도구와 연동할 수 있습니다.

### 연동 후 가능한 기능

네이버 블로그 MCP 서버를 연동하면 Claude Desktop에서:

- ✅ 네이버 블로그 글 작성 (제목, 본문, 카테고리, 태그)
- ✅ 이미지 업로드 (단일/다중)
- ✅ 글 삭제
- ✅ 카테고리 목록 조회
- ✅ 자연어로 명령 ("블로그에 글 써줘")

---

## 사전 준비

### 1. Claude Desktop 설치

아직 설치하지 않았다면:

1. [Claude Desktop 다운로드](https://claude.ai/download)
2. 운영체제에 맞는 설치 파일 다운로드
3. 설치 및 로그인

### 2. 네이버 블로그 MCP 서버 설치

먼저 MCP 서버가 설치되어 있어야 합니다:

```bash
# 저장소 복제
git clone https://github.com/YOUR_USERNAME/naver-blog-mcp.git
cd naver-blog-mcp

# 의존성 설치
uv sync

# Playwright 브라우저 설치
uv run playwright install chromium
```

자세한 내용은 [설치 가이드](installation-guide.md)를 참고하세요.

### 3. 네이버 계정 준비

- 네이버 블로그가 개설된 계정
- 2단계 인증 비활성화 권장 (자동화를 위해)

---

## 설정 파일 위치

### Windows

```
%APPDATA%\Claude\claude_desktop_config.json
```

전체 경로 예시:
```
C:\Users\YourName\AppData\Roaming\Claude\claude_desktop_config.json
```

### macOS

```
~/Library/Application Support/Claude/claude_desktop_config.json
```

### Linux

```
~/.config/Claude/claude_desktop_config.json
```

---

## 설정 방법

### 방법 1: GUI로 파일 열기 (권장)

#### Windows

1. `Win + R` 키 누르기
2. `%APPDATA%\Claude` 입력 후 엔터
3. `claude_desktop_config.json` 파일을 메모장 또는 VS Code로 열기

#### macOS

1. Finder 열기
2. `Cmd + Shift + G` 누르기
3. `~/Library/Application Support/Claude` 입력 후 이동
4. `claude_desktop_config.json` 파일 열기

#### Linux

```bash
nano ~/.config/Claude/claude_desktop_config.json
```

### 방법 2: 명령어로 파일 열기

#### Windows (PowerShell)

```powershell
notepad "$env:APPDATA\Claude\claude_desktop_config.json"
```

#### macOS/Linux

```bash
# VS Code가 설치된 경우
code ~/Library/Application\ Support/Claude/claude_desktop_config.json

# 또는 nano 사용
nano ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

### 설정 파일 내용 작성

#### 기본 설정 (환경 변수 사용)

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

#### macOS/Linux 경로 예시

```json
{
  "mcpServers": {
    "naver-blog": {
      "command": "uv",
      "args": [
        "--directory",
        "/Users/username/projects/naver-blog-mcp",
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

### 설정 항목 설명

| 항목 | 설명 | 예시 |
|------|------|------|
| `command` | 실행할 명령어 | `"uv"` |
| `args` | 명령어 인자 배열 | `["--directory", "...", "run", "naver-blog-mcp"]` |
| `--directory` | 프로젝트 경로 (절대 경로) | `"C:/path/to/project"` |
| `env` | 환경 변수 | 아래 환경 변수 표 참고 |

### 환경 변수 설명

| 변수명 | 필수 | 설명 | 예시 |
|--------|------|------|------|
| `NAVER_BLOG_ID` | ✅ | 네이버 아이디 | `"myid"` |
| `NAVER_BLOG_PASSWORD` | ✅ | 네이버 비밀번호 | `"mypassword"` |
| `HEADLESS` | ❌ | 브라우저 숨김 (`true`/`false`) | `"true"` |
| `SLOW_MO` | ❌ | 자동화 속도 (ms) | `"100"` |
| `LOG_LEVEL` | ❌ | 로그 레벨 | `"INFO"` |

---

## 실전 사용 예제

설정이 완료되면 Claude Desktop을 재시작한 후 아래와 같이 사용할 수 있습니다.

### 1. 카테고리 목록 조회

**사용자**:
```
네이버 블로그 카테고리 목록을 보여줘
```

**Claude 응답**:
```
네이버 블로그의 카테고리 목록입니다:

1. 일상
2. 여행
3. 개발
4. 리뷰
```

### 2. 간단한 글 작성

**사용자**:
```
네이버 블로그에 "오늘의 일기"라는 제목으로 글을 써줘.
본문은 "오늘 날씨가 정말 좋았다."로 해줘.
```

**Claude**:
- `naver_blog_create_post` 도구 자동 호출
- 제목, 본문 자동 입력
- 글 작성 완료 후 URL 반환

### 3. 이미지 포함 글 작성

**사용자**:
```
네이버 블로그에 여행 후기를 작성해줘.
제목: 제주도 여행 후기
본문: 제주도 여행이 정말 즐거웠습니다.
이미지: C:/Pictures/jeju1.jpg, C:/Pictures/jeju2.jpg
카테고리: 여행
태그: 제주도, 여행, 힐링
```

**Claude**:
- 이미지 2개 자동 업로드
- 카테고리 설정
- 태그 추가
- 글 발행

### 4. 글 삭제

**사용자**:
```
이 글을 삭제해줘: https://blog.naver.com/myid/223123456789
```

**Claude**:
- `naver_blog_delete_post` 도구 호출
- 글 삭제 완료

### 5. 연속 작업

**사용자**:
```
먼저 카테고리 목록을 보여주고,
"개발" 카테고리에 "Python 팁 모음"이라는 글을 작성해줘.
태그는 "Python, 개발, 팁"으로 설정해줘.
```

**Claude**:
1. 카테고리 목록 조회
2. "개발" 카테고리 확인
3. 글 작성 및 태그 설정

---

## 고급 설정

### 1. .env 파일 사용 (권장)

설정 파일에 비밀번호를 직접 저장하지 않고 `.env` 파일 사용:

#### .env 파일 생성

프로젝트 루트에 `.env` 파일:

```env
NAVER_BLOG_ID=your_naver_id
NAVER_BLOG_PASSWORD=your_password
HEADLESS=true
LOG_LEVEL=INFO
```

#### Claude Desktop 설정

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
      ]
    }
  }
}
```

이 경우 환경 변수는 `.env` 파일에서 자동으로 로드됩니다.

### 2. 디버그 모드

문제가 발생할 때 디버그 모드로 실행:

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
        "HEADLESS": "false",
        "SLOW_MO": "500",
        "LOG_LEVEL": "DEBUG"
      }
    }
  }
}
```

- `HEADLESS=false`: 브라우저가 화면에 표시됨
- `SLOW_MO=500`: 동작이 느려져서 관찰 가능
- `LOG_LEVEL=DEBUG`: 상세한 로그 출력

### 3. 여러 MCP 서버 동시 사용

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
        "NAVER_BLOG_PASSWORD": "your_password"
      }
    },
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "C:/Users/YourName/Documents"
      ]
    },
    "github": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-github"
      ],
      "env": {
        "GITHUB_TOKEN": "ghp_your_token"
      }
    }
  }
}
```

### 4. 프로필별 설정

개인용과 업무용 블로그를 분리:

```json
{
  "mcpServers": {
    "naver-blog-personal": {
      "command": "uv",
      "args": [
        "--directory",
        "C:/workdir/naver-blog-mcp",
        "run",
        "naver-blog-mcp"
      ],
      "env": {
        "NAVER_BLOG_ID": "personal_id",
        "NAVER_BLOG_PASSWORD": "personal_password"
      }
    },
    "naver-blog-work": {
      "command": "uv",
      "args": [
        "--directory",
        "C:/workdir/naver-blog-mcp",
        "run",
        "naver-blog-mcp"
      ],
      "env": {
        "NAVER_BLOG_ID": "work_id",
        "NAVER_BLOG_PASSWORD": "work_password"
      }
    }
  }
}
```

사용 시:
```
개인 블로그에 글 써줘 (naver-blog-personal 사용)
업무 블로그에 공지사항 올려줘 (naver-blog-work 사용)
```

---

## 문제 해결

### 1. "MCP 서버를 찾을 수 없습니다"

**증상**: Claude Desktop에서 네이버 블로그 도구가 보이지 않음

**해결**:

1. 설정 파일 경로 확인
   ```bash
   # Windows
   dir "%APPDATA%\Claude\claude_desktop_config.json"

   # macOS/Linux
   ls -la ~/Library/Application\ Support/Claude/claude_desktop_config.json
   ```

2. JSON 형식 검증
   - [JSONLint](https://jsonlint.com/)에서 JSON 검증
   - 쉼표, 중괄호, 따옴표 확인

3. Claude Desktop 완전히 재시작
   - 트레이 아이콘에서 완전 종료
   - 다시 실행

### 2. "command not found: uv"

**증상**: MCP 서버 시작 실패

**해결**:

```bash
# uv 설치
curl -LsSf https://astral.sh/uv/install.sh | sh

# PATH 확인
which uv  # macOS/Linux
where uv  # Windows
```

설치 후 Claude Desktop 재시작 필요

### 3. "로그인 실패" 또는 "인증 오류"

**증상**: 네이버 로그인이 되지 않음

**원인**:
- 잘못된 아이디/비밀번호
- 2단계 인증 활성화
- 네이버 보안 설정

**해결**:

1. 아이디/비밀번호 확인
   ```json
   "env": {
     "NAVER_BLOG_ID": "correct_id",  // 따옴표 확인
     "NAVER_BLOG_PASSWORD": "correct_password"
   }
   ```

2. 네이버 2단계 인증 비활성화
   - 네이버 → 내정보 → 보안설정 → 2단계 인증 끄기

3. "자동 로그인 방지" 해제
   - 네이버 → 내정보 → 보안설정

4. 직접 테스트
   ```bash
   cd C:/workdir/space-cap/naver-blog-mcp
   uv run naver-blog-mcp
   ```

### 4. 경로 오류

**증상**: "directory not found" 오류

**해결**:

- Windows: 슬래시 방향 주의 (`/` 사용)
  ```json
  "C:/workdir/space-cap/naver-blog-mcp"  // ✅ 올바름
  "C:\\workdir\\space-cap\\naver-blog-mcp"  // ❌ JSON에서 에러
  ```

- macOS/Linux: 절대 경로 사용
  ```json
  "/Users/username/projects/naver-blog-mcp"  // ✅ 올바름
  "~/projects/naver-blog-mcp"  // ❌ ~ 확장 안 됨
  ```

### 5. 로그 확인 방법

Claude Desktop 로그 위치:

- **Windows**: `%APPDATA%\Claude\logs\`
- **macOS**: `~/Library/Logs/Claude/`
- **Linux**: `~/.config/Claude/logs/`

최신 로그 파일 열어서 에러 메시지 확인:

```bash
# Windows
notepad "%APPDATA%\Claude\logs\mcp-server-naver-blog.log"

# macOS
tail -f ~/Library/Logs/Claude/mcp-server-naver-blog.log

# Linux
tail -f ~/.config/Claude/logs/mcp-server-naver-blog.log
```

### 6. 브라우저가 계속 열림

**증상**: 매번 브라우저가 새로 열림

**원인**: `HEADLESS=false` 설정

**해결**:

```json
"env": {
  "HEADLESS": "true"  // 브라우저 숨김
}
```

### 7. 너무 느림

**증상**: 글 작성이 너무 오래 걸림

**원인**: `SLOW_MO` 값이 높음

**해결**:

```json
"env": {
  "SLOW_MO": "0"  // 최고 속도
}
```

---

## 보안 고려사항

### 1. 비밀번호 보호

⚠️ **중요**: 설정 파일에 비밀번호가 평문으로 저장됩니다.

**권장 사항**:

1. `.env` 파일 사용 (프로젝트 디렉토리)
2. 파일 권한 설정
   ```bash
   # macOS/Linux
   chmod 600 ~/.config/Claude/claude_desktop_config.json
   chmod 600 /path/to/naver-blog-mcp/.env
   ```

3. 별도 계정 사용
   - 메인 네이버 계정 대신 서브 계정 사용
   - 블로그 관리 권한만 부여

### 2. 설정 파일 백업

```bash
# Windows
copy "%APPDATA%\Claude\claude_desktop_config.json" "%APPDATA%\Claude\claude_desktop_config.json.backup"

# macOS/Linux
cp ~/Library/Application\ Support/Claude/claude_desktop_config.json ~/Library/Application\ Support/Claude/claude_desktop_config.json.backup
```

### 3. Git 저장소에 업로드 금지

프로젝트를 Git으로 관리할 때:

```gitignore
# .gitignore
.env
claude_desktop_config.json
playwright-state/
*.log
```

---

## 설정 템플릿

### Windows 기본 템플릿

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

### macOS 기본 템플릿

```json
{
  "mcpServers": {
    "naver-blog": {
      "command": "uv",
      "args": [
        "--directory",
        "/Users/username/projects/naver-blog-mcp",
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

### Linux 기본 템플릿

```json
{
  "mcpServers": {
    "naver-blog": {
      "command": "uv",
      "args": [
        "--directory",
        "/home/username/projects/naver-blog-mcp",
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

---

## 다음 단계

설정이 완료되었다면:

1. ✅ Claude Desktop 재시작
2. ✅ [사용자 가이드](user-guide.md)에서 사용법 확인
3. ✅ 테스트 글 작성해보기
4. ✅ 실제 블로그 운영에 활용하기

---

## 추가 리소스

- [MCP 공식 문서](https://modelcontextprotocol.io/)
- [Claude Desktop 다운로드](https://claude.ai/download)
- [설치 가이드](installation-guide.md)
- [사용자 가이드](user-guide.md)
- [문제 해결 가이드](installation-guide.md#문제-해결)

---

**문서 버전**: 1.0
**최종 업데이트**: 2025-11-04
**Claude Desktop 지원 버전**: 0.7.0+
