"""네이버 블로그 DOM 셀렉터 정의.

네이버 UI 변경에 대응하기 위해 대체 셀렉터를 리스트로 관리합니다.
"""

from typing import List, Union

# 타입 정의
Selector = Union[str, List[str]]


class NaverSelectors:
    """네이버 블로그 셀렉터 클래스."""

    # 로그인 페이지
    LOGIN = {
        "id_input": "#id",
        "pw_input": "#pw",
        "login_btn": [".btn_login", "button[type='submit']"],
        "error_message": ".error_message",
    }

    # 블로그 메인
    BLOG_MAIN = {
        "profile": [".my_nick", ".profile_info"],
        "write_btn": ["a[href*='PostWriteForm']", ".write_btn"],
    }

    # 글쓰기 페이지
    POST_WRITE = {
        "title_input": ["input[placeholder*='제목']", "#title", ".se-title-input"],
        "content_frame": ["iframe.se-iframe", "iframe#mainFrame"],
        "content_body": [".se-component-content", ".se-text-paragraph"],
        "category_select": [".blog2_series", "select[name='category']"],
        "tag_input": ["input[placeholder*='태그']", ".tag_input"],
        "publish_btn": [
            "button:has-text('발행')",
            ".publish_btn",
            "button[type='submit']",
        ],
        "temp_save_btn": ["button:has-text('임시저장')", ".temp_save_btn"],
        "image_upload_btn": [
            "button[aria-label='사진']",
            ".image_upload",
            "button:has-text('사진')",
        ],
    }

    # 글 보기 페이지
    POST_VIEW = {
        "post_url_pattern": "**/PostView.naver*",
        "edit_btn": ["a:has-text('수정')", ".edit_btn"],
        "delete_btn": ["a:has-text('삭제')", ".delete_btn"],
    }

    @classmethod
    def get_selector(cls, category: str, key: str) -> Selector:
        """
        카테고리와 키로 셀렉터 가져오기.

        Args:
            category: 셀렉터 카테고리 (LOGIN, BLOG_MAIN, POST_WRITE, POST_VIEW)
            key: 셀렉터 키

        Returns:
            셀렉터 문자열 또는 대체 셀렉터 리스트

        Raises:
            KeyError: 존재하지 않는 카테고리나 키
        """
        category_dict = getattr(cls, category, None)
        if category_dict is None:
            raise KeyError(f"존재하지 않는 카테고리: {category}")

        selector = category_dict.get(key)
        if selector is None:
            raise KeyError(f"존재하지 않는 셀렉터 키: {key}")

        return selector


# 편의를 위한 상수
LOGIN_ID_INPUT = NaverSelectors.LOGIN["id_input"]
LOGIN_PW_INPUT = NaverSelectors.LOGIN["pw_input"]
LOGIN_BTN = NaverSelectors.LOGIN["login_btn"]
