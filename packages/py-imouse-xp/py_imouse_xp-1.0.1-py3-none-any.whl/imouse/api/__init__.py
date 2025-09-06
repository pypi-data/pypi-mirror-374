from .device import Device
from .console import Console
from ..models import DeviceInfo, DeviceListResponse
from ..shared.client import Client
from ..shared.payload import Payload
from ..shared.base_api import BaseAPI
from ..imouse_types import ModeType
from ..utils.utils import format_device_info


class API(BaseAPI):
    def __init__(self, host: str, port: int = 9911, timeout: int = 15, mode: ModeType = "websocket"):
        """
        初始化 API 类。
        
        :param host: 主机地址
        :param port: 端口号，默认 9911
        :param timeout: 超时时间，默认 15 秒
        :param mode: 通信模式，可选值: "http", "websocket"。默认为 "websocket"
        """
        super().__init__()
        self._client = Client(host, port, timeout, mode)
        self._payload = Payload()
        self._client.start()

    @property
    def console(self):
        return Console(self)
    
    def device(self, device_id: str):
        return Device(self, device_id)

    def devices(self):
        device_list_response = self.call(DeviceListResponse, self._payload.device_get)
        if device_list_response.status != 200 or device_list_response.data.code != 0:
            return []

        devices = []
        for device_info in device_list_response.data.device_list:
            devices.append(format_device_info(device_info))
        return devices
