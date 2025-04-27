from microcontroller import reset as microcontroller_reset
from storage import umount as storage_umount
from os import sync as os_sync
from time import sleep as time_sleep

from . import AbstractAction


class Action(AbstractAction):

    def __init__(self, system_method: str, system_data: str, app_data: dict):
        super().__init__("system", system_method, app_data)
        self.system_data = system_data


    def reset(self) -> None:
        os_sync()
        storage_umount('/')
        microcontroller_reset()


    def delay(self) -> None:
        try:
            if len(self.system_data) > 0:
                time_sleep(float(self.system_data))
        except ValueError as e:
            print(f"Action<system>.delay('{self.peckus_params}'): {e})")

