# PyPI 배포 가이드

네이버 블로그 MCP 서버를 PyPI (Python Package Index)에 배포하는 상세 가이드입니다.

## 📋 목차

1. [PyPI란?](#pypi란)
2. [배포 전 준비사항](#배포-전-준비사항)
3. [PyPI 계정 설정](#pypi-계정-설정)
4. [패키지 빌드](#패키지-빌드)
5. [TestPyPI로 테스트](#testpypi로-테스트)
6. [실제 PyPI 배포](#실제-pypi-배포)
7. [GitHub Actions 자동 배포](#github-actions-자동-배포)
8. [배포 후 확인](#배포-후-확인)
9. [업데이트 및 버전 관리](#업데이트-및-버전-관리)
10. [문제 해결](#문제-해결)

---

## PyPI란?

**PyPI (Python Package Index)**는 Python 패키지를 공유하는 공식 저장소입니다.

### 장점
- ✅ 사용자가 `pip install naver-blog-mcp`로 한 줄로 설치
- ✅ 의존성 자동 해결
- ✅ 전 세계 Python 개발자에게 노출
- ✅ 버전 관리 자동화
- ✅ 다운로드 통계 제공

### PyPI vs TestPyPI

| 구분 | PyPI | TestPyPI |
|------|------|----------|
| 용도 | 프로덕션 배포 | 테스트 전용 |
| URL | https://pypi.org | https://test.pypi.org |
| 패키지 삭제 | 불가능 (deprecated만 가능) | 가능 |
| 사용 | `pip install` | `pip install --index-url` |

---

## 배포 전 준비사항

### 1. 프로젝트 파일 점검

#### 필수 파일 체크리스트
- [ ] `pyproject.toml` - 패키지 메타데이터
- [ ] `README.md` - 프로젝트 설명 (PyPI 홈페이지에 표시)
- [ ] `LICENSE` - 라이선스 파일 (MIT 권장)
- [ ] `CHANGELOG.md` - 변경 이력
- [ ] `src/naver_blog_mcp/__init__.py` - 버전 정보

#### pyproject.toml 검증

```toml
[project]
name = "naver-blog-mcp"
version = "0.1.0"  # 버전 확인!
description = "Playwright-based MCP server for Naver Blog automation"
authors = [
    {name = "Your Name", email = "your.email@example.com"}
]
readme = "README.md"  # PyPI에 표시될 설명
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

# PyPI 링크
[project.urls]
Homepage = "https://github.com/space-cap/naver-blog-mcp"
Documentation = "https://github.com/space-cap/naver-blog-mcp/blob/main/README.md"
Repository = "https://github.com/space-cap/naver-blog-mcp"
Issues = "https://github.com/space-cap/naver-blog-mcp/issues"
Changelog = "https://github.com/space-cap/naver-blog-mcp/blob/main/CHANGELOG.md"

# CLI 진입점
[project.scripts]
naver-blog-mcp = "naver_blog_mcp.server:main"
```

**중요 사항:**
- `name`: PyPI에서 유일해야 함 (중복 불가)
- `version`: Semantic Versioning 준수
- `readme`: 반드시 존재해야 함
- `license`: 명확히 명시
- `classifiers`: PyPI 검색에 사용됨

### 2. README.md 최적화

PyPI는 README.md를 패키지 홈페이지로 표시합니다.

**포함할 내용:**
```markdown
# 네이버 블로그 MCP 서버

간단한 설명 (1-2줄)

## 주요 기능
- 기능 1
- 기능 2

## 설치
\`\`\`bash
pip install naver-blog-mcp
\`\`\`

## 빠른 시작
\`\`\`bash
# 설정
export NAVER_BLOG_ID=your_id
export NAVER_BLOG_PASSWORD=your_password

# 실행
naver-blog-mcp
\`\`\`

## 문서
- [사용자 가이드](링크)
- [API 문서](링크)

## 라이선스
MIT
```

### 3. LICENSE 파일

MIT 라이선스 예시:
```
MIT License

Copyright (c) 2025 [Your Name]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## PyPI 계정 설정

### 1. PyPI 계정 생성

#### 실제 PyPI
1. https://pypi.org/account/register/ 접속
2. 계정 정보 입력
   - Username
   - Email (인증 필요)
   - Password
3. 이메일 인증 완료

#### TestPyPI (테스트용)
1. https://test.pypi.org/account/register/ 접속
2. 별도 계정 생성 (PyPI와 다름!)

### 2. API Token 생성

**왜 API Token?**
- 비밀번호 대신 토큰 사용 (더 안전)
- 토큰별 권한 설정 가능
- 언제든지 취소 가능

#### PyPI Token 생성 단계

1. **PyPI 로그인** → Account settings

2. **API tokens** 섹션으로 이동

3. **"Add API token"** 클릭

4. **Token 정보 입력:**
   - Token name: `naver-blog-mcp-deploy`
   - Scope:
     - `Entire account` (모든 패키지)
     - 또는 `Project: naver-blog-mcp` (특정 패키지만)

5. **"Add token"** 클릭

6. **토큰 복사 및 저장**
   ```
   pypi-AgEIcHlwaS5vcmc...생략...
   ```
   ⚠️ **중요**: 이 페이지를 벗어나면 다시 볼 수 없습니다!

7. **안전한 곳에 저장:**
   - 비밀번호 관리자 (1Password, Bitwarden 등)
   - 또는 `.pypirc` 파일 (로컬 전용)

#### TestPyPI Token (별도)

동일한 과정을 https://test.pypi.org 에서 반복

### 3. `.pypirc` 파일 설정 (선택사항)

로컬에서 자동 인증하려면:

**위치:**
- Linux/macOS: `~/.pypirc`
- Windows: `%USERPROFILE%\.pypirc`

**내용:**
```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-AgEIcHlwaS5vcmc...YOUR_REAL_TOKEN...

[testpypi]
username = __token__
password = pypi-AgEIcHlwaS5vcmcC...YOUR_TEST_TOKEN...
```

**보안 주의:**
```bash
# 파일 권한 제한 (Linux/macOS)
chmod 600 ~/.pypirc

# Git에 추가하지 않도록 확인
echo ".pypirc" >> ~/.gitignore
```

---

## 패키지 빌드

### 1. 빌드 도구 설치

```bash
# uv 사용 (권장)
uv add --dev build twine

# 또는 pip 사용
pip install build twine
```

### 2. 빌드 전 정리

```bash
# 이전 빌드 파일 삭제
rm -rf dist/ build/ *.egg-info

# Windows에서
rmdir /s /q dist build
del /s /q *.egg-info

# Windows 예약어 파일 제거 (중요!)
rm nul 2>/dev/null || true  # Linux/macOS
del nul 2>nul || exit /b 0  # Windows
```

### 3. 패키지 빌드

```bash
# uv 사용
uv run python -m build

# 또는 직접 실행
python -m build
```

**출력:**
```
* Creating isolated environment: venv+pip...
* Installing packages in isolated environment:
  - hatchling
* Getting build dependencies for sdist...
* Building sdist...
* Building wheel from sdist
* Creating isolated environment: venv+pip...
* Installing packages in isolated environment:
  - hatchling
* Getting build dependencies for wheel...
* Building wheel...
Successfully built naver_blog_mcp-0.1.0.tar.gz and naver_blog_mcp-0.1.0-py3-none-any.whl
```

### 4. 빌드 결과 확인

```bash
ls -lh dist/
```

**예상 출력:**
```
naver_blog_mcp-0.1.0-py3-none-any.whl  (39KB)  ← Wheel 패키지
naver_blog_mcp-0.1.0.tar.gz           (166KB) ← Source 패키지
```

**파일 설명:**
- `.whl` (Wheel): 빠른 설치용 바이너리 패키지
- `.tar.gz` (Source): 소스 코드 패키지

### 5. 빌드 검증

```bash
# twine으로 패키지 검증
uv run twine check dist/*
```

**성공 시:**
```
Checking dist/naver_blog_mcp-0.1.0-py3-none-any.whl: PASSED
Checking dist/naver_blog_mcp-0.1.0.tar.gz: PASSED
```

**실패 시 확인사항:**
- README.md 형식 오류
- pyproject.toml 메타데이터 누락
- LICENSE 파일 없음

---

## TestPyPI로 테스트

**왜 TestPyPI?**
- 실수로 잘못된 패키지 업로드 방지
- 설치 테스트
- 메타데이터 확인

### 1. TestPyPI 업로드

```bash
uv run twine upload --repository testpypi dist/*
```

**인터랙티브 인증 (API Token 사용):**
```
Enter your username: __token__
Enter your password: [TestPyPI API 토큰 붙여넣기]
```

**또는 환경 변수 사용:**
```bash
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-AgEIcHlwaS5vcmcC...TEST_TOKEN...

uv run twine upload --repository testpypi dist/*
```

**성공 시:**
```
Uploading distributions to https://test.pypi.org/legacy/
Uploading naver_blog_mcp-0.1.0-py3-none-any.whl
100% ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 39.0/39.0 kB • 00:00
Uploading naver_blog_mcp-0.1.0.tar.gz
100% ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 166.0/166.0 kB • 00:00

View at:
https://test.pypi.org/project/naver-blog-mcp/0.1.0/
```

### 2. TestPyPI에서 확인

브라우저에서 확인:
```
https://test.pypi.org/project/naver-blog-mcp/
```

**확인 항목:**
- ✅ 프로젝트 설명이 올바르게 표시되는가?
- ✅ 설치 명령어가 올바른가?
- ✅ 링크들이 제대로 작동하는가?
- ✅ 라이선스가 표시되는가?
- ✅ Classifiers가 올바른가?

### 3. TestPyPI에서 설치 테스트

```bash
# 새로운 가상환경 생성
python -m venv test-env
source test-env/bin/activate  # Linux/macOS
test-env\Scripts\activate     # Windows

# TestPyPI에서 설치
pip install --index-url https://test.pypi.org/simple/ \
    --extra-index-url https://pypi.org/simple/ \
    naver-blog-mcp

# 설치 확인
naver-blog-mcp --version

# 실행 테스트
naver-blog-mcp --help
```

**주의:**
- `--extra-index-url https://pypi.org/simple/`이 필요한 이유:
  - 의존성(playwright, pydantic 등)은 실제 PyPI에 있음
  - TestPyPI는 패키지가 적음

### 4. 문제 발견 시

**문제를 수정하고 다시 업로드:**

1. 버전 번호 변경 (같은 버전 재업로드 불가!)
   ```toml
   version = "0.1.1"  # 0.1.0 → 0.1.1
   ```

2. 다시 빌드 및 업로드
   ```bash
   rm -rf dist/
   uv run python -m build
   uv run twine upload --repository testpypi dist/*
   ```

---

## 실제 PyPI 배포

**⚠️ 주의사항:**
- PyPI에 업로드한 패키지는 **삭제할 수 없습니다**
- 같은 버전을 다시 업로드할 수 없습니다
- 반드시 TestPyPI에서 테스트 후 진행

### 1. 최종 점검

- [ ] TestPyPI 테스트 완료
- [ ] README.md 최종 검토
- [ ] CHANGELOG.md 업데이트
- [ ] 버전 번호 확인 (pyproject.toml)
- [ ] Git 커밋 및 푸시
- [ ] Git 태그 생성

### 2. Git 태그 생성

```bash
# 버전 태그 생성
git tag -a v0.1.0 -m "Release v0.1.0: Initial PyPI release"

# 태그 푸시
git push origin v0.1.0

# 모든 태그 확인
git tag -l
```

### 3. PyPI 업로드

```bash
# 실제 PyPI에 업로드
uv run twine upload dist/*
```

**인증:**
```
Enter your username: __token__
Enter your password: [실제 PyPI API 토큰]
```

**또는 환경 변수:**
```bash
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-AgEIcHlwaS5vcmc...REAL_TOKEN...

uv run twine upload dist/*
```

**성공 시:**
```
Uploading distributions to https://upload.pypi.org/legacy/
Uploading naver_blog_mcp-0.1.0-py3-none-any.whl
100% ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 39.0/39.0 kB • 00:00
Uploading naver_blog_mcp-0.1.0.tar.gz
100% ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 166.0/166.0 kB • 00:00

View at:
https://pypi.org/project/naver-blog-mcp/0.1.0/
```

### 4. PyPI 페이지 확인

```
https://pypi.org/project/naver-blog-mcp/
```

**축하합니다! 🎉**
이제 전 세계 누구나 다음 명령어로 설치할 수 있습니다:
```bash
pip install naver-blog-mcp
```

---

## GitHub Actions 자동 배포

수동 업로드 대신 GitHub Release 시 자동 배포하기

### 1. PyPI API Token을 GitHub Secrets에 저장

1. **GitHub 저장소** → Settings → Secrets and variables → Actions

2. **"New repository secret"** 클릭

3. **Secret 추가:**
   - Name: `PYPI_API_TOKEN`
   - Value: `pypi-AgEIcHlwaS5vcmc...` (실제 PyPI 토큰)

4. **Save**

### 2. GitHub Actions Workflow 생성

`.github/workflows/publish-to-pypi.yml`:

```yaml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  deploy:
    runs-on: ubuntu-latest
    permissions:
      contents: read

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.13'

      - name: Install uv
        run: |
          curl -LsSf https://astral.sh/uv/install.sh | sh
          echo "$HOME/.cargo/bin" >> $GITHUB_PATH

      - name: Install dependencies
        run: |
          uv sync

      - name: Install build tools
        run: |
          uv pip install build twine

      - name: Build package
        run: |
          uv run python -m build

      - name: Check package
        run: |
          uv run twine check dist/*

      - name: Publish to PyPI
        env:
          TWINE_USERNAME: __token__
          TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
        run: |
          uv run twine upload dist/*
```

### 3. 사용 방법

1. **코드 변경 및 버전 업데이트**
   ```bash
   # pyproject.toml 버전 변경
   version = "0.2.0"

   # 커밋
   git add .
   git commit -m "feat: 새로운 기능 추가"
   git push
   ```

2. **Git 태그 생성**
   ```bash
   git tag -a v0.2.0 -m "Release v0.2.0"
   git push origin v0.2.0
   ```

3. **GitHub Release 생성**
   - GitHub → Releases → "Draft a new release"
   - Tag: `v0.2.0` 선택
   - Release title: `v0.2.0`
   - Description: 변경 사항 기입
   - **"Publish release"** 클릭

4. **자동 배포 시작**
   - GitHub Actions가 자동으로 실행
   - Actions 탭에서 진행 상황 확인
   - 성공 시 PyPI에 자동 업로드됨

### 4. 배포 상태 확인

GitHub Actions 로그:
```
Actions → Publish to PyPI → 최신 실행
```

성공 시:
```
✅ Build package
✅ Check package
✅ Publish to PyPI
```

---

## 배포 후 확인

### 1. PyPI 페이지 확인

```
https://pypi.org/project/naver-blog-mcp/
```

**확인 항목:**
- 최신 버전이 표시되는가?
- README가 올바르게 렌더링되는가?
- 다운로드 통계가 작동하는가?

### 2. 설치 테스트

```bash
# 새 환경에서 설치
pip install naver-blog-mcp

# 버전 확인
naver-blog-mcp --version

# 실행 확인
naver-blog-mcp --help
```

### 3. README 업데이트

GitHub README에 PyPI 배지 추가:

```markdown
[![PyPI version](https://img.shields.io/pypi/v/naver-blog-mcp)](https://pypi.org/project/naver-blog-mcp/)
[![Downloads](https://pepy.tech/badge/naver-blog-mcp)](https://pepy.tech/project/naver-blog-mcp)
[![Python versions](https://img.shields.io/pypi/pyversions/naver-blog-mcp)](https://pypi.org/project/naver-blog-mcp/)
[![License](https://img.shields.io/pypi/l/naver-blog-mcp)](https://github.com/space-cap/naver-blog-mcp/blob/main/LICENSE)
```

### 4. 사용자 문서 업데이트

설치 방법을 PyPI 기반으로 간소화:

```markdown
## 설치

```bash
pip install naver-blog-mcp
```

또는 최신 개발 버전:
```bash
pip install git+https://github.com/space-cap/naver-blog-mcp.git
```
```

---

## 업데이트 및 버전 관리

### Semantic Versioning

```
MAJOR.MINOR.PATCH (예: 1.2.3)
```

- **MAJOR**: 호환성이 깨지는 변경 (Breaking Changes)
- **MINOR**: 새 기능 추가 (하위 호환)
- **PATCH**: 버그 수정

### 버전 업데이트 프로세스

#### 1. 코드 변경

```bash
# 새 기능 개발
git checkout -b feature/new-feature
# ... 코드 작성 ...
git commit -m "feat: 새로운 기능 추가"
git push origin feature/new-feature
```

#### 2. Pull Request 및 병합

#### 3. 버전 번호 결정

- 버그 수정만? → PATCH (0.1.0 → 0.1.1)
- 새 기능 추가? → MINOR (0.1.0 → 0.2.0)
- Breaking Change? → MAJOR (0.1.0 → 1.0.0)

#### 4. 버전 업데이트

**pyproject.toml:**
```toml
version = "0.2.0"
```

**CHANGELOG.md:**
```markdown
## [0.2.0] - 2025-11-06

### Added
- 새로운 기능 A
- 새로운 기능 B

### Fixed
- 버그 C 수정
- 버그 D 수정

### Changed
- 변경 사항 E
```

#### 5. 커밋 및 태그

```bash
git add pyproject.toml CHANGELOG.md
git commit -m "chore: bump version to 0.2.0"
git push

git tag -a v0.2.0 -m "Release v0.2.0"
git push origin v0.2.0
```

#### 6. GitHub Release 생성

- CHANGELOG.md 내용 복사
- GitHub Release 생성
- GitHub Actions가 자동으로 PyPI 배포

### 통계 확인

```
https://pypistats.org/packages/naver-blog-mcp
```

다운로드 수, 사용자 통계 등 확인 가능

---

## 문제 해결

### 문제 1: 패키지 이름 중복

**에러:**
```
The name 'naver-blog-mcp' is too similar to an existing project
```

**해결:**
- 다른 이름 선택: `naver-blog-mcp-server`, `mcp-naver-blog` 등
- PyPI에서 사용 가능한 이름 확인: https://pypi.org/project/[이름]/

### 문제 2: 버전 충돌

**에러:**
```
File already exists
```

**원인:**
- 같은 버전을 다시 업로드하려고 함

**해결:**
```bash
# 버전 번호 변경
version = "0.1.1"  # 0.1.0 → 0.1.1

# 다시 빌드
rm -rf dist/
uv run python -m build
uv run twine upload dist/*
```

### 문제 3: README 렌더링 실패

**에러:**
```
The description failed to render
```

**원인:**
- README.md 형식 오류
- 지원하지 않는 Markdown 문법

**해결:**
```bash
# twine check로 사전 검증
uv run twine check dist/*

# README.md 수정 후 재빌드
```

### 문제 4: 의존성 설치 실패

**에러:**
```
Could not find a version that satisfies the requirement playwright>=1.55.0
```

**원인:**
- Python 버전 제약 (`requires-python`)이 너무 높음

**해결:**
```toml
# pyproject.toml
requires-python = ">=3.10"  # 3.13 → 3.10으로 완화
```

### 문제 5: 인증 실패

**에러:**
```
Invalid or non-existent authentication information
```

**해결:**
```bash
# API Token 재확인
# 1. __token__ (username)
# 2. pypi-AgEI... (password)

# 환경 변수로 시도
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=your_token_here
uv run twine upload dist/*
```

### 문제 6: Windows에서 빌드 실패

**에러:**
```
OSError: [WinError 87] 매개 변수가 틀립니다: '...nul'
```

**해결:**
```bash
# nul 파일 삭제 (Windows 예약어)
del nul 2>nul

# 다시 빌드
uv run python -m build
```

---

## 체크리스트

### 첫 배포 전

- [ ] PyPI 계정 생성 완료
- [ ] API Token 생성 및 저장
- [ ] TestPyPI 계정 생성 완료
- [ ] pyproject.toml 검증
- [ ] README.md 작성
- [ ] LICENSE 파일 추가
- [ ] CHANGELOG.md 작성
- [ ] .gitignore에 dist/, build/ 추가

### 빌드 전

- [ ] 버전 번호 업데이트
- [ ] CHANGELOG.md 업데이트
- [ ] 이전 빌드 파일 삭제 (`rm -rf dist/`)
- [ ] Windows 예약어 파일 제거 (`del nul`)
- [ ] Git 커밋 완료

### 배포 전

- [ ] TestPyPI 업로드 테스트
- [ ] TestPyPI에서 설치 테스트
- [ ] README 렌더링 확인
- [ ] Git 태그 생성

### 배포 후

- [ ] PyPI 페이지 확인
- [ ] 실제 설치 테스트
- [ ] GitHub Release 생성
- [ ] README에 배지 추가
- [ ] 사용자 문서 업데이트

---

## 추가 리소스

### 공식 문서
- [PyPI 공식 가이드](https://packaging.python.org/tutorials/packaging-projects/)
- [Twine 문서](https://twine.readthedocs.io/)
- [Semantic Versioning](https://semver.org/)

### 유용한 도구
- [PyPI Stats](https://pypistats.org/)
- [Libraries.io](https://libraries.io/)
- [JSON Lint](https://jsonlint.com/) - pyproject.toml 검증

### 커뮤니티
- [Python Packaging Discourse](https://discuss.python.org/c/packaging/14)
- [PyPA GitHub](https://github.com/pypa)

---

**마지막 업데이트**: 2025-11-06

**작성자**: Claude Code

**프로젝트**: https://github.com/space-cap/naver-blog-mcp
