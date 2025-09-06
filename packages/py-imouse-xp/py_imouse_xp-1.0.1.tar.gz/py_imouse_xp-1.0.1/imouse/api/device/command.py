from typing import TYPE_CHECKING
from ...models import CommonResponse

if TYPE_CHECKING:
    from . import Device


class Command:
    def __init__(self, device: "Device"):
        self._device = device
        self._api = device._api
        self._device_id = device.id

    # basic commands
    def help(self):
        self._device.keyboard.send_fn_key("tab+h")

    # movement commands
    def move_forward(self):
        self._device.keyboard.send_fn_key("tab")

    def move_backward(self):
        self._device.keyboard.send_hid_key("shift+tab")

    def move_up(self):
        self._device.keyboard.send_fn_key("uparrow")

    def move_down(self):
        self._device.keyboard.send_fn_key("downarrow")

    def move_left(self):
        self._device.keyboard.send_fn_key("leftarrow")

    def move_right(self):
        self._device.keyboard.send_fn_key("rightarrow")

    def move_to_beginning(self):
        self._device.keyboard.send_fn_key("tab+leftarrow")

    def move_to_end(self):
        self._device.keyboard.send_fn_key("tab+rightarrow")

    def move_to_next_item(self):
        self._device.keyboard.send_hid_key("ctrl+tab")

    def move_to_previous_item(self):
        self._device.keyboard.send_hid_key("ctrl+shift+tab")

    def find(self):
        self._device.keyboard.send_fn_key("tab+f")

    # interaction commands
    def activate(self):
        self._device.keyboard.send_fn_key(" ")

    def go_back(self):
        self._device.keyboard.send_hid_key("tab+b")

    def contextual_menu(self):
        self._device.keyboard.send_hid_key("tab+m")

    def actions(self):
        self._device.keyboard.send_hid_key("tab+z")

    # device commands
    def home(self):
        self._device.keyboard.send_hid_key("win+h")

    def app_switcher(self):
        self._device.keyboard.send_fn_key("AppSwitch")

    def control_center(self):
        self._device.keyboard.send_fn_key("ControlBar")

    def notification_center(self):
        self._device.keyboard.send_fn_key("NoticeBar")

    def lock_screen(self):
        self._device.keyboard.send_hid_key("tab+l")

    def restart(self):
        self._device.keyboard.send_hid_key("ctrl+alt+shift+win+r")

    def siri(self):
        self._device.keyboard.send_hid_key("fn+s")

    def accessibility_shortcut(self):
        self._device.keyboard.send_hid_key("tab+x")

    def sos(self):
        self._device.keyboard.send_hid_key("ctrl+alt+shift+win+s")

    def rotate_device(self):
        self._device.keyboard.send_hid_key("tab+r")

    def analytics(self):
        self._device.keyboard.send_hid_key("ctrl+alt+shift+win+.")

    def pass_through_mode(self):
        self._device.keyboard.send_hid_key("ctrl+alt+win+p")

    # gestures commands
    def keyboard_gestures(self):
        self._device.keyboard.send_hid_key("tab+g")

    # custom commands
    def spotlight(self):
        self._device.keyboard.send_fn_key("win+ ")