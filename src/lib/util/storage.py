from microcontroller import nvm as microcontroller_nvm

from peckus.util.datastream import DataStream


class Storage(object):

    def __init__(self, nvm_offset, nvm_length):
        super().__init__()
        self.nvm_offset = nvm_offset
        self.nvm_length = nvm_length
        self.load()


    def load(self) -> bool:
        self.data = DataStream('sleep_memory').load(microcontroller_nvm, self.nvm_offset, self.nvm_length)
        if isinstance(self.data, dict) is False:
            self.data = {}
            self.save()
            return False
        return True


    def save(self) -> bool:
        return DataStream('sleep_memory').save(self.data, microcontroller_nvm, self.nvm_offset, self.nvm_length)


    def clear(self) -> bool:
        self.data = {}
        return self.save()


    def set(self, key: str, value_new: Any) -> None:
        value_old = self.data[key] if key in self.data else None
        if value_old != value_new:
            if value_new is not None:
                self.data[key] = value_new
            else:
                del self.data[key]
            self.save()


    def get(self, key: str) -> Any:
        if key in self.data:
            return self.data[key]
        return None

