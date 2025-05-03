from microcontroller import nvm as microcontroller_nvm

from . import AbstractAction


class Action(AbstractAction):

    def __init__(self, nvm_method: str, nvm_data: str, app_data: dict):
        super().__init__("nvm", nvm_method, app_data)
        self.nvm_data = nvm_data


    def erase(self) -> None:
        nvm_offset = 0
        nvm_length = 0
        if self.nvm_data is None:
            nvm_length = len(microcontroller_nvm)
        else:
            if self.nvm_data in self.app_data['nvm']:
                nvm_offset = self.app_data['nvm'][self.nvm_data]['offset']
                nvm_length = self.app_data['nvm'][self.nvm_data]['length']
        if nvm_length == 0:
            raise ValueError(f"Action<nvm>.erase('{self.nvm_data}') did not resolve to any known NVM area (known areas: {list(self.app_data['nvm'].keys())})")
        chunk_data = bytearray(1024)
        for chunk_offset in range(nvm_offset, nvm_offset+nvm_length, len(chunk_data)):
            microcontroller_nvm[chunk_offset:chunk_offset+len(chunk_data)] = chunk_data

