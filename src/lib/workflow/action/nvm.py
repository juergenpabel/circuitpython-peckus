from microcontroller import nvm as microcontroller_nvm

from . import AbstractAction


class Action(AbstractAction):

    def __init__(self, nvm_method: str, nvm_data: str, app_data: dict):
        super().__init__('nvm', nvm_method, app_data)
        self.nvm_data = nvm_data


    def erase(self) -> None:
        nvm_offset = 0
        nvm_length = len(microcontroller_nvm)
        if self.nvm_data is not None:
            if 'nvm' in self.app_data:
                if self.nvm_data in self.app_data['nvm']:
                    nvm_offset = self.app_data['nvm'][self.nvm_data]['offset']
                    nvm_length = self.app_data['nvm'][self.nvm_data]['length']
                else:
                    raise ValueError(f"Action<nvm>.erase('{self.nvm_data}') did not resolve to any known NVM area (known areas: {list(self.app_data['nvm'].keys())})")
        chunk_data = bytearray(b'\xc0') * 1024
        for chunk_offset in range(nvm_offset, nvm_offset+nvm_length, len(chunk_data)):
            microcontroller_nvm[chunk_offset:chunk_offset+len(chunk_data)] = chunk_data

