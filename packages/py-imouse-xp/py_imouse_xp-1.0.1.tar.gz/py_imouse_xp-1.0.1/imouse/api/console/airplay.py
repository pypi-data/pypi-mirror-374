from typing import TYPE_CHECKING, List
from ...imouse_types import SetDeviceAirplayParams
from ...models import ImServerConfigResponse, CommonResponse

if TYPE_CHECKING:
    from .. import API


class AirPlay:
    def __init__(self, api: "API"):
        self._api = api

    def global_config(
            self,
            fps: int = None,
            ratio: int = None,
            audio: bool = None,
            img_fps: int = None
    ) -> bool:
        """设置 iMouse 全局 AirPlay 配置（用于所有设备默认使用）"""
        # Get current config directly via API
        config_response = self._api.call(ImServerConfigResponse, self._api._payload.config_imserver_get)
        if config_response.status != 200 or config_response.data.code != 0:
            return False
        
        config = config_response.data
        update_map = {
            'air_play_fps': fps,
            'air_play_ratio': ratio,
            'air_play_audio': audio,
            'air_play_img_fps': img_fps,
        }
        for key, value in update_map.items():
            if value is not None:
                setattr(config, key, value)
        
        result = self._api.call(ImServerConfigResponse, self._api._payload.config_imserver_set, config)
        return result.status == 200 and result.data.code == 0

    def config(
            self,
            device_ids: str,
            fps: int = None,
            ratio: int = None,
            refresh: int = None,
            audio: int = None,
            img_fps: int = None
    ) -> bool:
        """设置指定设备的 AirPlay 配置"""
        params = SetDeviceAirplayParams(
            fps=fps,
            ratio=ratio,
            refresh=refresh,
            audio=audio,
            img_fps=img_fps
        )
        result = self._api.call(CommonResponse, self._api._payload.device_airplay_set, device_ids, params)
        return result.status == 200 and result.data.code == 0

    def connect(self, device_ids: str) -> bool:
        """指定设备的投屏"""
        result = self._api.call(CommonResponse, self._api._payload.device_airplay_connect, device_ids)
        return result.status == 200 and result.data.code == 0

    def connect_all(self) -> bool:
        """让所有离线的设备投屏"""
        result = self._api.call(CommonResponse, self._api._payload.device_airplay_connect_all)
        return result.status == 200 and result.data.code == 0

    def disconnect(self, device_ids: str) -> bool:
        """断开指定设备的投屏"""
        result = self._api.call(CommonResponse, self._api._payload.device_airplay_disconnect, device_ids)
        return result.status == 200 and result.data.code == 0

    def name(self, name: str) -> bool:
        """设置 AirPlay 的显示名称"""
        config = self._console.get_imserver_config
        config.air_play_name = name
        result = self._api.call(ImServerConfigResponse, self._api._payload.config_imserver_set, config)
        return result.status == 200 and result.data.code == 0

    def auto_connect(self, state: bool) -> bool:
        """设置是否自动连接设备"""
        config = self._console.get_imserver_config
        config.auto_connect = state
        result = self._api.call(ImServerConfigResponse, self._api._payload.config_imserver_set, config)
        return result.status == 200 and result.data.code == 0

    def failed_retry(self, num: int) -> bool:
        """设置连接失败后的重试次数"""
        config = self._console.get_imserver_config
        config.connect_failed_retry = num
        result = self._api.call(ImServerConfigResponse, self._api._payload.config_imserver_set, config)
        return result.status == 200 and result.data.code == 0

    def gpu_decoding(self, state: bool) -> bool:
        """设置是否启用 GPU 硬件解码"""
        config = self._console.get_imserver_config
        config.enable_hardware_acceleration = state
        result = self._api.call(ImServerConfigResponse, self._api._payload.config_imserver_set, config)
        return result.status == 200 and result.data.code == 0

    def set_mdns_type(self, mdns_type: int, ip_list: List[str] = None) -> bool:
        """设置 mDNS 类型及允许的 IP 列表"""
        config = self._console.get_imserver_config
        config.mdns_type = mdns_type
        if ip_list is not None:
            config.allow_ip_list = ip_list

        result = self._api.call(ImServerConfigResponse, self._api._payload.config_imserver_set, config)
        return result.status == 200 and result.data.code == 0

    def restart_mdns(self) -> bool:
        """重新广播投屏"""
        result = self._api.call(CommonResponse, self._api._payload.imserver_regmdns)
        return result.status == 200 and result.data.code == 0
