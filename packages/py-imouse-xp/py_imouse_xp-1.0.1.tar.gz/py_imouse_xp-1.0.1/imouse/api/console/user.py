from typing import TYPE_CHECKING, Optional

from ...models import UserData, UserResponse, CommonResponse

if TYPE_CHECKING:
    from .. import API


class User:
    def __init__(self, api: "API"):
        self._api = api

    def get(self) -> Optional[UserData]:
        """获取imouse账号信息"""
        ret = self._api.call(UserResponse, self._api._payload.config_user_info)
        if not (ret.status == 200 and ret.data.code == 0):
            return None
        return ret.data

    def login(self, user_name: str, password: str, utag: int) -> Optional[UserData]:
        """登录imouse账号"""
        ret = self._api.call(UserResponse, self._api._payload.config_user_login, user_name, password, utag)
        if not (ret.status == 200 and ret.data.code == 0):
            return None
        return ret.data

    def logout(self) -> bool:
        """退出imouse账号"""
        result = self._api.call(CommonResponse, self._api._payload.config_user_logout)
        return result.status == 200 and result.data.code == 0

    def switch_utag(self, utag: int) -> bool:
        """切换imouse子账号"""
        result = self._api.call(CommonResponse, self._api._payload.config_user_switch, utag)
        return result.status == 200 and result.data.code == 0
