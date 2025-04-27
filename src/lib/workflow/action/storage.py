from storage import getmount as storage_getmount, \
                    mount as storage_mount, \
                    remount as storage_remount, \
                    umount as storage_umount
from os import stat as os_stat, \
               sync as os_sync, \
               remove as os_remove

from . import AbstractAction


class Action(AbstractAction):

    RW_OPTIONS = {'READONLY': True, 'READWRITE': False}

    def __init__(self, storage_method: str, storage_data: str, app_data: dict):
        super().__init__("storage", storage_method, app_data)
        self.storage_data = storage_data


    def mount(self) -> None:
        rw_option = self.storage_data.upper()
        if 'rootfs' not in self.app_data['storage']:
            raise ValueError(f"Action<storage>.mount({rw_option}) not possible (not previously unmounted)")
        if rw_option not in Action.RW_OPTIONS.keys():
            raise ValueError(f"Action<storage>.mount({rw_option}) not valid (only {list(Action.RW_OPTIONS.keys())})")
        storage_mount(self.app_data['storage']['rootfs'], '/', readonly=Action.RW_OPTIONS[rw_option])


    def remount(self) -> None:
        rw_option = self.storage_data.upper()
        if rw_option not in Action.RW_OPTIONS.keys():
            raise ValueError(f"Action<storage>.remount({rw_option}) not valid (only {list(Action.RW_OPTIONS.keys())})")
        storage_remount('/', readonly=Action.RW_OPTIONS[rw_option])


    def umount(self) -> None:
        self.app_data['storage']['rootfs'] = storage_getmount('/')
        storage_umount('/')


    def wipe(self) -> None:
        if storage_getmount('/').readonly is True:
            raise RuntimeError(f"Action<storage>.wipe('{self.storge_data}') not valid read-only mounted filesystem")
        try:
            stat = os_stat(self.storage_data)
            if stat is not None:
                with open(self.storage_data, 'rb+') as f:
                    zeros = bytearray(512)
                    for i in range(0, stat[6], len(zeros)):
                        f.write(zeros)
                    f.write(zeros)
                os_remove(self.storage_data)
                os_sync()
        except Exception as e:
            pass

