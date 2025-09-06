from typing import TYPE_CHECKING, List, Optional

from ...models import DeviceSortData, DeviceSortResponse, ImServerConfigResponse

if TYPE_CHECKING:
    from .. import API


class Config:
    def __init__(self, api: "API"):
        self._api = api
    
    def _get_imserver_config(self):
        """Get ImServer config"""
        ret = self._api.call(ImServerConfigResponse, self._api._payload.config_imserver_get)
        if ret.status == 200 and ret.data.code == 0:
            return ret.data
        return None

    @property
    def device_sort(self) -> Optional[DeviceSortData]:
        """获取设备列表排序"""
        ret = self._api.call(DeviceSortResponse, self._api._payload.device_sort_get)
        if not (ret.status == 200 and ret.data.code == 0):
            return None
        return ret.data

    def set_device_sort(self, index, value: int) -> Optional[DeviceSortData]:
        """设置设备列表排序"""
        ret = self._api.call(DeviceSortResponse, self._api._payload.device_sort_set, index, value)
        if not (ret.status == 200 and ret.data.code == 0):
            return None
        return ret.data


    @property
    def language(self) -> Optional[str]:
        """获取控制台显示语言"""
        config = self._get_imserver_config()
        if config is None:
            return None
        return config.lang

    @language.setter
    def language(self, value: str):
        """设置控制台语言"""
        config = self._get_imserver_config()
        config.lang = value
        result = self._api.call(ImServerConfigResponse, self._api._payload.config_imserver_set, config)
        if not (result.status == 200 and result.data.code == 0):
            raise ValueError("语言设置失败")

    @property
    def language_list(self) -> List[str]:
        """获取控制台支持语言列表"""
        config = self._get_imserver_config()
        return config.lang_list

    def auto_update(self,state: bool)->bool:
        """设置是否自动升级"""
        config = self._get_imserver_config()
        config.auto_update = state
        result = self._api.call(ImServerConfigResponse, self._api._payload.config_imserver_set, config)
        return result.status == 200 and result.data.code == 0


    def thread_mode(self,state: bool)->bool:
        """设置启用线程模式批量控制"""
        config = self._get_imserver_config()
        config.thread_mode = state
        result = self._api.call(ImServerConfigResponse, self._api._payload.config_imserver_set, config)
        return result.status == 200 and result.data.code == 0

    def mouse_mode(self,state: bool)->bool:
        """设置是否使用快准狠鼠标模式"""
        config = self._get_imserver_config()
        config.mouse_mode = state
        result = self._api.call(ImServerConfigResponse, self._api._payload.config_imserver_set, config)
        return result.status == 200 and result.data.code == 0

    def flip_right(self,state: bool)->bool:
        """设置横屏向右翻转"""
        config = self._get_imserver_config()
        config.flip_right = state
        result = self._api.call(ImServerConfigResponse, self._api._payload.config_imserver_set, config)
        return result.status == 200 and result.data.code == 0

