from _bleio import adapter as bleio_adapter
from usb_cdc import disable as usb_cdc_disable, \
                    enable as usb_cdc_enable
from storage import disable_usb_drive as storage_disable_usb_drive, \
                    enable_usb_drive as storage_enable_usb_drive, \
                    umount as storage_umount
from time import sleep as time_sleep
from microcontroller import reset as microcontroller_reset
from supervisor import runtime as supervisor_runtime, \
                       reload as supervisor_reload

from . import AbstractAction


class Action(AbstractAction):

    def __init__(self, circuitpython_method: str, circuitpython_data: str, app_data: dict):
        super().__init__('circuitpython', circuitpython_method, app_data)
        self.circuitpython_data = circuitpython_data


    def usb_storage(self) -> None:
        if self.circuitpython_data.upper() == 'TRUE':
            storage_enable_usb_drive()
            print(f"PECKUS: enabled USB storage")
        else:
            storage_disable_usb_drive()
            print(f"PECKUS: disabled USB storage")


    def usb_serial(self) -> None:
        if self.circuitpython_data.upper() == 'TRUE':
            usb_cdc_enable()
            print(f"PECKUS: enabled USB console")
        else:
            usb_cdc_disable()
            print(f"PECKUS: disabled USB console")


    def ble_network(self) -> None:
        if self.circuitpython_data.upper() == 'TRUE':
            supervisor_runtime.ble_workflow = True
            print(f"PECKUS: enabled BLE network")
        else:
            supervisor_runtime.ble_workflow = False
            print(f"PECKUS: disabled BLE network")


    def delay(self) -> None:
        time_sleep(float(self.circuitpython_data))


    def reload(self) -> None:
        supervisor_reload()


    def reset(self) -> None:
        try:
            storage_umount('/')
        except Exception as e:
            pass
        microcontroller_reset()

