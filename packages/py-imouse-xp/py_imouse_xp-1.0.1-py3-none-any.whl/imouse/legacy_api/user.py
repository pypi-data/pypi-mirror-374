from typing import TYPE_CHECKING

from ..models import UserResponse, CommonResponse

if TYPE_CHECKING:
    from . import LegacyAPI


class User:
    def __init__(self, api: "LegacyAPI"):
        self._api = api

    def config_user_login(self, account_number, password: str, utag: int = 1) -> UserResponse:
        """https://www.imouse.cc/XP%E7%89%88API%E6%96%87%E6%A1%A3/%E7%94%A8%E6%88%B7%E7%9B%B8%E5%85%B3/%E7%99%BB%E5%BD%95"""
        return self._api.call(UserResponse,
                                        self._api._payload.config_user_login, account_number, password, utag)

    def config_user_logout(self) -> CommonResponse:
        """https://www.imouse.cc/XP%E7%89%88API%E6%96%87%E6%A1%A3/%E7%94%A8%E6%88%B7%E7%9B%B8%E5%85%B3/%E9%80%80%E5%87%BA%E7%99%BB%E5%BD%95"""
        return self._api.call(CommonResponse, self._api._payload.config_user_logout)

    def config_user_info(self) -> UserResponse:
        """https://www.imouse.cc/XP%E7%89%88API%E6%96%87%E6%A1%A3/%E7%94%A8%E6%88%B7%E7%9B%B8%E5%85%B3/%E8%8E%B7%E5%8F%96%E7%94%A8%E6%88%B7%E4%BF%A1%E6%81%AF"""
        return self._api.call(UserResponse,
                                        self._api._payload.config_user_info)

    def config_user_switch(self, utag: int) -> CommonResponse:
        """https://www.imouse.cc/XP%E7%89%88API%E6%96%87%E6%A1%A3/%E7%94%A8%E6%88%B7%E7%9B%B8%E5%85%B3/%E5%88%87%E6%8D%A2%E5%AD%90%E8%B4%A6%E5%8F%B7"""
        return self._api.call(CommonResponse, self._api._payload.config_user_switch, utag)
