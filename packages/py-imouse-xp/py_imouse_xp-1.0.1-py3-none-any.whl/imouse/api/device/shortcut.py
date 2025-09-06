from typing import TYPE_CHECKING, List

from ...models import AlbumFileResponse, PhoneFileResponse, ResultTextResponse, CommonResponse
from ...imouse_types import AlbumFileParams, PhoneFileParams

if TYPE_CHECKING:
    from . import Device


class Shortcut:
    def __init__(self, device: "Device"):
        self._device = device
        self._api = device._api
        self._device_id = device.id

    def album_get(self, album_name: str = "", num: int = 20, outtime: int = 15) -> AlbumFileResponse:
        """获取相册列表"""
        return self._api.call(AlbumFileResponse, self._api._payload.shortcut_album_get,
                             self._device_id, album_name, num, outtime * 1000, _timeout=outtime + 1)

    def album_upload(self, album_name: str, files: List[str], is_zip: bool = False, outtime: int = 30) -> AlbumFileResponse:
        """上传照片视频"""
        return self._api.call(AlbumFileResponse, self._api._payload.shortcut_album_upload,
                             self._device_id, album_name, files, is_zip, outtime * 1000, _timeout=outtime + 1)

    def album_down(self, files: List[AlbumFileParams], is_zip: bool = False, outtime: int = 30) -> CommonResponse:
        """下载照片视频"""
        return self._api.call(CommonResponse, self._api._payload.shortcut_album_down,
                             self._device_id, files, is_zip, outtime * 1000, _timeout=outtime + 1)

    def album_del(self, files: List[AlbumFileParams], outtime: int = 30) -> AlbumFileResponse:
        """删除照片视频"""
        return self._api.call(AlbumFileResponse, self._api._payload.shortcut_album_del,
                             self._device_id, files, outtime * 1000, _timeout=outtime + 1)

    def album_clear(self, album_name: str = '', outtime: int = 30) -> AlbumFileResponse:
        """清空照片视频"""
        return self._api.call(AlbumFileResponse, self._api._payload.shortcut_album_clear,
                             self._device_id, album_name, outtime * 1000, _timeout=outtime + 1)

    def file_get(self, path: str = "", outtime: int = 15) -> PhoneFileResponse:
        """获取文件列表"""
        return self._api.call(PhoneFileResponse, self._api._payload.shortcut_file_get,
                             self._device_id, path, outtime * 1000, _timeout=outtime + 1)

    def file_upload(self, path: str, files: List[str], is_zip: bool = False, outtime: int = 30) -> PhoneFileResponse:
        """上传文件"""
        return self._api.call(PhoneFileResponse, self._api._payload.shortcut_file_upload,
                             self._device_id, path, is_zip, files, outtime * 1000, _timeout=outtime + 1)

    def file_down(self, path: str, files: List[PhoneFileParams], is_zip: bool = False, outtime: int = 30) -> CommonResponse:
        """下载文件"""
        return self._api.call(CommonResponse, self._api._payload.shortcut_file_down,
                             self._device_id, path, is_zip, files, outtime * 1000, _timeout=outtime + 1)

    def file_del(self, path: str, files: List[PhoneFileParams], outtime: int = 30) -> PhoneFileResponse:
        """删除文件"""
        return self._api.call(PhoneFileResponse, self._api._payload.shortcut_file_del,
                             self._device_id, path, files, outtime * 1000, _timeout=outtime + 1)

    def clipboard_set(self, text: str, sleep: int = 0, outtime: int = 10) -> CommonResponse:
        """到手机剪切板"""
        return self._api.call(CommonResponse, self._api._payload.shortcut_clipboard_set,
                             self._device_id, text, sleep, outtime * 1000, _timeout=outtime + 1)

    def clipboard_get(self, outtime: int = 10) -> ResultTextResponse:
        """取手机剪切板"""
        return self._api.call(ResultTextResponse, self._api._payload.shortcut_clipboard_get,
                             self._device_id, outtime * 1000, _timeout=outtime + 1)

    def exec_url(self, url: str, outtime: int = 10) -> CommonResponse:
        """打开url"""
        return self._api.call(CommonResponse, self._api._payload.shortcut_exec_url,
                             self._device_id, url, outtime * 1000, _timeout=outtime + 1)

    def switch_device(self, state: int, outtime: int = 10) -> CommonResponse:
        """关闭重启设备"""
        return self._api.call(CommonResponse, self._api._payload.shortcut_switch_device,
                             self._device_id, state, outtime * 1000, _timeout=outtime + 1)

    def switch_bril(self, state: float, outtime: int = 10) -> CommonResponse:
        """亮度调节"""
        return self._api.call(CommonResponse, self._api._payload.shortcut_switch_bril,
                             self._device_id, state, outtime * 1000, _timeout=outtime + 1)

    def switch_torch(self, state: int, outtime: int = 10) -> CommonResponse:
        """开关手电筒"""
        return self._api.call(CommonResponse, self._api._payload.shortcut_switch_torch,
                             self._device_id, state, outtime * 1000, _timeout=outtime + 1)

    def switch_flight(self, state: int, outtime: int = 10) -> CommonResponse:
        """开关飞行模式"""
        return self._api.call(CommonResponse, self._api._payload.shortcut_switch_flight,
                             self._device_id, state, outtime * 1000, _timeout=outtime + 1)

    def switch_cdpd(self, state: int, outtime: int = 10) -> CommonResponse:
        """开关蜂窝数据"""
        return self._api.call(CommonResponse, self._api._payload.shortcut_switch_cdpd,
                             self._device_id, state, outtime * 1000, _timeout=outtime + 1)

    def switch_wlan(self, state: int, outtime: int = 10) -> CommonResponse:
        """开关无线局域网"""
        return self._api.call(CommonResponse, self._api._payload.shortcut_switch_wlan,
                             self._device_id, state, outtime * 1000, _timeout=outtime + 1)

    def device_ip(self, outtime: int = 10) -> ResultTextResponse:
        """获取外网ip"""
        return self._api.call(ResultTextResponse, self._api._payload.shortcut_device_ip,
                             self._device_id, 1, outtime * 1000, _timeout=outtime + 1)