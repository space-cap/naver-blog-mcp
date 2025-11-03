"""프로젝트 설정 관리."""

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

# .env 파일 로드
project_root = Path(__file__).parent.parent.parent
load_dotenv(project_root / ".env")


class Config:
    """프로젝트 설정 클래스."""

    # 네이버 블로그 계정
    NAVER_BLOG_ID: str = os.getenv("NAVER_BLOG_ID", "")
    NAVER_BLOG_PASSWORD: str = os.getenv("NAVER_BLOG_PASSWORD", "")

    # Playwright 설정
    HEADLESS: bool = os.getenv("HEADLESS", "true").lower() == "true"
    SLOW_MO: int = int(os.getenv("SLOW_MO", "0"))

    # 로깅 설정
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO").upper()

    # 세션 설정
    SESSION_STORAGE_PATH: str = os.getenv(
        "SESSION_STORAGE_PATH", "playwright-state/auth.json"
    )
    SESSION_VALIDITY_HOURS: int = int(os.getenv("SESSION_VALIDITY_HOURS", "24"))

    # Playwright 브라우저 설정
    BROWSER_ARGS: list[str] = [
        "--disable-blink-features=AutomationControlled",
        "--disable-dev-shm-usage",
    ]

    USER_AGENT: str = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )

    VIEWPORT: dict[str, int] = {"width": 1920, "height": 1080}

    @classmethod
    def validate(cls) -> None:
        """설정 유효성 검사."""
        if not cls.NAVER_BLOG_ID:
            raise ValueError("NAVER_BLOG_ID가 설정되지 않았습니다.")
        if not cls.NAVER_BLOG_PASSWORD:
            raise ValueError("NAVER_BLOG_PASSWORD가 설정되지 않았습니다.")

    @classmethod
    def get_browser_config(cls) -> dict:
        """Playwright 브라우저 설정을 반환합니다."""
        return {
            "headless": cls.HEADLESS,
            "args": cls.BROWSER_ARGS,
            "slow_mo": cls.SLOW_MO,
        }

    @classmethod
    def get_context_config(cls) -> dict:
        """Playwright 컨텍스트 설정을 반환합니다."""
        return {
            "user_agent": cls.USER_AGENT,
            "viewport": cls.VIEWPORT,
            "locale": "ko-KR",
            "timezone_id": "Asia/Seoul",
        }


# 전역 설정 인스턴스
config = Config()
