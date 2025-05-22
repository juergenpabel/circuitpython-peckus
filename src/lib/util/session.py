from alarm import sleep_memory as alarm_sleep_memory
from time import monotonic as time_monotonic

from peckus.util.datastream import DataStream


class Session(object):

    def __init__(self, sm_offset: int = 0, sm_length: int = len(alarm_sleep_memory)):
        super().__init__()
        self.sm_offset = sm_offset
        self.sm_length = sm_length
        self.load()


    def load(self) -> bool:
        self.data = DataStream('sleep_memory').load(alarm_sleep_memory, self.sm_offset, self.sm_length)
        if isinstance(self.data, dict) is False:
            self.data = {}
            self.save()
            return False
        return True


    def save(self) -> bool:
        return DataStream('sleep_memory').save(self.data, alarm_sleep_memory, self.sm_offset, self.sm_length)


    def clear(self) -> bool:
        self.data = {}
        return self.save()


    def set(self, key: str, value_new: Any, validity_new: int=0) -> None:
        value_old = self.data[key]['value'] if key in self.data else None
        validity_old = self.data[key]['validity'] if key in self.data else 0
        validity_new = (time_monotonic() + validity_new) if validity_new != 0 else 0
        if value_new != value_old or int(validity_old) != int(validity_new):
            if value_new is not None:
                self.data[key] = {'value': value_new, 'validity': validity_new}
            else:
                del self.data[key]
            self.save()


    def get(self, key: str, default: Any=None, validity_delta: int=0) -> Any:
        if key in self.data:
            if self.data[key]['validity'] != 0:
                if (time_monotonic() + validity_delta) > self.data[key]['validity']:
                    if validity_delta == 0:
                        self.set(key, default, 0)
                    return default
            return self.data[key]['value']
        return default

