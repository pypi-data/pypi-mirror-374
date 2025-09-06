from typing import TYPE_CHECKING

from ...models import ImServerConfigData, ImServerConfigResponse, CommonResponse

if TYPE_CHECKING:
    from .. import API

from .device import Device
from .group import Group
from .airplay import AirPlay
from .usb import Usb
from .config import Config
from .user import User


class Console:
    def __init__(self, api: "API"):
        self._api = api
        self._imserver_config = self.get_imserver_config

    def restart_core(self) -> bool:
        ret = self._api.call(CommonResponse, self._api._payload.imserver_restart)
        return ret.status == 200 and ret.data.code == 0

    @property
    def get_imserver_config(self) -> ImServerConfigData:
        ret = self._api.call(ImServerConfigResponse, self._api._payload.config_imserver_get)
        if ret.status == 200 and ret.data.code == 0:
            self._imserver_config = ret.data
        else:
            self._imserver_config = None
        return self._imserver_config

    @property
    def device(self):
        return Device(self._api)

    @property
    def group(self):
        return Group(self._api)

    @property
    def airplay(self):
        return AirPlay(self._api)

    @property
    def usb(self):
        return Usb(self._api)

    @property
    def user(self):
        return User(self._api)

    @property
    def im_config(self):
        return Config(self._api)

