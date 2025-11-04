"""네이버 블로그 세션 관리자."""

import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from playwright.async_api import Browser, BrowserContext

from ..automation.login import login_to_naver, verify_login_session, NaverLoginError


class SessionManager:
    """네이버 블로그 세션을 관리하는 클래스."""

    def __init__(
        self,
        user_id: str,
        password: str,
        storage_path: str = "playwright-state/auth.json",
        session_validity_hours: int = 24,
    ):
        """
        세션 매니저 초기화.

        Args:
            user_id: 네이버 아이디
            password: 네이버 비밀번호
            storage_path: 세션 저장 경로
            session_validity_hours: 세션 유효 시간 (시간)
        """
        self.user_id = user_id
        self.password = password
        self.storage_path = storage_path
        self.session_validity_hours = session_validity_hours
        self.last_login_time: Optional[datetime] = None

    def is_session_file_valid(self) -> bool:
        """
        세션 파일이 유효한지 확인합니다.

        Returns:
            세션 파일 유효 여부
        """
        # 1. 파일 존재 여부
        if not Path(self.storage_path).exists():
            return False

        # 2. 파일 수정 시간 확인
        file_mtime = datetime.fromtimestamp(Path(self.storage_path).stat().st_mtime)
        elapsed = datetime.now() - file_mtime

        # 설정된 유효 시간 이내인지 확인
        if elapsed > timedelta(hours=self.session_validity_hours):
            return False

        return True

    async def is_session_valid(self, context: BrowserContext) -> bool:
        """
        실제 네이버 페이지에 접속하여 세션 유효성을 검사합니다.

        Args:
            context: Playwright BrowserContext 객체

        Returns:
            세션 유효 여부
        """
        # 1. 파일 유효성 확인
        if not self.is_session_file_valid():
            return False

        # 2. 실제 페이지 접속 테스트
        page = await context.new_page()
        try:
            is_valid = await verify_login_session(page)
            return is_valid
        finally:
            await page.close()

    async def get_or_create_session(
        self, browser: Browser, headless: bool = True
    ) -> BrowserContext:
        """
        유효한 세션이 있으면 재사용하고, 없으면 새로 로그인합니다.

        Args:
            browser: Playwright Browser 객체
            headless: 헤드리스 모드 여부

        Returns:
            BrowserContext 객체

        Raises:
            NaverLoginError: 로그인 실패 시
        """
        # 1. 기존 세션 파일이 있고 유효하면 재사용
        if self.is_session_file_valid():
            try:
                context = await browser.new_context(storage_state=self.storage_path)

                # 실제 로그인 상태 확인
                if await self.is_session_valid(context):
                    print(f"저장된 세션 재사용: {self.storage_path}")
                    return context
                else:
                    print("저장된 세션이 만료되었습니다. 재로그인합니다.")
                    await context.close()
            except Exception as e:
                print(f"세션 복원 실패: {e}. 재로그인합니다.")

        # 2. 새로 로그인
        context = await browser.new_context()
        page = await context.new_page()

        try:
            result = await login_to_naver(
                page=page,
                user_id=self.user_id,
                password=self.password,
                storage_state_path=self.storage_path,
                headless=headless,
            )

            self.last_login_time = datetime.now()
            print(f"{result['message']}")
            print(f"   세션 저장: {result['storage_state_path']}")

            return context

        except NaverLoginError as e:
            await context.close()
            raise e
        finally:
            await page.close()

    async def refresh_session_if_needed(
        self, browser: Browser, context: BrowserContext, headless: bool = True
    ) -> BrowserContext:
        """
        필요 시 세션을 갱신합니다.

        Args:
            browser: Playwright Browser 객체
            context: 현재 BrowserContext 객체
            headless: 헤드리스 모드 여부

        Returns:
            갱신된 또는 기존 BrowserContext 객체
        """
        # 세션이 유효하면 그대로 반환
        if await self.is_session_valid(context):
            return context

        # 세션이 만료되었으면 재로그인
        print("세션이 만료되었습니다. 재로그인합니다.")
        await context.close()
        return await self.get_or_create_session(browser, headless)

    def clear_session(self) -> None:
        """저장된 세션 파일을 삭제합니다."""
        if Path(self.storage_path).exists():
            Path(self.storage_path).unlink()
            print(f"세션 파일 삭제: {self.storage_path}")
