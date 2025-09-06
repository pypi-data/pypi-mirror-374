from typing import TYPE_CHECKING, List

from ...models import DeviceInfo, DeviceListResponse, IdListResponse, CommonResponse
from ...imouse_types import SetDeviceParams

if TYPE_CHECKING:
    from .. import API


class Device:
    def __init__(self, api: "API"):
        self._api = api

    def list_by_id(self, device_ids: str = "") -> List[DeviceInfo]:
        """通过设备id获取设备列表"""
        ret = self._api.call(DeviceListResponse, self._api._payload.device_get, device_ids)
        if ret.status != 200 or ret.data.code != 0:
            return []
        return ret.data.device_list or []

    def list_by_group(self, gid: str = "0") -> List[DeviceInfo]:
        """通过分组id获取设备列表"""
        ret = self._api.call(DeviceListResponse, self._api._payload.device_group_getdev, gid)
        if ret.status != 200 or ret.data.code != 0:
            return []
        return ret.data.device_list or []

    def set_name(self, device_ids: str, name: str) -> List[str]:
        """设置设备名称"""
        ret = self._api.call(IdListResponse, self._api._payload.device_set, device_ids, SetDeviceParams(name=name))
        if ret.status != 200 or ret.data.code != 0:
            return []
        return ret.data.id_list or []

    def bind_hardware(self, device_id: str, vid: str, pid: str) -> List[str]:
        """绑定硬件"""
        ret = self._api.call(IdListResponse, self._api._payload.device_set, device_id, SetDeviceParams(vid=vid, pid=pid))
        if ret.status != 200 or ret.data.code != 0:
            return []
        return ret.data.id_list or []

    def set_mouse_location(self, device_ids: str, location_crc: str) -> List[str]:
        """设置鼠标参数"""
        ret = self._api.call(IdListResponse, self._api._payload.device_set, device_ids, SetDeviceParams(location_crc=location_crc))
        if ret.status != 200 or ret.data.code != 0:
            return []
        return ret.data.id_list or []

    def set_group(self, device_ids: str, group_id: str) -> List[str]:
        """设置设备分组"""
        ret = self._api.call(IdListResponse, self._api._payload.device_set, device_ids, SetDeviceParams(gid=group_id))
        if ret.status != 200 or ret.data.code != 0:
            return []
        return ret.data.id_list or []

    def delete(self, device_ids: str) -> List[str]:
        """删除设备"""
        ret = self._api.call(IdListResponse, self._api._payload.device_del, device_ids)
        if ret.status != 200 or ret.data.code != 0:
            return []
        return ret.data.id_list or []

    def restart(self, device_ids: str) -> bool:
        """重启设备"""
        result = self._api.call(CommonResponse, self._api._payload.device_restart, device_ids)
        return result.status == 200 and result.data.code == 0
