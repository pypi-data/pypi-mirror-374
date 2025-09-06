from typing import TYPE_CHECKING, List

from ...models import UsbInfo, UsbListResponse, CommonResponse

if TYPE_CHECKING:
    from .. import API


class Usb:
    def __init__(self, api: "API"):
        self._api = api

    def get(self) -> List[UsbInfo]:
        """获取硬件列表"""
        ret = self._api.call(UsbListResponse, self._api._payload.config_usb_get)
        if not (ret.status == 200 and ret.data.code == 0):
            return []
        return ret.data.usb_list or []

    def restart(self, vpids: str) -> bool:
        """重启硬件"""
        result = self._api.call(CommonResponse, self._api._payload.device_usb_restart, vpids)
        return result.status == 200 and result.data.code == 0
