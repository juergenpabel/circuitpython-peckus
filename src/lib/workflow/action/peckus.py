from microcontroller import nvm as microcontroller_nvm
from storage import getmount as storage_getmount, \
                    mount as storage_mount, \
                    remount as storage_remount, \
                    umount as storage_umount
from io import BytesIO as io_BytesIO
from os import getenv as os_getenv, \
               stat as os_stat, \
               sync as os_sync, \
               remove as os_remove
from time import sleep as time_sleep
from msgpack import unpack as msgpack_unpack, \
                    pack as msgpack_pack
from traceback import print_exception as traceback_print_exception


from peckus.application import StatusPayload
from . import AbstractAction


class ActionCommand():
    INSTALL = 'INSTALL'
    LOCK    = 'LOCK'
    UNLOCK  = 'UNLOCK'


class Action(AbstractAction):

    def __init__(self, peckus_method: str, peckus_params: str, app_data: dict):
        super().__init__("peckus", peckus_method, app_data)
        self.peckus_params = peckus_params


    def install(self) -> None:
        if self.app_data['status']['payload'] != StatusPayload.UNINITIALIZED:
            raise ValueError(f"Action<peckus>.install('{self.peckus_params}') not valid with payload status" \
                              "'{str(self.app_data['status']['payload'])}' (only valid in '{StatusPayload.UNINITIALIZED}')")
        try:
            stat = None
            try:
                stat = os_stat(self.peckus_params)
            except OSError as e:
                print(f"Action<peckus>.install('{self.peckus_params}'): file not found")
            if stat is not None:
                nvm_offset_payload = self.app_data['nvm']['payload']['offset']
                nvm_length_payload = self.app_data['nvm']['payload']['length']
                if stat[6] >= nvm_length_payload-2:
                    raise MemoryError(f"Action<peckus>.install('{self.peckus_params}') is too big for NVM payload " \
                                       "({stat[6]} bytes, but NVM payload is only {nvm_length_payload-2} bytes; 2 additional bytes are for metadata)")
                payload = io_BytesIO()
                with open(self.peckus_params, 'rb') as f:
                    msgpack_pack(f.read(), payload)
                    payload = payload.getvalue()
                microcontroller_nvm[nvm_offset_payload:nvm_offset_payload+len(payload)] = payload
                self.app_data['status']['payload'] = StatusPayload.INSTALLED
                print(f"installed payload from '{self.peckus_params}' to NVM ({len(payload)-2} bytes)")
        except Exception as e:
            if isinstance(e, MemoryError) is True:
                raise e
            print(f"Action<peckus>.install('{self.peckus_params}'): {e})")
            traceback_print_exception(e)


    def unlock(self) -> None:
        if self.app_data['status']['payload'] != StatusPayload.INSTALLED:
            raise ValueError(f"Action<peckus>.unlock('{self.peckus_params}') not valid with payload status " \
                              "'{str(self.app_data['status']['payload'])}' (only valid in '{StatusPayload.INSTALLED}')")
        try:
            nvm_offset_payload = self.app_data['nvm']['payload']['offset']
            nvm_length_payload = self.app_data['nvm']['payload']['length']
            payload = msgpack_unpack(io_BytesIO(microcontroller_nvm[nvm_offset_payload:nvm_offset_payload+nvm_length_payload]))
            with open(self.peckus_params, 'wb') as f:
                f.write(payload)
            os_sync()
            self.app_data['peckus']['rootfs'] = storage_getmount('/')
            storage_umount('/')
            time_sleep(1.5) #TODO: make configurable via settings.toml (getenv before umount)
            storage_mount(self.app_data['peckus']['rootfs'], '/', readonly=False)
            self.app_data['status']['payload'] = StatusPayload.UNLOCKED
        except Exception as e:
            print(f"Action<peckus>.unlock('{self.peckus_params}'): {e})")
            traceback_print_exception(e)

