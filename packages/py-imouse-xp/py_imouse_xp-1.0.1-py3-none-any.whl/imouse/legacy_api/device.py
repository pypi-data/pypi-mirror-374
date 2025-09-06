from typing import Optional, Union, TYPE_CHECKING

from ..models import DeviceListResponse, IdListResponse, GroupListResponse, \
    DeviceInfo, GroupInfo, CommonResponse
from ..imouse_types import SetDeviceParams, SetDeviceAirplayParams

if TYPE_CHECKING:
    from . import LegacyAPI


class Device:
    def __init__(self, api: "LegacyAPI"):
        self._api = api

    def device_get(self, device_id: str = '') -> DeviceListResponse:
        """https://www.imouse.cc/XP%E7%89%88API%E6%96%87%E6%A1%A3/%E8%AE%BE%E5%A4%87%E7%9B%B8%E5%85%B3/%E8%8E%B7%E5%8F%96%E8%AE%BE%E5%A4%87%E5%88%97%E8%A1%A8"""
        return self._api.call(DeviceListResponse, self._api._payload.device_get, device_id)

    def device_group_get(self, group_id: str = '') -> GroupListResponse:
        """https://www.imouse.cc/XP%E7%89%88API%E6%96%87%E6%A1%A3/%E8%AE%BE%E5%A4%87%E7%9B%B8%E5%85%B3/%E8%8E%B7%E5%8F%96%E5%88%86%E7%BB%84%E5%88%97%E8%A1%A8"""
        return self._api.call(GroupListResponse, self._api._payload.device_group_get, group_id)

    def device_group_getdev(self, group_id: str) -> DeviceListResponse:
        """https://www.imouse.cc/XP%E7%89%88API%E6%96%87%E6%A1%A3/%E8%AE%BE%E5%A4%87%E7%9B%B8%E5%85%B3/%E8%8E%B7%E5%8F%96%E5%88%86%E7%BB%84%E5%86%85%E8%AE%BE%E5%A4%87"""
        return self._api.call(DeviceListResponse, self._api._payload.device_group_getdev, group_id)

    def device_set_name(self, device_id, name: str) -> CommonResponse:
        return self._api.call(CommonResponse, self._api._payload.device_set,
                             device_id, SetDeviceParams(name=name))

    def device_bind_hardware(self, device_id, vid, pid: str) -> CommonResponse:
        return self._api.call(CommonResponse, self._api._payload.device_set,
                             device_id, SetDeviceParams(vid=vid, pid=pid))

    def device_set_mouse_location(self, device_id, location_crc: str) -> CommonResponse:
        return self._api.call(CommonResponse, self._api._payload.device_set,
                             device_id, SetDeviceParams(location_crc=location_crc))

    def device_set_group(self, device_id, group_id: str) -> CommonResponse:
        return self._api.call(CommonResponse, self._api._payload.device_set,
                             device_id, SetDeviceParams(gid=group_id))

    def device_del(self, device_id: str) -> CommonResponse:
        """https://www.imouse.cc/XP%E7%89%88API%E6%96%87%E6%A1%A3/%E8%AE%BE%E5%A4%87%E7%9B%B8%E5%85%B3/%E5%88%A0%E9%99%A4%E8%AE%BE%E5%A4%87"""
        return self._api.call(CommonResponse, self._api._payload.device_del, device_id)

    def device_group_set(self, group_id: str, group_name: str) -> GroupListResponse:
        """https://www.imouse.cc/XP%E7%89%88API%E6%96%87%E6%A1%A3/%E8%AE%BE%E5%A4%87%E7%9B%B8%E5%85%B3/%E8%AE%BE%E7%BD%AE%E5%88%86%E7%BB%84"""
        return self._api.call(GroupListResponse, self._api._payload.device_group_set, group_id, group_name)

    def device_group_del(self, group_id: str) -> IdListResponse:
        """https://www.imouse.cc/XP%E7%89%88API%E6%96%87%E6%A1%A3/%E8%AE%BE%E5%A4%87%E7%9B%B8%E5%85%B3/%E5%88%A0%E9%99%A4%E5%88%86%E7%BB%84"""
        return self._api.call(IdListResponse, self._api._payload.device_group_del, group_id)

    def device_airplay_set(self, device_id: str, params: SetDeviceAirplayParams) -> CommonResponse:
        """https://www.imouse.cc/XP%E7%89%88API%E6%96%87%E6%A1%A3/%E8%AE%BE%E5%A4%87%E7%9B%B8%E5%85%B3/%E8%AE%BE%E7%BD%AE%E8%AE%BE%E5%A4%87%E6%8A%95%E5%B1%8F%E9%85%8D%E7%BD%AE"""
        return self._api.call(CommonResponse, self._api._payload.device_airplay_set, device_id, params)

    def device_airplay_connect(self, device_id: str) -> CommonResponse:
        """https://www.imouse.cc/XP%E7%89%88API%E6%96%87%E6%A1%A3/%E8%AE%BE%E5%A4%87%E7%9B%B8%E5%85%B3/%E8%BF%9E%E6%8E%A5%E6%8A%95%E5%B1%8F"""
        return self._api.call(CommonResponse, self._api._payload.device_airplay_connect, device_id)

    def device_airplay_connect_all(self) -> CommonResponse:
        """https://www.imouse.cc/XP%E7%89%88API%E6%96%87%E6%A1%A3/%E8%AE%BE%E5%A4%87%E7%9B%B8%E5%85%B3/%E6%8A%95%E5%B1%8F%E6%89%80%E6%9C%89"""
        return self._api.call(CommonResponse, self._api._payload.device_airplay_connect_all)

    def device_airplay_disconnect(self, device_id: str) -> CommonResponse:
        """https://www.imouse.cc/XP%E7%89%88API%E6%96%87%E6%A1%A3/%E8%AE%BE%E5%A4%87%E7%9B%B8%E5%85%B3/%E6%96%AD%E5%BC%80%E6%8A%95%E5%B1%8F"""
        return self._api.call(CommonResponse, self._api._payload.device_airplay_disconnect, device_id)

    def device_restart(self, device_id: str) -> CommonResponse:
        """https://www.imouse.cc/XP%E7%89%88API%E6%96%87%E6%A1%A3/%E8%AE%BE%E5%A4%87%E7%9B%B8%E5%85%B3/%E9%87%8D%E5%90%AF%E8%AE%BE%E5%A4%87"""
        return self._api.call(CommonResponse, self._api._payload.device_restart, device_id)

    def device_usb_restart(self, vpids: str) -> CommonResponse:
        """https://www.imouse.cc/XP%E7%89%88API%E6%96%87%E6%A1%A3/%E8%AE%BE%E5%A4%87%E7%9B%B8%E5%85%B3/%E9%87%8D%E5%90%AFusb"""
        return self._api.call(CommonResponse, self._api._payload.device_usb_restart, vpids)

    def device_sort_set(self, sort_index, sort_value: int) -> CommonResponse:
        """https://www.imouse.cc/XP%E7%89%88API%E6%96%87%E6%A1%A3/%E8%AE%BE%E5%A4%87%E7%9B%B8%E5%85%B3/%E8%AE%BE%E7%BD%AE%E8%AE%BE%E5%A4%87%E5%88%97%E8%A1%A8%E6%8E%92%E5%BA%8F"""
        return self._api.call(CommonResponse, self._api._payload.device_sort_set, sort_index, sort_value)

    def device_sort_get(self) -> CommonResponse:
        """https://www.imouse.cc/XP%E7%89%88API%E6%96%87%E6%A1%A3/%E8%AE%BE%E5%A4%87%E7%9B%B8%E5%85%B3/%E8%8E%B7%E5%8F%96%E8%AE%BE%E5%A4%87%E5%88%97%E8%A1%A8%E6%8E%92%E5%BA%8F"""
        return self._api.call(CommonResponse, self._api._payload.device_sort_get)