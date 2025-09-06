from typing import TYPE_CHECKING, List, Union
from ...imouse_types import FunctionKeys
from ...models import CommonResponse

if TYPE_CHECKING:
    from . import Device


class KeyBoard:
    def __init__(self, device: "Device"):
        self._device = device
        self._api = device._api
        self._device_id = device.id

    def send_keys(self, keys: str) -> CommonResponse:
        """发送字符键"""
        return self._api.call(CommonResponse, self._api._payload.key_sendkey,
                             self._device_id, keys, "")

    def send_fn_key(self, fn_key: Union[FunctionKeys, str]) -> CommonResponse:
        """发送功能键"""
        key_value = fn_key.value if hasattr(fn_key, 'value') else fn_key
        return self._api.call(CommonResponse, self._api._payload.key_sendkey,
                             self._device_id, "", key_value)

    def send_hid_key(self, keys: Union[str, List[str]], delay: int = 20) -> CommonResponse:
        """发送HID按键序列（自动处理修饰键）"""
        if isinstance(keys, str):
            # 检测所有修饰键
            standard_modifiers = ["ctrl", "shift", "alt", "win", "fn"]
            detected_modifiers = []
            
            # 找到所有标准修饰键
            for modifier in standard_modifiers:
                if modifier + "+" in keys:
                    detected_modifiers.append(modifier)
            
            # 特殊处理 tab 键
            tab_detected = "tab+" in keys
            if tab_detected:
                # 如果 tab 与其他修饰键组合，tab 作为普通键
                # 如果 tab 只与普通键组合，tab 作为修饰键
                if detected_modifiers:
                    # tab 与其他修饰键组合，tab 作为普通键，不加入修饰键列表
                    pass
                else:
                    # tab 只与普通键组合，tab 作为修饰键
                    detected_modifiers.append("tab")
            
            # 构建按键序列
            if detected_modifiers:
                # 先按住所有修饰键，然后按组合键
                keys = detected_modifiers + [keys]
            else:
                keys = [keys]
        
        actions = []
        for i, key in enumerate(keys):
            actions.append({
                "delayed": 0 if i == 0 else delay,
                "key": key
            })
        
        # Add final action to lift all keys
        actions.append({
            "delayed": delay,
            "key": ""
        })
        
        return self._api.call(CommonResponse, self._api._payload.key_sendhidkey,
                             self._device_id, actions)

