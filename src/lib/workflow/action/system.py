from microcontroller import reset as microcontroller_reset
from supervisor import runtime as supervisor_runtime, \
                       reload as supervisor_reload
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


    def reload(self) -> None:
        print("PECKUS: reloading application")
        supervisor_reload()


    def delay(self) -> None:
        try:
            time_sleep(int(self.system_data))
        except ValueError:
            pass


    def console(self) -> None:
        if self.system_data.upper() == 'TRUE':
            while supervisor_runtime.serial_connected is False:
                time_sleep(0.1)

