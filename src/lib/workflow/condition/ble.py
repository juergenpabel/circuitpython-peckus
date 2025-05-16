from _bleio import adapter as bleio_adapter
from time import sleep as time_sleep

from adafruit_ble import BLERadio as ble_BLERadio
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement as ble_ProvideServicesAdvertisement
from adafruit_ble.services.standard.hid import HIDService as ble_HIDService

from . import AbstractCondition


class Condition(AbstractCondition):

    def __init__(self, ble_method: str, ble_data: str, app_data: dict):
        super().__init__('ble', ble_method, app_data)
        self.ble_data = ble_data
        if 'radio' not in self.app_data['ble']:
            self.app_data['ble']['radio'] = ble_BLERadio(bleio_adapter)


    def paired(self) -> bool:
        result = False
        for connection in self.app_data['ble']['radio'].connections:
            result = True if connection.paired is True else result
        return str(result).upper() == self.ble_data.upper()


    def connected(self) -> bool:
        result = False
        for connection in self.app_data['ble']['radio'].connections:
            result = True if connection.connected is True else result
        return str(result).upper() == self.ble_data.upper()


    def scan_any_of(self) -> bool:
        result = False
        scan_secs, scan_macs = self.ble_data.split(':', 1)
        scan_secs = float(scan_secs)
        scan_macs = scan_macs.split(',')
        print(scan_macs)
        for device in self.app_data['ble']['radio'].start_scan(timeout=scan_secs):
            print(device) # TODO: implement
        self.app_data['ble']['radio'].stop_scan()
        return result

