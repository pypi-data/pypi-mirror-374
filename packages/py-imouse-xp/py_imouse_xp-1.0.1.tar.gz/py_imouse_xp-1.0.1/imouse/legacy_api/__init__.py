import json

from ..shared.event_dispatcher import *
from ..shared.payload import *
import time
from ..shared.client import Client
from ..shared.base_api import BaseAPI
from .config import Config
from .device import Device
from .mouse_key import MouseKey
from ..utils import logger
from .pic import Pic
from .shortcut import Shortcut
from .user import User
from ..imouse_types import ModeType


class LegacyAPI(BaseAPI):
    def __init__(self, host: str, port: int = 9911, imouse_call_back=None, timeout: int = 15, mode: ModeType = "websocket"):
        """
        初始化 LegacyAPI 类。
        
        :param host: 主机地址
        :param port: 端口号，默认 9911
        :param imouse_call_back: 回调函数
        :param timeout: 超时时间，默认 15 秒
        :param mode: 通信模式，可选值: "http", "websocket"。默认为 "websocket"
        """
        super().__init__()
        self._imouse_call_back = imouse_call_back
        self._payload = Payload()
        self._client = Client(host, port, timeout, mode)
        
        # Override the client's message handler to point to our handler
        self._client._handle_message = self._handle_message
        self._client.start()

    def _handle_message(self, message: str):
        try:
            event.emit(json.loads(message))
        except Exception as e:
            logger.error(f'_handle_message发生异常: {e}')

    @property
    def device(self):
        return Device(self)

    @property
    def config(self):
        return Config(self)
    
    @property
    def user(self):
        return User(self)
        
    @property
    def mouse_key(self):
        return MouseKey(self)
        
    @property
    def pic(self):
        return Pic(self)
        
    @property
    def shortcut(self):
        return Shortcut(self)

