from typing import TYPE_CHECKING

from ...imouse_types import MouseSwipeParams
from ...models import CommonResponse

if TYPE_CHECKING:
    from . import Device


class Mouse:
    def __init__(self, device: "Device"):
        self._device = device
        self._api = device._api
        self._device_id = device.id

    def click(self, button: str, x: int, y: int, time: int = 0) -> CommonResponse:
        """点击"""
        return self._api.call(CommonResponse, self._api._payload.mouse_click,
                             self._device_id, button, x, y, time)

    def swipe(self, params: MouseSwipeParams) -> CommonResponse:
        """滑动"""
        return self._api.call(CommonResponse, self._api._payload.mouse_swipe,
                             self._device_id, params)

    def up(self, button: str) -> CommonResponse:
        """弹起"""
        return self._api.call(CommonResponse, self._api._payload.mouse_up,
                             self._device_id, button)

    def down(self, button: str) -> CommonResponse:
        """按下"""
        return self._api.call(CommonResponse, self._api._payload.mouse_down,
                             self._device_id, button)

    def move(self, x: int, y: int) -> CommonResponse:
        """移动"""
        return self._api.call(CommonResponse, self._api._payload.mouse_move,
                             self._device_id, x, y)

    def reset(self) -> CommonResponse:
        """复位"""
        return self._api.call(CommonResponse, self._api._payload.mouse_reset,
                             self._device_id)

    def wheel(self, direction: str, len: int, number: int) -> CommonResponse:
        """滚轮"""
        return self._api.call(CommonResponse, self._api._payload.mouse_wheel,
                             self._device_id, direction, len, number)