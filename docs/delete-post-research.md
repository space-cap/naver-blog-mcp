# 네이버 블로그 글 삭제 기능 구현 가능성 조사

**조사 일자**: 2025-11-04
**조사 목적**: 네이버 블로그 MCP 서버에 글 삭제 기능 구현 가능 여부 확인
**결론**: ✅ **구현 가능**

---

## 목차

1. [조사 배경](#조사-배경)
2. [조사 방법](#조사-방법)
3. [네이버 블로그 글 삭제 프로세스](#네이버-블로그-글-삭제-프로세스)
4. [기술적 구현 가능성](#기술적-구현-가능성)
5. [구현 방안](#구현-방안)
6. [예상 구현 난이도](#예상-구현-난이도)
7. [구현 시 고려사항](#구현-시-고려사항)
8. [결론 및 권장사항](#결론-및-권장사항)

---

## 조사 배경

### 현재 상태
- **구현 완료**: `naver_blog_create_post` (글 작성, 이미지 업로드)
- **미구현**: `naver_blog_delete_post` (글 삭제)
- **미구현**: `naver_blog_list_categories` (카테고리 조회)

### 구현 필요성
MCP 서버의 완성도를 높이고 사용자가 Claude를 통해 블로그를 완전히 관리할 수 있도록 글 삭제 기능이 필요합니다.

---

## 조사 방법

### 1. 웹 검색 조사
네이버 블로그 글 삭제 방법에 대한 공개 정보를 수집했습니다.

**검색 키워드**:
- "네이버 블로그 글 삭제 방법 2024 2025"
- "네이버 블로그 개별 게시글 삭제 버튼 위치"

**검색 결과 요약**:
- 개별 게시글 삭제에 대한 구체적인 최신 문서는 부족
- 블로그 전체 초기화(탈퇴) 방법에 대한 정보는 다수 존재
- 일반적으로 각 게시글의 관리 메뉴에서 삭제 가능

### 2. 기술적 분석
Playwright 기반 자동화의 관점에서 구현 가능성을 분석했습니다.

---

## 네이버 블로그 글 삭제 프로세스

### 일반적인 사용자 프로세스

```
1. 네이버 블로그 로그인
   ↓
2. 삭제할 글 페이지로 이동
   ↓
3. "수정" 또는 "더보기" 버튼 클릭
   ↓
4. "삭제" 옵션 선택
   ↓
5. 삭제 확인 팝업에서 "확인" 클릭
   ↓
6. 글 삭제 완료
```

### URL 구조
```
https://blog.naver.com/{블로그ID}/{글번호}
```

예시:
```
https://blog.naver.com/myid/223123456789
```

---

## 기술적 구현 가능성

### ✅ 구현 가능한 이유

#### 1. **Playwright 자동화 적합성**
웹 UI를 통해 수동으로 삭제할 수 있다면, Playwright로 자동화 가능합니다.

| 요구 기능 | 현재 프로젝트 지원 | 비고 |
|-----------|-------------------|------|
| 페이지 이동 | ✅ | `page.goto()` 사용 중 |
| 버튼 클릭 | ✅ | 글 작성에서 사용 중 |
| 팝업 처리 | ✅ | 확인 대화상자 처리 가능 |
| iframe 접근 | ✅ | 글 작성에서 구현됨 |
| 동적 셀렉터 | ✅ | `selector_helper.py` 존재 |

#### 2. **기존 구현 재사용**
현재 프로젝트에서 이미 구현된 기능들을 재사용할 수 있습니다:

```python
# 이미 구현된 기능들
- 네이버 로그인 (login.py)
- 세션 관리 (session_manager.py)
- 에러 처리 (error_handler.py)
- 재시도 로직 (retry.py)
- Trace 기록 (trace_manager.py)
```

#### 3. **API 대신 웹 자동화 사용**
- 네이버 블로그 공식 API는 2020년에 종료됨
- 현재 프로젝트는 Playwright 기반으로 구축되어 있어 동일한 방식 적용 가능

---

## 구현 방안

### 아키텍처 설계

```
src/naver_blog_mcp/
├── automation/
│   └── post_actions.py          # delete_blog_post() 함수 추가
├── mcp/
│   └── tools.py                 # handle_delete_post() 구현
└── tests/
    └── test_delete_post.py      # 삭제 기능 테스트
```

### 코드 구조 (Pseudo-code)

```python
# automation/post_actions.py

@retry_on_error
async def delete_blog_post(
    page: Page,
    post_url: str,
    confirm: bool = True
) -> Dict[str, Any]:
    """네이버 블로그 글을 삭제합니다.

    Args:
        page: Playwright Page 객체 (로그인된 상태)
        post_url: 삭제할 글의 URL
        confirm: 삭제 확인 (기본: True, False면 실제 삭제 안 함)

    Returns:
        {
            "success": bool,
            "message": str,
            "post_url": str
        }
    """
    try:
        # 1. 글 페이지로 이동
        await page.goto(post_url, wait_until="networkidle")
        logger.info(f"글 페이지 접근: {post_url}")

        # 2. iframe 접근 (필요 시)
        # 네이버 블로그 구조에 따라 iframe 내부 접근 필요
        iframe_element = await page.query_selector("iframe#mainFrame")
        if iframe_element:
            main_frame = await iframe_element.content_frame()
            context = main_frame
        else:
            context = page

        # 3. 삭제 버튼/메뉴 찾기 (여러 셀렉터 시도)
        delete_button_selectors = [
            "button:has-text('삭제')",
            "a:has-text('삭제')",
            ".btn_delete",
            "[data-action='delete']",
        ]

        # 더보기 메뉴가 필요한 경우
        more_button = await context.query_selector("button:has-text('더보기')")
        if more_button:
            await more_button.click()
            await asyncio.sleep(0.5)

        # 삭제 버튼 찾기
        delete_button = await find_element_with_fallback(
            context,
            delete_button_selectors
        )

        if not delete_button:
            raise ElementNotFoundError("삭제 버튼을 찾을 수 없습니다")

        # 4. 삭제 확인 여부 체크
        if not confirm:
            logger.info("삭제 확인이 False이므로 실제 삭제하지 않습니다")
            return {
                "success": True,
                "message": "삭제 가능 확인 완료 (실제 삭제 안 함)",
                "post_url": post_url
            }

        # 5. 삭제 클릭
        await delete_button.click()
        logger.info("삭제 버튼 클릭")

        # 6. 확인 팝업 처리
        # Playwright의 dialog 이벤트 리스너 등록
        page.on("dialog", lambda dialog: dialog.accept())

        # 또는 확인 버튼 클릭
        confirm_button = await page.wait_for_selector(
            "button:has-text('확인')",
            timeout=5000
        )
        if confirm_button:
            await confirm_button.click()

        # 7. 삭제 완료 확인
        # 페이지가 리다이렉트되었는지 확인
        await page.wait_for_url(
            lambda url: post_url not in url,
            timeout=10000
        )

        logger.info(f"글 삭제 완료: {post_url}")

        return {
            "success": True,
            "message": "글이 성공적으로 삭제되었습니다",
            "post_url": post_url
        }

    except Exception as e:
        logger.error(f"글 삭제 실패: {e}")
        return {
            "success": False,
            "message": f"글 삭제 중 오류 발생: {str(e)}",
            "post_url": post_url
        }
```

### MCP Tool 구현

```python
# mcp/tools.py

async def handle_delete_post(page: Page, post_url: str) -> Dict[str, Any]:
    """네이버 블로그 글을 삭제합니다.

    Args:
        page: Playwright Page 객체 (로그인된 상태)
        post_url: 삭제할 글의 URL

    Returns:
        작업 결과 딕셔너리
    """
    logger.info(f"글 삭제 요청: {post_url}")

    # URL 형식 검증
    if not is_valid_naver_blog_url(post_url):
        return {
            "success": False,
            "message": "올바른 네이버 블로그 URL이 아닙니다",
            "post_url": post_url
        }

    # 삭제 실행
    result = await delete_blog_post(page, post_url, confirm=True)

    return result
```

### 테스트 코드

```python
# tests/test_delete_post.py

import pytest
from playwright.async_api import async_playwright

@pytest.mark.asyncio
async def test_delete_post():
    """글 삭제 기능 테스트."""

    # 1. 테스트용 글 작성
    test_post = await create_blog_post(
        page=page,
        title="삭제 테스트 글",
        content="이 글은 자동으로 삭제됩니다"
    )

    post_url = test_post["post_url"]

    # 2. 글 삭제
    result = await delete_blog_post(
        page=page,
        post_url=post_url
    )

    # 3. 검증
    assert result["success"] == True
    assert "삭제" in result["message"]

    # 4. 실제로 삭제되었는지 확인
    await page.goto(post_url)
    # 404 또는 "존재하지 않는 글" 메시지 확인
```

---

## 예상 구현 난이도

### 난이도: ⭐⭐⭐ (중간)

| 구현 단계 | 난이도 | 예상 소요 시간 | 비고 |
|-----------|--------|---------------|------|
| UI 구조 조사 | ⭐ | 2-3시간 | 브라우저 개발자 도구로 확인 |
| 삭제 함수 구현 | ⭐⭐ | 4-6시간 | 기존 코드 참고 가능 |
| 에러 처리 | ⭐⭐ | 2-3시간 | 재시도 로직, 예외 처리 |
| 테스트 작성 | ⭐⭐ | 3-4시간 | 안전한 테스트 환경 구축 |
| 문서화 | ⭐ | 1-2시간 | 사용자 가이드 업데이트 |
| **총 예상 시간** | | **12-18시간** | **1-2일** |

### 글 작성 대비 난이도

| 기능 | 복잡도 | 이유 |
|------|--------|------|
| **글 작성** | ⭐⭐⭐⭐ | iframe, 이미지 업로드, 여러 필드 입력 |
| **글 삭제** | ⭐⭐⭐ | 버튼 클릭, 확인 팝업만 처리 |

**결론**: 글 작성보다 **간단**합니다.

---

## 구현 시 고려사항

### 장점

#### 1. **기술적 장점**
- ✅ 기존 코드 인프라 재사용 가능
- ✅ Playwright 자동화에 적합한 작업
- ✅ 에러 처리 및 재시도 로직 이미 구축됨

#### 2. **사용자 경험**
- ✅ MCP 서버 완성도 향상
- ✅ Claude를 통한 완전한 블로그 관리 가능
- ✅ "이 글 삭제해줘"와 같은 자연어 명령 지원

### 주의사항

#### 1. **복구 불가능**
- ⚠️ 삭제된 글은 복구할 수 없음
- ⚠️ 사용자 확인 프로세스 필수
- ⚠️ 안전장치 고려 (예: 삭제 전 백업)

```python
# 안전장치 예시
async def handle_delete_post_with_safety(
    page: Page,
    post_url: str,
    require_confirmation: bool = True
) -> Dict[str, Any]:
    """안전장치가 포함된 글 삭제."""

    if require_confirmation:
        # MCP 클라이언트에서 사용자 확인 요청
        return {
            "success": False,
            "message": "정말로 이 글을 삭제하시겠습니까? 복구할 수 없습니다.",
            "require_confirmation": True,
            "post_url": post_url
        }

    # 실제 삭제 진행
    return await delete_blog_post(page, post_url)
```

#### 2. **UI 변경 가능성**
- ⚠️ 네이버가 블로그 UI를 변경할 수 있음
- ⚠️ 셀렉터가 작동하지 않을 경우 대체 셀렉터 필요
- ⚠️ `selector_helper.py`의 대체 셀렉터 기능 활용

#### 3. **에러 케이스**
예상 에러 상황과 처리 방법:

| 에러 상황 | 원인 | 처리 방법 |
|-----------|------|----------|
| 글을 찾을 수 없음 | 이미 삭제되었거나 존재하지 않는 URL | `ElementNotFoundError` 발생 |
| 권한 없음 | 다른 사용자의 글 | `PermissionError` 발생 |
| 네트워크 오류 | 연결 끊김 | `NetworkError` 발생 → 재시도 |
| 삭제 버튼 없음 | UI 변경 | 대체 셀렉터 시도 |

#### 4. **테스트 전략**
안전한 테스트를 위한 전략:

```python
# 테스트 전략
1. 테스트용 임시 글 작성
2. 해당 글 삭제 테스트
3. 삭제 확인
4. 실제 운영 글은 테스트하지 않음

# 테스트 환경 분리
- 개발 환경: 실제 삭제 수행
- 프로덕션: confirm=False로 시뮬레이션만
```

---

## 구현 단계별 계획

### Phase 1: UI 조사 (Day 1)
- [ ] 네이버 블로그에서 수동으로 글 삭제 프로세스 확인
- [ ] 브라우저 개발자 도구로 DOM 구조 분석
- [ ] 삭제 버튼/메뉴의 셀렉터 수집
- [ ] 확인 팝업 구조 확인

**산출물**:
- `docs/delete-ui-structure.md` - UI 구조 문서
- DOM 셀렉터 목록

### Phase 2: 기본 구현 (Day 1-2)
- [ ] `automation/post_actions.py`에 `delete_blog_post()` 함수 구현
- [ ] `mcp/tools.py`에서 `handle_delete_post()` 구현
- [ ] 기본 에러 처리 추가

**산출물**:
- 작동하는 삭제 함수

### Phase 3: 에러 처리 및 재시도 (Day 2)
- [ ] 커스텀 예외 추가 (`DeleteError`)
- [ ] `@retry_on_error` 데코레이터 적용
- [ ] 대체 셀렉터 구현
- [ ] Trace 기록 추가

**산출물**:
- 안정적인 삭제 기능

### Phase 4: 테스트 (Day 2)
- [ ] `tests/test_delete_post.py` 작성
- [ ] 통합 테스트 작성
- [ ] 엣지 케이스 테스트

**산출물**:
- 테스트 커버리지 80% 이상

### Phase 5: 문서화 (Day 2)
- [ ] `docs/user-guide.md` 업데이트
- [ ] API 문서 작성
- [ ] 사용 예제 추가

**산출물**:
- 완전한 문서

---

## 참고: 유사 프로젝트 사례

### 다른 블로그 플랫폼의 삭제 API

| 플랫폼 | API 제공 | 자동화 난이도 |
|--------|----------|--------------|
| Tistory | ✅ (OAuth API) | ⭐ (쉬움) |
| Medium | ✅ (REST API) | ⭐ (쉬움) |
| WordPress | ✅ (REST API) | ⭐ (쉬움) |
| **네이버 블로그** | ❌ (종료됨) | ⭐⭐⭐ (중간) |

네이버 블로그는 공식 API가 없지만, Playwright를 사용하면 다른 플랫폼과 유사한 수준의 자동화가 가능합니다.

---

## 결론 및 권장사항

### 최종 결론

✅ **네이버 블로그 글 삭제 기능은 구현 가능합니다.**

**근거**:
1. 웹 UI를 통해 수동으로 삭제할 수 있음
2. Playwright로 자동화 가능한 작업
3. 기존 코드 인프라 재사용 가능
4. 예상 구현 시간: 1-2일

### 권장사항

#### 우선순위: ⭐⭐⭐⭐ (높음)

**구현을 권장하는 이유**:
1. **MCP 서버 완성도**: CRUD 중 Delete 기능 필수
2. **사용자 요구**: 블로그 관리를 위해 삭제 기능 필요
3. **구현 비용**: 상대적으로 낮은 난이도 (1-2일)
4. **유지보수**: 기존 구조와 일관성 유지

#### 구현 순서

1. ✅ **글 작성** (완료)
2. ✅ **이미지 업로드** (완료)
3. 🔲 **글 삭제** ← **다음 구현 권장**
4. 🔲 **카테고리 조회**
5. 🔲 **글 수정**
6. 🔲 **글 목록 조회**

#### 대안

만약 구현하지 않는다면:
- 사용자가 수동으로 삭제해야 함
- MCP 서버의 완성도 저하
- 자동화된 블로그 관리 불가능

### 다음 단계

구현을 진행하기로 결정했다면:

1. **Phase 1 시작**: UI 조사 스크립트 실행
   ```bash
   uv run python tests/test_delete_post_research.py
   ```

2. **이슈 생성**: GitHub에 구현 이슈 등록
   ```
   Title: [Feature] 글 삭제 기능 구현
   Labels: enhancement, automation
   ```

3. **브랜치 생성**:
   ```bash
   git checkout -b feature/delete-post
   ```

4. **구현 시작**: Phase 1부터 순차적으로 진행

---

## 부록

### A. 참고 자료

1. **Playwright 공식 문서**
   - Dialog 처리: https://playwright.dev/docs/dialogs
   - 요소 선택: https://playwright.dev/docs/selectors

2. **프로젝트 내부 참고 코드**
   - `src/naver_blog_mcp/automation/post_actions.py` - 글 작성 구현
   - `src/naver_blog_mcp/utils/selector_helper.py` - 대체 셀렉터
   - `src/naver_blog_mcp/utils/retry.py` - 재시도 로직

3. **관련 문서**
   - `docs/architecture.md` - 프로젝트 아키텍처
   - `docs/implementation-plan.md` - 원래 구현 계획

### B. FAQ

**Q1: 삭제한 글을 복구할 수 있나요?**
A: 아니요. 네이버 블로그 API/UI 모두 삭제한 글은 복구할 수 없습니다.

**Q2: 다른 사람의 글도 삭제할 수 있나요?**
A: 아니요. 로그인한 사용자 본인의 글만 삭제 가능합니다.

**Q3: 삭제 전에 백업이 가능한가요?**
A: 예. 삭제 전에 글 내용을 가져오는 기능을 추가로 구현할 수 있습니다.

**Q4: UI가 변경되면 어떻게 되나요?**
A: 대체 셀렉터 기능으로 여러 셀렉터를 시도하여 변경에 대응합니다.

---

**문서 버전**: 1.0
**작성자**: Claude Code
**최종 업데이트**: 2025-11-04
**관련 이슈**: N/A
