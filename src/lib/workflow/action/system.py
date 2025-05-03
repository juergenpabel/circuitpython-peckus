from microcontroller import reset as microcontroller_reset
from supervisor import runtime as supervisor_runtime
from storage import umount as storage_umount
from os import sync as os_sync
from time import sleep as time_sleep

from . import AbstractAction


class Action(AbstractAction):

    def __init__(self, system_method: str, system_data: str, app_data: dict):
        super().__init__("system", system_method, app_data)
        self.system_data = system_data


    def reset(self) -> None:
        print("PECKUS: resetting system (SOFTWARE)")
        os_sync()
        storage_umount('/')
        microcontroller_reset()


    def delay(self) -> None:
        if isinstance(self.system_data, int) and self.system_data > 0:
            time_sleep(self.system_data)


    def console(self) -> None:
        if self.system_data.upper() == 'TRUE':
            while supervisor_runtime.serial_connected is False:
                time_sleep(0.1)

