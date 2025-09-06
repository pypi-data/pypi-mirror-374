import json
from abc import ABC
from typing import Union, Type, Optional

from ..utils.utils import parse_model
from ..models import CommonResponse
from .client import Client
from .payload import Payload


class BaseAPI(ABC):
    """API操作基类，直接返回Pydantic模型"""
    
    def __init__(self):
        self._client: Optional[Client] = None
        self._payload: Optional[Payload] = None
    
    def _make_request(self, payload_data: dict, timeout: int = 0, is_async: bool = False) -> Union[str, bytes, None]:
        """
        使用给定载荷发起网络请求
        
        Args:
            payload_data: 要发送的载荷字典
            timeout: 请求超时时间（秒）
            is_async: 是否异步请求
            
        Returns:
            响应数据：字符串、字节或None
        """
        if not self._client:
            raise RuntimeError("客户端未初始化")
            
        return self._client._network_request(
            json.dumps(payload_data), 
            timeout, 
            is_async
        )
    
    def call(self, model_class: Type, payload_method, *args, **kwargs):
        """
        通用API调用方法，直接返回Pydantic模型
        
        Args:
            model_class: 用于解析响应的Pydantic模型类
            payload_method: 要调用的载荷方法
            *args, **kwargs: 载荷方法的参数
            
        Returns:
            解析后的Pydantic模型实例，错误时抛出异常
        """
        # 从kwargs中提取timeout和is_async参数
        timeout = kwargs.pop('_timeout', 0)
        is_async = kwargs.pop('_is_async', False)
        
        try:
            # 构建载荷
            payload_data = payload_method(*args, **kwargs)
            
            # 发起请求
            response = self._make_request(payload_data, timeout, is_async)
            
            if response is None:
                raise RuntimeError("网络请求失败")
            
            # 直接处理截图等方法的字节响应
            if isinstance(response, bytes):
                print(f"[调试] 成功 - 二进制响应长度: {len(response)} 字节")
                return response
                
            # 使用指定模型解析JSON响应
            response_dict = json.loads(response) if isinstance(response, str) else response
            print(f"[调试] JSON响应: {response_dict}")
            
            # 特殊情况：如果期望字节但收到JSON，检查错误
            if model_class == bytes:
                # 期望字节但收到JSON - 解析为CommonResponse检查错误
                error_response = parse_model(CommonResponse, response_dict)
                # 检查是否为错误：code != 0 表示错误
                if error_response.data and error_response.data.code != 0:
                    raise RuntimeError(error_response.data.message)
                else:
                    raise RuntimeError("期望二进制数据但收到JSON响应")
            
            parsed_response = parse_model(model_class, response_dict)
            return parsed_response
                
        except (json.JSONDecodeError, ValueError) as e:
            raise RuntimeError(f"响应解析错误: {e}")
        except RuntimeError:
            # 重新抛出RuntimeError（包含我们的有意义错误消息）
            raise
        except Exception as e:
            raise RuntimeError(f"请求异常: {e}")

