from storage import getmount as storage_getmount, \
                    mount as storage_mount, \
                    remount as storage_remount, \
                    umount as storage_umount
from os import stat as os_stat, \
               sync as os_sync, \
               remove as os_remove, \
               rename as os_rename
from time import sleep as time_sleep

from . import AbstractAction


class Action(AbstractAction):

    RW_OPTIONS = {'READONLY': True, 'READWRITE': False}

    def __init__(self, filesystem_method: str, filesystem_data: str, app_data: dict):
        super().__init__("filesystem", filesystem_method, app_data)
        self.filesystem_data = filesystem_data


    def mount(self) -> None:
        rw_option = self.filesystem_data.upper()
        if 'vfs' not in self.app_data['filesystem']:
            raise ValueError(f"Action<filesystem>.mount({rw_option}) not possible (not previously unmounted)")
        if rw_option not in Action.RW_OPTIONS.keys():
            raise ValueError(f"Action<filesystem>.mount({rw_option}) not valid (only {list(Action.RW_OPTIONS.keys())})")
        storage_mount(self.app_data['filesystem']['vfs'], '/', readonly=Action.RW_OPTIONS[rw_option])


    def remount(self) -> None:
        rw_option = self.filesystem_data.upper()
        if rw_option not in Action.RW_OPTIONS.keys():
            raise ValueError(f"Action<filesystem>.remount({rw_option}) not valid (only {list(Action.RW_OPTIONS.keys())})")
        storage_remount('/', readonly=Action.RW_OPTIONS[rw_option])


    def umount(self) -> None:
        self.app_data['filesystem']['vfs'] = storage_getmount('/')
        storage_umount('/')


    def file_move(self) -> None:
        if storage_getmount('/').readonly is True:
            raise RuntimeError(f"Action<filesystem>.file_move('{self.filesystem_data}') not possible on read-only mounted filesystem")
        file_src, file_dst = self.filesystem_data.split(':', 1)
        try:
            os_remove(file_dst)
        except Exception as e:
            pass
        try:
            os_rename(file_src, file_dst)
        except Exception as e:
            print(e)
        os_sync()


    def file_shred(self) -> None:
        if storage_getmount('/').readonly is True:
            raise RuntimeError(f"Action<filesystem>.shred('{self.storge_data}') not valid read-only mounted filesystem")
        try:
            stat = os_stat(self.filesystem_data)
            if stat is not None:
                with open(self.filesystem_data, 'rb+') as f:
                    zeros = bytearray(512)
                    for i in range(0, stat[6], len(zeros)):
                        f.write(zeros)
                    f.write(zeros)
                os_remove(self.filesystem_data)
        except Exception as e:
            pass
        os_sync()

