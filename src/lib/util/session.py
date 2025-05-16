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


    def set(self, key: str, value_new: Any, validity: int=None) -> None:
        value_old = self.data[key] if key in self.data else None
        if value_old != value_new:
            if value_new is not None:
                self.data[key] = {'value': value_new, 'validity': (time_monotonic() + validity) if validity is not None else None}
            else:
                del self.data[key]
            self.save()


    def get(self, key: str, validity_delta: int=0) -> Any:
        if key in self.data:
            if self.data[key]['validity'] is not None:
                if time_monotonic() > self.data[key]['validity']:
                    self.set(key, None)
                    return None
                if (time_monotonic() + validity_delta) > self.data[key]['validity']:
                    return None
            return self.data[key]['value']
        return None

