from _bleio import adapter as bleio_adapter
from time import sleep as time_sleep
from traceback import print_exception as traceback_print_exception

from adafruit_ble import BLERadio as ble_BLERadio
from adafruit_ble.advertising.standard import Advertisement as ble_Advertisement, \
                                              ProvideServicesAdvertisement as ble_ProvideServicesAdvertisement
from adafruit_ble.services.standard.hid import HIDService as ble_HIDService

from . import AbstractAction


class Action(AbstractAction):

    def __init__(self, ble_method: str, ble_data: str, app_data: dict):
        super().__init__('ble', ble_method, app_data)
        self.ble_data = ble_data
        if 'radio' not in self.app_data['ble']:
            self.app_data['ble']['radio'] = ble_BLERadio(bleio_adapter)


    def name(self) -> None:
        self.app_data['ble']['radio'].name = self.ble_data


    def enable(self) -> None:
        bleio_adapter.enabled = True


    def disable(self) -> None:
        bleio_adapter.enabled = False


    def advertise(self) -> None:
        if self.ble_data.upper() == str(True).upper():
            advertisement = ble_ProvideServicesAdvertisement(ble_HIDService())
            advertisement.appearance = 960
            advertisement.connectable = True
            self.app_data['ble']['radio'].start_advertising(advertisement)
        else:
            self.app_data['ble']['radio'].stop_advertising()


    def unpair(self) -> None:
        bleio_adapter.erase_bonding()

