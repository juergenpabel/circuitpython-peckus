from time import monotonic as time_monotonic

from . import AbstractCondition


class Condition(AbstractCondition):

    def __init__(self, timeout_method: str, timeout_criteria: str, app_data: dict):
        super().__init__('timeout', timeout_method, app_data)
        self.timeout_name = timeout_criteria


    def exists(self) -> bool:
        result = False
        if self.timeout_name in self.app_data['timeout']:
            if time_monotonic() <= self.app_data['timeout'][self.timeout_name]:
                result = True
        return result


    def expired(self) -> bool:
        result = False
        if self.timeout_name in self.app_data['timeout']:
            if time_monotonic() > self.app_data['timeout'][self.timeout_name]:
                result = True
        return result

