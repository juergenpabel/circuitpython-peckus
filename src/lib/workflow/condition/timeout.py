from time import monotonic as time_monotonic

from . import AbstractCondition


class Condition(AbstractCondition):

    def __init__(self, timeout_method: str, timeout_criteria: str, app_data: dict):
        super().__init__("timeout", timeout_method, app_data)
        self.timeout_name = timeout_criteria

    def exists(self) -> bool:
        result = False
        if 'timeouts' in self.app_data:
            if self.timeout_name in self.app_data['timeouts']:
                result = True
        return result

    def expired(self) -> bool:
        result = False
        if 'timeouts' in self.app_data:
            if self.timeout_name in self.app_data['timeouts']:
                if time_monotonic() > self.app_data['timeouts'][self.timeout_name]:
#TODO:too early     del self.app_data['timeouts'][self.timeout_name]
                    result = True
        return result

