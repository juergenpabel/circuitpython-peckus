from time import monotonic as time_monotonic

from . import AbstractCondition


class Condition(AbstractCondition):

    def __init__(self, timeout_method: str, timeout_data: str, app_data: dict):
        super().__init__('timeout', timeout_method, app_data)
        self.timeout_data = timeout_data


    def unknown(self) -> bool:
        return not(self.timeout_data in self.app_data['timeout'])


    def exists(self) -> bool:
        result = False
        if self.timeout_data in self.app_data['timeout']:
            if time_monotonic() <= self.app_data['timeout'][self.timeout_data]:
                result = True
        return result


    def expired(self) -> bool:
        result = False
        if self.timeout_data in self.app_data['timeout']:
            if time_monotonic() > self.app_data['timeout'][self.timeout_data]:
                result = True
        return result

