from typing import TYPE_CHECKING, List

from ...models import FindImageResultResponse, FindImageCvResultResponse, OcrResultResponse, \
    FindMultiColorResponse
from ...imouse_types import MultiColorParams

if TYPE_CHECKING:
    from . import Device


class Image:
    def __init__(self, device: "Device"):
        self._device = device
        self._api = device._api
        self._device_id = device.id

    def screenshot(self, rect: List[int] = None) -> bytes:
        """截取设备屏幕"""
        return self._api.call(bytes, self._api._payload.pic_screenshot, 
                             self._device_id, False, rect)

    def find_image(self, img_list: List[str], similarity: float = 0.85, all: bool = False,
                   rect: List[int] = None,
                   delta_color: str = "", direction: str = "") -> FindImageResultResponse:
        """普通找图"""
        return self._api.call(FindImageResultResponse, self._api._payload.pic_find_image,
                             self._device_id, img_list, similarity, all, rect, delta_color, direction)

    def find_image_cv(self, img_list: List[str], similarity: float = 0.85, all: bool = False,
                      same: bool = False,
                      rect: List[int] = None) -> FindImageCvResultResponse:
        """OpenCV找图"""
        return self._api.call(FindImageCvResultResponse, self._api._payload.pic_find_image_cv,
                             self._device_id, img_list, similarity, all, same, rect)

    def ocr(self, rect: List[int] = None, is_ex: bool = False) -> OcrResultResponse:
        """OCR文字识别"""
        return self._api.call(OcrResultResponse, self._api._payload.pic_ocr,
                             self._device_id, rect, is_ex)

    def find_text(self, text_list: List[str], similarity: float, contain: bool = False,
                  rect: List[int] = None,
                  is_ex: bool = False) -> OcrResultResponse:
        """查找文字"""
        return self._api.call(OcrResultResponse, self._api._payload.pic_find_text,
                             self._device_id, text_list, similarity, contain, rect, is_ex)

    def find_multi_color(self, params: List[MultiColorParams], all: bool = False,
                         same: bool = False) -> FindMultiColorResponse:
        """多点找色"""
        return self._api.call(FindMultiColorResponse, self._api._payload.pic_find_multi_color,
                             self._device_id, params, all, same)
