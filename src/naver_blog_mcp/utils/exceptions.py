"""네이버 블로그 MCP 서버 커스텀 예외 클래스."""

from typing import Optional


class NaverBlogError(Exception):
    """네이버 블로그 관련 기본 에러."""

    def __init__(self, message: str, details: Optional[dict] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class LoginError(NaverBlogError):
    """로그인 관련 에러."""

    pass


class CaptchaDetectedError(LoginError):
    """CAPTCHA가 감지된 경우."""

    pass


class InvalidCredentialsError(LoginError):
    """잘못된 로그인 정보."""

    pass


class SessionExpiredError(LoginError):
    """세션이 만료된 경우."""

    pass


class PostError(NaverBlogError):
    """글쓰기 관련 에러."""

    pass


class ElementNotFoundError(PostError):
    """페이지 요소를 찾을 수 없음 (UI 변경 가능성)."""

    pass


class NavigationError(PostError):
    """페이지 이동 실패."""

    pass


class UploadError(PostError):
    """업로드 실패 (글, 이미지 등)."""

    pass


class NetworkError(NaverBlogError):
    """네트워크 관련 에러."""

    pass


class TimeoutError(NaverBlogError):
    """타임아웃 에러."""

    pass


class UIChangedError(NaverBlogError):
    """네이버 UI가 변경되어 셀렉터가 동작하지 않음."""

    def __init__(self, message: str, selector: Optional[str] = None):
        self.selector = selector
        details = {"selector": selector} if selector else {}
        super().__init__(message, details)
