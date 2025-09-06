from .api import API
from .legacy_api import LegacyAPI
from .imouse_types import ModeType

__version__ = "1.0.1"


def legacy(host: str = "localhost", port: int = 9911, mode: ModeType = "websocket"):
    """
    创建 LegacyAPI 实例。
    
    :param host: 主机地址，默认 "localhost"
    :param port: 端口号，默认 9911
    :param mode: 通信模式，可选值: "http", "websocket"。默认为 "websocket"
    :return: LegacyAPI 实例
    """
    return LegacyAPI(host, port, mode=mode)


def api(host: str = "localhost", port: int = 9911, mode: ModeType = "websocket"):
    """
    创建 API 实例。
    
    :param host: 主机地址，默认 "localhost"
    :param port: 端口号，默认 9911
    :param mode: 通信模式，可选值: "http", "websocket"。默认为 "websocket"
    :return: API 实例
    """
    return API(host, port, mode=mode)


__all__ = ["legacy", "api", "__version__"]
