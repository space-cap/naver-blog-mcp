# 네이버 블로그 이미지 업로드 구조 조사

## 조사 일시
2025-01-04

## 조사 목적
Day 11-12 이미지 업로드 기능 구현 전, 네이버 블로그의 이미지 업로드가 기술적으로 가능한지 확인

## 조사 결과

### ✅ 이미지 업로드 가능 확인

네이버 블로그에서 Playwright를 통한 이미지 업로드가 **기술적으로 가능**함을 확인했습니다.

## 상세 구조

### 1. iframe 구조

네이버 블로그 글쓰기 에디터는 iframe 내부에 위치합니다:

```html
<iframe id="mainFrame" name="mainFrame"
  src="/PostWriteForm.naver?blogId=070802&...">
  <!-- 에디터가 여기 안에 있음 -->
</iframe>
```

**중요**: 모든 DOM 조작은 iframe 내부에서 수행해야 합니다.

### 2. 이미지 업로드 버튼

툴바에 위치한 "사진" 버튼:

```python
# 권장 셀렉터
button_selector = "button[data-name='image']"

# 대체 셀렉터
alternative_selectors = [
    "button[data-name='image']",
    "button:has-text('사진')",
    ".se-image-toolbar-button",
]
```

**속성**:
- Tag: `BUTTON`
- Classes: `se-image-toolbar-button se-document-toolbar-basic-button se-text-icon-toolbar-button __se-sentry`
- Data-Name: `image`

### 3. 파일 업로드 Input

버튼 클릭 후 생성되는 hidden file input:

```python
file_input_selector = "input[type='file']#hidden-file"
```

**속성**:
- Type: `file`
- ID: `hidden-file`
- Accept: `.jpg,.jpeg,.gif,.png,.bmp,.heic,.heif,.webp`
- 초기에는 DOM에 없고, 버튼 클릭 시 동적으로 생성됨

### 4. 지원 이미지 포맷

- JPG/JPEG
- GIF
- PNG
- BMP
- HEIC/HEIF (Apple 포맷)
- WebP

## 구현 방법

### Step 1: iframe 접근

```python
# iframe 찾기
iframe_element = await page.wait_for_selector("iframe#mainFrame")
main_frame = await iframe_element.content_frame()
```

### Step 2: 이미지 버튼 클릭

```python
# 사진 버튼 클릭
photo_button = main_frame.locator("button[data-name='image']")
await photo_button.click()
await asyncio.sleep(1)  # 파일 input 생성 대기
```

### Step 3: 파일 업로드

```python
# 파일 input 찾기
file_input = main_frame.locator("input[type='file']#hidden-file")

# 파일 업로드
await file_input.set_input_files("path/to/image.jpg")
```

### Step 4: 업로드 완료 대기

```python
# 업로드된 이미지가 에디터에 삽입될 때까지 대기
# (구체적인 셀렉터는 추가 조사 필요)
await main_frame.wait_for_selector(".se-image-resource", timeout=10000)
```

## 추가 조사 필요 사항

1. **업로드 완료 감지**
   - 이미지 업로드 후 에디터에 삽입되는 요소의 셀렉터
   - 업로드 진행 상태 표시 요소
   - 업로드 완료/실패 감지 방법

2. **이미지 옵션**
   - 이미지 크기 조절 가능 여부
   - 이미지 정렬 (좌/중/우) 설정
   - 대체 텍스트(alt text) 설정

3. **다중 이미지 업로드**
   - 한 번에 여러 이미지 업로드 가능 여부
   - 이미지 순서 제어 방법

4. **에러 처리**
   - 용량 제한 (파일 크기, 전체 용량)
   - 지원하지 않는 포맷 업로드 시 에러 메시지
   - 네트워크 에러 시 재시도 로직

## 구현 우선순위

### Phase 1 (Day 11) - 기본 기능
- [x] iframe 접근 확인
- [x] 이미지 버튼 찾기
- [x] 파일 input 찾기
- [ ] 단일 이미지 업로드 구현
- [ ] 업로드 완료 감지

### Phase 2 (Day 12) - 고급 기능
- [ ] 다중 이미지 업로드
- [ ] 이미지 옵션 설정 (크기, 정렬)
- [ ] 에러 처리 및 재시도
- [ ] Base64 이미지 지원

## 결론

**이미지 업로드는 기술적으로 가능합니다.** ✅

Day 11-12 구현을 진행할 수 있는 충분한 근거를 확보했습니다.

## 참고 자료

- 테스트 스크립트: `tests/test_image_upload_research.py`
- 스크린샷: `playwright-state/screenshots/upload_dialog.png`
- iframe HTML: `playwright-state/html/write_page.html`
