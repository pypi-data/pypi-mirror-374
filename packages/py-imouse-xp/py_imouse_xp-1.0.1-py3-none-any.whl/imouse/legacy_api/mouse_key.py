from typing import Optional, List, Union, TYPE_CHECKING

from ..models import CommonResponse
from ..imouse_types import MouseSwipeParams

if TYPE_CHECKING:
    from . import LegacyAPI


class MouseKey:
    def __init__(self, api: "LegacyAPI"):
        self._api = api

    def mouse_click(self, device_id, button: str, x, y, time: int = 0) -> CommonResponse:
        """https://www.imouse.cc/XP%E7%89%88API%E6%96%87%E6%A1%A3/%E9%BC%A0%E6%A0%87%E9%94%AE%E7%9B%98/%E9%BC%A0%E6%A0%87%E7%82%B9%E5%87%BB"""
        return self._api.call(CommonResponse, self._api._payload.mouse_click, device_id, button, x, y, time)

    def mouse_swipe(self, device_id, params: MouseSwipeParams) -> CommonResponse:
        """https://www.imouse.cc/XP%E7%89%88API%E6%96%87%E6%A1%A3/%E9%BC%A0%E6%A0%87%E9%94%AE%E7%9B%98/%E9%BC%A0%E6%A0%87%E6%BB%91%E5%8A%A8"""
        return self._api.call(CommonResponse, self._api._payload.mouse_swipe, device_id, params)

    def mouse_up(self, device_id, button: str) -> CommonResponse:
        """https://www.imouse.cc/XP%E7%89%88API%E6%96%87%E6%A1%A3/%E9%BC%A0%E6%A0%87%E9%94%AE%E7%9B%98/%E9%BC%A0%E6%A0%87%E5%BC%B9%E8%B5%B7"""
        return self._api.call(CommonResponse, self._api._payload.mouse_up, device_id, button)

    def mouse_down(self, device_id, button: str) -> CommonResponse:
        """https://www.imouse.cc/XP%E7%89%88API%E6%96%87%E6%A1%A3/%E9%BC%A0%E6%A0%87%E9%94%AE%E7%9B%98/%E9%BC%A0%E6%A0%87%E6%8C%89%E4%B8%8B"""
        return self._api.call(CommonResponse, self._api._payload.mouse_down, device_id, button)

    def mouse_move(self, device_id: str, x, y: int) -> CommonResponse:
        """https://www.imouse.cc/XP%E7%89%88API%E6%96%87%E6%A1%A3/%E9%BC%A0%E6%A0%87%E9%94%AE%E7%9B%98/%E9%BC%A0%E6%A0%87%E7%A7%BB%E5%8A%A8"""
        return self._api.call(CommonResponse, self._api._payload.mouse_move, device_id, x, y)

    def mouse_reset(self, device_id: str) -> CommonResponse:
        """https://www.imouse.cc/XP%E7%89%88API%E6%96%87%E6%A1%A3/%E9%BC%A0%E6%A0%87%E9%94%AE%E7%9B%98/%E9%BC%A0%E6%A0%87%E5%A4%8D%E4%BD%8D"""
        return self._api.call(CommonResponse, self._api._payload.mouse_reset, device_id)

    def mouse_wheel(self, device_id, direction: str, len, number: int) -> CommonResponse:
        """https://www.imouse.cc/XP%E7%89%88API%E6%96%87%E6%A1%A3/%E9%BC%A0%E6%A0%87%E9%94%AE%E7%9B%98/%E9%BC%A0%E6%A0%87%E6%BB%9A%E8%BD%AE"""
        return self._api.call(CommonResponse, self._api._payload.mouse_wheel, device_id, direction, len, number)

    def key_sendkey(self, device_id, key, fn_key: str) -> CommonResponse:
        """https://www.imouse.cc/XP%E7%89%88API%E6%96%87%E6%A1%A3/%E9%BC%A0%E6%A0%87%E9%94%AE%E7%9B%98/%E9%94%AE%E7%9B%98%E8%BE%93%E5%85%A5"""
        return self._api.call(CommonResponse, self._api._payload.key_sendkey, device_id, key, fn_key)

    def key_sendhid(self, device_id, command_list: List[str]) -> CommonResponse:
        """https://www.imouse.cc/XP%E7%89%88API%E6%96%87%E6%A1%A3/%E9%BC%A0%E6%A0%87%E9%94%AE%E7%9B%98/%E9%94%AE%E7%9B%98%E9%AB%98%E7%BA%A7%E6%93%8D%E4%BD%9C"""
        return self._api.call(CommonResponse, self._api._payload.key_sendhid, device_id, command_list)