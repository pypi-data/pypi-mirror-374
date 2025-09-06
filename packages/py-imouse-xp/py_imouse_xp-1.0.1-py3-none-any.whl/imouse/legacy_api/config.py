from typing import TYPE_CHECKING, List

from ..models import UsbListResponse, ImServerConfigResponse, ImServerConfigData, UsbInfo, CommonResponse

if TYPE_CHECKING:
    from . import LegacyAPI


class Config:
    def __init__(self, api: "LegacyAPI"):
        self._api = api


    def config_usb_get(self) -> UsbListResponse:
        """https://www.imouse.cc/XP%E7%89%88API%E6%96%87%E6%A1%A3/%E9%85%8D%E7%BD%AE%E7%9B%B8%E5%85%B3/%E8%8E%B7%E5%8F%96%E5%B7%B2%E8%BF%9E%E6%8E%A5%E7%A1%AC%E4%BB%B6%E5%88%97%E8%A1%A8"""
        return self._api.call(UsbListResponse, self._api._payload.config_usb_get)

    def config_imserver_get(self) -> ImServerConfigResponse:
        """https://www.imouse.cc/XP%E7%89%88API%E6%96%87%E6%A1%A3/%E9%85%8D%E7%BD%AE%E7%9B%B8%E5%85%B3/%E8%8E%B7%E5%8F%96%E5%86%85%E6%A0%B8%E9%85%8D%E7%BD%AE"""
        return self._api.call(ImServerConfigResponse, self._api._payload.config_imserver_get)

    def config_imserver_set(self,params: ImServerConfigData) -> ImServerConfigResponse:
        """https://www.imouse.cc/XP%E7%89%88API%E6%96%87%E6%A1%A3/%E9%85%8D%E7%BD%AE%E7%9B%B8%E5%85%B3/%E8%AE%BE%E7%BD%AE%E5%86%85%E6%A0%B8%E9%85%8D%E7%BD%AE"""
        return self._api.call(ImServerConfigResponse, self._api._payload.config_imserver_set, params)

    def imserver_regmdns(self) -> CommonResponse:
        """https://www.imouse.cc/XP%E7%89%88API%E6%96%87%E6%A1%A3/%E9%85%8D%E7%BD%AE%E7%9B%B8%E5%85%B3/%E9%87%8D%E6%96%B0%E5%B9%BF%E6%92%AD%E6%8A%95%E5%B1%8F"""
        return self._api.call(CommonResponse, self._api._payload.imserver_regmdns)

    def imserver_restart(self) -> CommonResponse:
        """https://www.imouse.cc/XP%E7%89%88API%E6%96%87%E6%A1%A3/%E9%85%8D%E7%BD%AE%E7%9B%B8%E5%85%B3/%E9%87%8D%E5%90%AF%E5%86%85%E6%A0%B8"""
        return self._api.call(CommonResponse, self._api._payload.imserver_restart)