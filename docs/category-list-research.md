# 네이버 블로그 카테고리 조회 기능 구현 가능성 조사

**조사 일자**: 2025-11-04
**조사 목적**: 네이버 블로그 MCP 서버에 카테고리 목록 조회 기능 구현 가능 여부 확인
**결론**: ✅ **구현 가능 (매우 쉬움)**

---

## 목차

1. [조사 배경](#조사-배경)
2. [네이버 블로그 카테고리 시스템](#네이버-블로그-카테고리-시스템)
3. [카테고리 조회 방법](#카테고리-조회-방법)
4. [기술적 구현 가능성](#기술적-구현-가능성)
5. [구현 방안](#구현-방안)
6. [예상 구현 난이도](#예상-구현-난이도)
7. [구현 시 고려사항](#구현-시-고려사항)
8. [결론 및 권장사항](#결론-및-권장사항)

---

## 조사 배경

### 현재 Tool 정의 상태

`src/naver_blog_mcp/mcp/tools.py`에 이미 정의되어 있음:

```python
"naver_blog_list_categories": {
    "name": "naver_blog_list_categories",
    "description": "네이버 블로그의 카테고리 목록을 가져옵니다.",
    "inputSchema": {
        "type": "object",
        "properties": {},
        "required": [],
    },
}
```

### 구현 상태
- ❌ **미구현**: `handle_list_categories()` 함수가 빈 껍데기만 존재
- ⚠️ 현재는 "아직 구현되지 않았습니다" 메시지만 반환

### 필요성
- ⭐⭐⭐⭐⭐ **매우 높음**
- 글 작성 시 카테고리를 지정하려면 **어떤 카테고리가 있는지 알아야 함**
- 현재 MCP Tool로 이미 정의되어 있어 **즉시 구현 필요**

---

## 네이버 블로그 카테고리 시스템

### 카테고리 구조

네이버 블로그는 **2단계 계층 구조**를 지원합니다:

```
블로그 루트
├── 카테고리 1 (1차)
│   ├── 서브카테고리 1-1 (2차)
│   ├── 서브카테고리 1-2 (2차)
│   └── 서브카테고리 1-3 (2차)
├── 카테고리 2 (1차)
│   ├── 서브카테고리 2-1 (2차)
│   └── 서브카테고리 2-2 (2차)
├── ─────────── (구분선)
└── 카테고리 3 (1차)
```

**특징**:
- 최대 2단계 분류 (1차 카테고리 → 2차 서브카테고리)
- 구분선(separator)으로 카테고리 그룹 구분 가능
- 카테고리별로 글 개수 표시

### 카테고리 표시 위치

#### 1. 블로그 사이드바
```
┌─────────────────────┐
│  블로그 홈          │
├─────────────────────┤
│ 📁 전체보기         │
│ 📁 카테고리 1 (15)  │ ← 여기서 조회 가능
│   📄 서브 1-1 (5)   │
│   📄 서브 1-2 (10)  │
│ 📁 카테고리 2 (8)   │
│ ─────────────────   │
│ 📁 카테고리 3 (23)  │
└─────────────────────┘
```

#### 2. 관리자 페이지
```
블로그 관리 → 메뉴·글·동영상 관리 → 블로그 → 카테고리 목록
```

### 카테고리 URL 구조

```
# 블로그 메인 (모든 카테고리 표시)
https://blog.naver.com/{블로그ID}

# 특정 카테고리
https://blog.naver.com/{블로그ID}/category/{카테고리ID}

# 예시
https://blog.naver.com/myid/
https://blog.naver.com/myid/category/123456
```

---

## 카테고리 조회 방법

### 방법 1: 블로그 사이드바에서 조회 (권장)

**접근 경로**:
```
1. 블로그 메인 페이지 접속
   → https://blog.naver.com/{블로그ID}

2. 사이드바에서 카테고리 목록 추출
   → DOM에서 카테고리 링크/텍스트 파싱
```

**예상 DOM 구조**:
```html
<!-- 사이드바 영역 -->
<div class="blog_sidebar">
    <!-- 카테고리 영역 -->
    <div class="category_area">
        <!-- 전체보기 -->
        <a href="/blog_id">전체보기</a>

        <!-- 1차 카테고리 -->
        <div class="category_item">
            <a href="/blog_id/category/123">개발</a>
            <span class="count">(15)</span>

            <!-- 2차 카테고리 -->
            <div class="sub_category">
                <a href="/blog_id/category/124">Python</a>
                <span class="count">(5)</span>
            </div>
            <div class="sub_category">
                <a href="/blog_id/category/125">JavaScript</a>
                <span class="count">(10)</span>
            </div>
        </div>

        <!-- 구분선 -->
        <hr class="separator">

        <!-- 다른 1차 카테고리 -->
        <div class="category_item">
            <a href="/blog_id/category/126">일상</a>
            <span class="count">(23)</span>
        </div>
    </div>
</div>
```

**장점**:
- ✅ 가장 직접적인 방법
- ✅ 공개 페이지에서 접근 가능
- ✅ 카테고리 계층 구조 확인 가능
- ✅ 글 개수도 함께 조회 가능

**단점**:
- ⚠️ DOM 셀렉터가 변경될 수 있음 (대체 셀렉터 필요)

### 방법 2: 블로그 관리 페이지에서 조회

**접근 경로**:
```
1. 네이버 로그인 (이미 구현됨)
2. 블로그 관리 페이지 접속
   → https://blog.naver.com/manage/category
3. 카테고리 관리 화면에서 목록 추출
```

**장점**:
- ✅ 더 구조화된 데이터
- ✅ 카테고리 ID 명확하게 확인 가능
- ✅ 편집 가능한 형태로 표시

**단점**:
- ⚠️ 추가 페이지 이동 필요
- ⚠️ iframe 구조일 가능성

### 방법 3: HTML 파싱 (가장 안정적)

블로그 메인 페이지의 HTML에서 카테고리 메뉴 파싱:

```python
# 페이지 HTML에서 카테고리 추출
html = await page.content()
# BeautifulSoup 또는 정규표현식으로 파싱
```

---

## 기술적 구현 가능성

### ✅ 구현 가능 (매우 쉬움)

| 항목 | 평가 | 비고 |
|------|------|------|
| 기술적 난이도 | ⭐ (매우 쉬움) | DOM 조회만 하면 됨 |
| 구현 시간 | 0.5-1일 | 4-8시간 |
| 안정성 | ⭐⭐⭐⭐ | 공개 정보라 변경 가능성 낮음 |
| 유지보수 | ⭐⭐⭐⭐ | 간단한 구조 |

### 구현 가능 근거

#### 1. **공개 정보**
- 블로그 메인 페이지에서 누구나 볼 수 있음
- 로그인 필요 없음 (더 안정적)
- 정적인 HTML 구조

#### 2. **간단한 작업**
- 페이지 접속 → DOM 조회 → 텍스트 추출
- 복잡한 인터랙션 없음
- 버튼 클릭이나 폼 입력 불필요

#### 3. **기존 코드 재사용**
```python
# 이미 구현된 기능들
✅ 페이지 이동 (page.goto)
✅ DOM 조회 (page.query_selector_all)
✅ 텍스트 추출 (element.text_content)
✅ 에러 처리 (error_handler.py)
```

#### 4. **변경 가능성 낮음**
- 카테고리는 블로그의 핵심 네비게이션
- UI 변경이 상대적으로 적음
- 대체 셀렉터 준비만 하면 됨

---

## 구현 방안

### 아키텍처 설계

```
src/naver_blog_mcp/
├── automation/
│   └── category_actions.py      # 새로 생성 (카테고리 조회 로직)
├── mcp/
│   └── tools.py                 # handle_list_categories() 구현
└── tests/
    └── test_category_list.py    # 카테고리 조회 테스트
```

### 구현 코드 (Pseudo-code)

#### 1. `automation/category_actions.py` (신규 파일)

```python
"""네이버 블로그 카테고리 관련 자동화 기능."""

import logging
from typing import Dict, Any, List, Optional
from playwright.async_api import Page

logger = logging.getLogger(__name__)


class CategoryInfo:
    """카테고리 정보 데이터 클래스."""

    def __init__(
        self,
        name: str,
        url: Optional[str] = None,
        count: Optional[int] = None,
        level: int = 1,
        parent: Optional[str] = None
    ):
        self.name = name
        self.url = url
        self.count = count
        self.level = level  # 1: 1차 카테고리, 2: 2차 카테고리
        self.parent = parent  # 2차 카테고리의 경우 부모 카테고리명

    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환."""
        return {
            "name": self.name,
            "url": self.url,
            "count": self.count,
            "level": self.level,
            "parent": self.parent
        }


async def get_categories(
    page: Page,
    blog_id: Optional[str] = None
) -> Dict[str, Any]:
    """네이버 블로그의 카테고리 목록을 가져옵니다.

    Args:
        page: Playwright Page 객체
        blog_id: 블로그 아이디 (None이면 현재 로그인한 블로그)

    Returns:
        {
            "success": bool,
            "message": str,
            "categories": [
                {
                    "name": str,
                    "url": str,
                    "count": int,
                    "level": int,
                    "parent": str (2차 카테고리의 경우)
                },
                ...
            ]
        }
    """
    try:
        # 1. 블로그 메인 페이지로 이동
        if blog_id:
            blog_url = f"https://blog.naver.com/{blog_id}"
        else:
            # 현재 로그인한 사용자의 블로그
            blog_url = "https://blog.naver.com"

        await page.goto(blog_url, wait_until="networkidle")
        logger.info(f"블로그 페이지 접근: {blog_url}")

        # 2. 카테고리 영역 찾기 (여러 셀렉터 시도)
        category_selectors = [
            ".blog_sidebar .category_area",
            "#category",
            ".category_list",
            "[class*='category']",
        ]

        category_area = None
        for selector in category_selectors:
            try:
                category_area = await page.wait_for_selector(
                    selector,
                    timeout=5000
                )
                if category_area:
                    logger.info(f"카테고리 영역 발견: {selector}")
                    break
            except:
                continue

        if not category_area:
            logger.warning("카테고리 영역을 찾을 수 없습니다")
            return {
                "success": True,
                "message": "카테고리가 없거나 찾을 수 없습니다",
                "categories": []
            }

        # 3. 카테고리 링크 추출
        # 1차 카테고리 셀렉터
        category_link_selectors = [
            "a[href*='/category/']",
            ".category_item a",
            ".category_link",
        ]

        categories = []

        # 여러 셀렉터 시도
        for link_selector in category_link_selectors:
            try:
                links = await category_area.query_selector_all(link_selector)

                if links:
                    for link in links:
                        # 카테고리 이름
                        name = await link.text_content()
                        name = name.strip() if name else ""

                        # URL
                        url = await link.get_attribute("href")

                        # 글 개수 추출 (예: "(15)")
                        count_text = name
                        count = None
                        if "(" in count_text and ")" in count_text:
                            import re
                            count_match = re.search(r'\((\d+)\)', count_text)
                            if count_match:
                                count = int(count_match.group(1))
                                # 이름에서 개수 제거
                                name = re.sub(r'\s*\(\d+\)\s*', '', name).strip()

                        # 계층 레벨 판단 (들여쓰기, 클래스명 등으로)
                        class_name = await link.get_attribute("class") or ""
                        level = 2 if "sub" in class_name.lower() else 1

                        # 카테고리 정보 추가
                        if name and name != "전체보기":  # "전체보기" 제외
                            category_info = CategoryInfo(
                                name=name,
                                url=url,
                                count=count,
                                level=level
                            )
                            categories.append(category_info.to_dict())

                    logger.info(f"카테고리 {len(categories)}개 발견")
                    break  # 성공하면 중단

            except Exception as e:
                logger.debug(f"셀렉터 {link_selector} 실패: {e}")
                continue

        # 4. 결과 반환
        if categories:
            return {
                "success": True,
                "message": f"{len(categories)}개의 카테고리를 찾았습니다",
                "categories": categories
            }
        else:
            return {
                "success": True,
                "message": "카테고리가 없습니다",
                "categories": []
            }

    except Exception as e:
        logger.error(f"카테고리 조회 실패: {e}", exc_info=True)
        return {
            "success": False,
            "message": f"카테고리 조회 중 오류 발생: {str(e)}",
            "categories": []
        }
```

#### 2. `mcp/tools.py` 업데이트

```python
from ..automation.category_actions import get_categories


async def handle_list_categories(page: Page) -> Dict[str, Any]:
    """네이버 블로그의 카테고리 목록을 가져옵니다.

    Args:
        page: Playwright Page 객체 (로그인된 상태)

    Returns:
        작업 결과 딕셔너리
        {
            "success": bool,
            "message": str,
            "categories": [
                {
                    "name": "카테고리명",
                    "url": "카테고리 URL",
                    "count": 글 개수,
                    "level": 계층 레벨 (1 또는 2),
                    "parent": "부모 카테고리명" (2차인 경우)
                },
                ...
            ]
        }
    """
    logger.info("카테고리 목록 조회 시작")

    try:
        result = await get_categories(page)

        if result["success"]:
            logger.info(f"카테고리 조회 완료: {len(result['categories'])}개")
        else:
            logger.error(f"카테고리 조회 실패: {result['message']}")

        return result

    except Exception as e:
        logger.error(f"카테고리 조회 중 예외 발생: {e}", exc_info=True)
        return {
            "success": False,
            "message": f"카테고리 조회 실패: {str(e)}",
            "categories": []
        }
```

#### 3. 테스트 코드

```python
# tests/test_category_list.py

"""카테고리 목록 조회 기능 테스트."""

import asyncio
import sys
from pathlib import Path

# 프로젝트 루트 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from playwright.async_api import async_playwright
from naver_blog_mcp.config import config
from naver_blog_mcp.services.session_manager import SessionManager
from naver_blog_mcp.automation.category_actions import get_categories


async def test_list_categories():
    """카테고리 조회 테스트."""

    print("=" * 80)
    print("네이버 블로그 카테고리 조회 테스트")
    print("=" * 80)

    # 환경 변수 확인
    config.validate()

    async with async_playwright() as p:
        # 브라우저 실행
        browser = await p.chromium.launch(headless=False)

        # 세션 관리자
        session_manager = SessionManager(
            user_id=config.NAVER_BLOG_ID,
            password=config.NAVER_BLOG_PASSWORD
        )
        context = await session_manager.get_or_create_session(browser)
        page = await context.new_page()

        try:
            # 카테고리 조회
            print("\n[테스트] 카테고리 조회 중...")
            result = await get_categories(page)

            # 결과 출력
            print(f"\n✓ 성공: {result['success']}")
            print(f"✓ 메시지: {result['message']}")
            print(f"\n총 {len(result['categories'])}개의 카테고리:")
            print("-" * 80)

            for idx, cat in enumerate(result['categories'], 1):
                indent = "  " * (cat['level'] - 1)
                count_str = f"({cat['count']})" if cat['count'] else ""
                print(f"{idx}. {indent}{cat['name']} {count_str}")
                if cat.get('url'):
                    print(f"   {indent}URL: {cat['url']}")

            print("-" * 80)
            print("\n✅ 테스트 완료!")

        finally:
            await context.close()
            await browser.close()


if __name__ == "__main__":
    asyncio.run(test_list_categories())
```

### 사용 예시 (MCP 클라이언트)

```
사용자: "내 블로그 카테고리 목록을 보여줘"

Claude: [naver_blog_list_categories 도구 호출]

결과:
{
  "success": true,
  "message": "5개의 카테고리를 찾았습니다",
  "categories": [
    {
      "name": "개발",
      "url": "https://blog.naver.com/myid/category/123",
      "count": 15,
      "level": 1,
      "parent": null
    },
    {
      "name": "Python",
      "url": "https://blog.naver.com/myid/category/124",
      "count": 5,
      "level": 2,
      "parent": "개발"
    },
    {
      "name": "일상",
      "url": "https://blog.naver.com/myid/category/125",
      "count": 23,
      "level": 1,
      "parent": null
    }
  ]
}

Claude 응답:
"블로그에 총 5개의 카테고리가 있습니다:

1. 개발 (15개 글)
   - Python (5개 글)
   - JavaScript (10개 글)
2. 일상 (23개 글)
3. 여행 (8개 글)"
```

---

## 예상 구현 난이도

### 난이도: ⭐ (매우 쉬움)

| 구현 단계 | 난이도 | 예상 소요 시간 | 비고 |
|-----------|--------|---------------|------|
| UI 구조 조사 | ⭐ | 1-2시간 | 브라우저 개발자 도구 |
| 기본 함수 구현 | ⭐ | 2-3시간 | DOM 조회만 하면 됨 |
| 에러 처리 | ⭐ | 1시간 | 간단한 예외 처리 |
| 테스트 작성 | ⭐ | 1-2시간 | 단순 조회 테스트 |
| 문서화 | ⭐ | 1시간 | API 문서 작성 |
| **총 예상 시간** | | **6-9시간** | **1일 이내** |

### 다른 기능 대비 난이도

| 기능 | 복잡도 | 이유 |
|------|--------|------|
| **글 작성** | ⭐⭐⭐⭐ | iframe, 여러 필드 입력, 이미지 업로드 |
| **글 삭제** | ⭐⭐⭐ | 버튼 클릭, 확인 팝업 처리 |
| **카테고리 조회** | ⭐ | DOM 조회만 하면 됨 (가장 쉬움) |
| **글 목록 조회** | ⭐⭐ | 페이지네이션 처리 필요 |
| **글 수정** | ⭐⭐⭐⭐ | 글 작성과 유사한 복잡도 |

**결론**: **가장 쉬운 기능**

---

## 구현 시 고려사항

### 장점

#### 1. **매우 간단한 구현**
- ✅ 페이지 접속 → DOM 조회 → 텍스트 추출
- ✅ 복잡한 인터랙션 없음
- ✅ 기존 코드 대부분 재사용 가능

#### 2. **높은 안정성**
- ✅ 공개 페이지 (로그인 불필요할 수도 있음)
- ✅ 정적 HTML 구조
- ✅ 카테고리는 핵심 네비게이션이라 변경 적음

#### 3. **즉시 활용 가능**
- ✅ 글 작성 시 카테고리 선택에 활용
- ✅ MCP Tool로 이미 정의되어 있음
- ✅ 사용자가 기대하는 기능

#### 4. **확장 가능**
- ✅ 카테고리별 글 개수 조회
- ✅ 카테고리 계층 구조 파악
- ✅ 향후 "카테고리별 글 목록 조회"의 기반

### 주의사항

#### 1. **UI 변경 가능성**
- ⚠️ DOM 셀렉터가 변경될 수 있음
- ✅ **해결**: 여러 대체 셀렉터 준비

```python
category_selectors = [
    ".blog_sidebar .category_area",  # 메인 셀렉터
    "#category",                      # 대체 셀렉터 1
    ".category_list",                 # 대체 셀렉터 2
    "[class*='category']",            # 폴백 셀렉터
]
```

#### 2. **카테고리가 없는 경우**
- ⚠️ 새 블로그는 카테고리가 없을 수 있음
- ✅ **해결**: 빈 배열 반환 (에러 아님)

```python
if not categories:
    return {
        "success": True,
        "message": "카테고리가 없습니다",
        "categories": []
    }
```

#### 3. **특수 카테고리**
- ⚠️ "전체보기"는 실제 카테고리가 아님
- ✅ **해결**: 필터링으로 제외

```python
if name and name != "전체보기":
    categories.append(category_info)
```

#### 4. **2차 카테고리 인식**
- ⚠️ 2차 카테고리(서브카테고리) 구분 필요
- ✅ **해결**: CSS 클래스 또는 들여쓰기로 판단

```python
class_name = await link.get_attribute("class") or ""
level = 2 if "sub" in class_name.lower() else 1
```

### 에러 케이스

| 에러 상황 | 원인 | 처리 방법 |
|-----------|------|----------|
| 카테고리 영역 없음 | 블로그 UI 변경 | 대체 셀렉터 시도 |
| 카테고리가 없음 | 신규 블로그 | 빈 배열 반환 (정상) |
| 페이지 로딩 실패 | 네트워크 오류 | 재시도 로직 |
| DOM 구조 변경 | 네이버 업데이트 | 여러 셀렉터 시도 |

---

## 결론 및 권장사항

### 최종 결론

✅ **네이버 블로그 카테고리 조회 기능은 구현 가능하며, 가장 쉬운 기능입니다.**

**근거**:
1. 공개 페이지에서 조회 가능 (안정적)
2. DOM 조회만 하면 됨 (복잡한 인터랙션 없음)
3. 예상 구현 시간: **0.5-1일** (6-9시간)
4. 이미 MCP Tool로 정의되어 있음 (즉시 구현 필요)

### 우선순위: ⭐⭐⭐⭐⭐ (최우선)

**즉시 구현을 권장하는 이유**:

1. **필수 기능**
   - 글 작성 시 카테고리 선택에 필요
   - "어떤 카테고리가 있는지" 알아야 사용 가능

2. **가장 쉬운 구현**
   - 1일 이내 완성 가능
   - 리스크가 거의 없음

3. **이미 정의됨**
   - MCP Tool에 이미 선언되어 있음
   - 사용자가 이미 기대하는 기능

4. **다른 기능의 기반**
   - 카테고리별 글 목록 조회의 기반
   - 블로그 관리 기능의 시작점

### 구현 로드맵

```
✅ 현재: 글 작성 + 이미지 업로드 (완료)
    ↓
⚡ Day 1: 카테고리 조회 구현 ← 지금 여기
    ↓
⚡ Day 2-4: 글 목록 조회 구현
    ↓
🔥 Day 5-8: 글 수정 구현
    ↓
⚪ Day 9-10: 글 삭제 구현 (선택)
```

### 즉시 실행 권장

**다음 단계**:

1. ✅ **UI 구조 조사**
   ```bash
   # 브라우저에서 직접 확인
   # F12 개발자 도구로 카테고리 DOM 분석
   ```

2. ✅ **기본 구현**
   ```bash
   git checkout -b feature/list-categories
   # automation/category_actions.py 생성
   # mcp/tools.py 업데이트
   ```

3. ✅ **테스트**
   ```bash
   uv run python tests/test_category_list.py
   ```

4. ✅ **MCP 서버 재시작 및 Claude Desktop 테스트**
   ```
   Claude: "내 블로그 카테고리 목록 보여줘"
   ```

### 예상 효과

구현 완료 시:
- ✅ 글 작성 시 카테고리 선택 가능
- ✅ 사용자 경험 향상
- ✅ MCP 서버 완성도 향상
- ✅ 다음 기능 (글 목록 조회)의 기반 마련

---

## 부록

### A. 예상 셀렉터 목록

```python
# 카테고리 영역
CATEGORY_AREA_SELECTORS = [
    ".blog_sidebar .category_area",
    "#category",
    ".category_list",
    "[class*='category']",
]

# 카테고리 링크
CATEGORY_LINK_SELECTORS = [
    "a[href*='/category/']",
    ".category_item a",
    ".category_link",
    "a.link_item",
]

# 글 개수
COUNT_SELECTORS = [
    ".count",
    ".num",
    "span.post_count",
]
```

### B. 반환 데이터 형식

```typescript
interface CategoryListResult {
    success: boolean;
    message: string;
    categories: Category[];
}

interface Category {
    name: string;           // 카테고리명
    url?: string;           // 카테고리 URL
    count?: number;         // 글 개수
    level: 1 | 2;          // 계층 레벨
    parent?: string;        // 2차 카테고리의 부모
}
```

### C. 참고 자료

1. **프로젝트 내부**
   - `src/naver_blog_mcp/automation/post_actions.py` - 페이지 접근 참고
   - `src/naver_blog_mcp/services/session_manager.py` - 세션 관리
   - `src/naver_blog_mcp/utils/selector_helper.py` - 대체 셀렉터

2. **네이버 블로그 구조**
   - 카테고리는 블로그 사이드바에 표시
   - 최대 2단계 계층 지원
   - 글 개수와 함께 표시

### D. FAQ

**Q1: 로그인이 필요한가요?**
A: 기본적으로 불필요합니다. 공개 블로그의 카테고리는 누구나 볼 수 있습니다. 다만, 현재 프로젝트는 로그인된 상태를 유지하므로 그대로 사용하면 됩니다.

**Q2: 비공개 카테고리도 조회되나요?**
A: 로그인된 상태라면 본인의 비공개 카테고리도 조회 가능합니다.

**Q3: 카테고리 개수 제한이 있나요?**
A: 네이버 블로그의 카테고리 개수 제한은 명확하지 않지만, 실용적으로는 20-30개 이내를 권장합니다.

**Q4: 구분선(separator)도 조회되나요?**
A: 구분선은 실제 카테고리가 아니므로 제외됩니다. 필요시 별도 처리 가능합니다.

---

**문서 버전**: 1.0
**작성자**: Claude Code
**최종 업데이트**: 2025-11-04
**결론**: 카테고리 조회는 최우선 구현 권장 (0.5-1일 소요)
