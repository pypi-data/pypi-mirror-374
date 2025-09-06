import abc
import json
import threading
from typing import Union

import requests
import websocket
from websocket import WebSocketApp, WebSocketException

from ..utils import logger
from ..utils.utils import safe_json_log
from ..imouse_types import ModeType


class Client:
    __metaclass__ = abc.ABCMeta

    def __init__(self, host: str, port: int, timeout: int = 15, mode: ModeType = "websocket"):
        """
        初始化 Client 类。

        :param host: 主机地址。
        :param port: 端口号。
        :param timeout: 网络请求超时时间。
        :param mode: 通信模式，可选值: "http", "websocket"。默认为 "websocket"。
        """
        self.mode = mode
        self._global_timeout = timeout
        self.host = host
        self.port = port
        self.base_url = f'http://{host}:{port}/api'
        self._ws = WebSocketApp
        self._is_working = False
        self._is_connected = False

    def start(self):
        """启动网络通信。"""
        if self.mode == "websocket":
            self._is_working = True
            t1 = threading.Thread(target=self._initialize_websocket, name='WebSocket 初始化')
            logger.info("启动网络通信")
            t1.start()
        else:
            # HTTP mode - no persistent connection needed
            self._is_connected = True
            logger.info("HTTP 模式启动")

    def stop(self):
        """停止网络通信。"""
        self._is_working = False
        if self.mode == "websocket" and self._is_connected:
            self._ws.close()
        elif self.mode == "http":
            self._is_connected = False

    def is_connected(self) -> bool:
        """返回网络是否已连接。"""
        return self._is_connected

    def _network_request(self, data: str, timeout: int = 0, is_async: bool = False) -> Union[str, bytes]:
        """
        发送网络请求。

        :param data: 要发送的数据。
        :param timeout: 超时时间。
        :param is_async: 是否异步请求（仅在websocket模式下有效）。
        :return: 响应数据。
        """
        ret = None
        try:
            if timeout == 0:
                timeout = self._global_timeout
            
            # Force HTTP mode or handle async WebSocket requests
            if self.mode == "http" or not is_async:
                logger.debug(safe_json_log(data, 'HTTP请求:->'))
                ret = requests.post(self.base_url, json=json.loads(data), timeout=timeout)
                if ret.status_code == 200:
                    content_type = ret.headers.get("Content-Type", "")
                    if "text" in content_type or "json" in content_type:
                        ret = ret.text
                        logger.debug(safe_json_log(ret, '响应:->'))
                    else:
                        ret = ret.content
                else:
                    data_dict = {"data": {"code": 33, "id": "", "message": "失败"}, "status": ret.status_code, "msgid": 0,
                                 'fun': json.loads(data).get('fun'), 'message': '请求失败'}
                    ret = json.dumps(data_dict)
            elif self.mode == "websocket" and is_async:
                if not self._is_connected:
                    raise RuntimeError("WebSocket 连接未建立，无法发送异步请求")
                logger.debug(f'WebSocket请求，timeout={timeout}: \r\n' + data)
                self._ws.send(data)
            else:
                raise ValueError("无效的请求模式配置")
                
        except requests.exceptions.RequestException as e:
            logger.error(f'网络请求错误: {e}')
            data_dict = {"data": {"code": 33, "id": "", "message": "失败"}, "status": 400, "msgid": 0,
                         'fun': json.loads(data).get('fun'), 'message': '网络请求错误'}
            ret = json.dumps(data_dict)
        except Exception as e:
            logger.error(f'请求异常: {e}')
            data_dict = {"data": {"code": 33, "id": "", "message": "失败"}, "status": 500, "msgid": 0,
                         'fun': json.loads(data).get('fun'), 'message': str(e)}
            ret = json.dumps(data_dict)
        return ret

    def _handle_message(self, message: str):
        """
        处理接收到的消息的默认实现（可以被子类重写）。

        :param message: 接收到的消息。
        """
        # Default implementation does nothing - suitable for request/response only usage
        pass

    def _on_data(self, ws, message, data_type, continue_flag):
        """
        收到数据的回调方法。

        :param ws: WebSocket 实例。
        :param message: 收到的消息。
        :param data_type: 数据类型。
        :param continue_flag: 指示消息是否继续的标志。
        """
        if data_type == websocket.ABNF.OPCODE_TEXT:
            logger.debug(f'回调数据: \r\n{message}')
            self._handle_message(message)

    def _on_error(self, ws, error):
        """
        WebSocket 错误的回调方法。

        :param ws: WebSocket 实例。
        :param error: 错误消息。
        """
        # log.info(f'WebSocket 错误: {error}')
        pass

    def _on_close(self, ws, close_status_code, close_msg):
        """
        WebSocket 关闭事件的回调方法。

        :param ws: WebSocket 实例。
        :param close_status_code: 关闭事件的状态码。
        :param close_msg: 关闭消息。
        """

        if self._is_connected:
            self._handle_message(
                json.dumps({"fun": "im_disconnect", "status": 200, "message": "", "msgid": 0, "data": {}}))
            logger.debug('WebSocket 连接已关闭')
        self._is_connected = False

    def _on_open(self, ws):
        """
        WebSocket 打开事件的回调方法。

        :param ws: WebSocket 实例。
        """
        self._is_connected = True
        logger.debug('WebSocket 连接已打开')

    def _initialize_websocket(self):
        """
        初始化 WebSocket 连接。
        """
        self._ws = websocket.WebSocketApp(f'ws://{self.host}:{self.port}/api',
                                          on_data=self._on_data,
                                          on_error=self._on_error,
                                          on_open=self._on_open,
                                          on_close=self._on_close)
        while self._is_working:
            try:
                self._ws.run_forever(ping_interval=1)
                self._is_connected = False
            except WebSocketException as e:
                self._ws.close()
                logger.error(f'WebSocket 异常: {e}')
            except KeyboardInterrupt:
                logger.debug('用户中断程序')
                break
            except Exception as e:
                logger.error(f'发生异常: {e}')
