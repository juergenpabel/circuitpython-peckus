from time import monotonic as time_monotonic

from . import AbstractAction


class Action(AbstractAction):

    def __init__(self, timeout_method: str, timeout_data: str, app_data: dict):
        super().__init__("timeout", timeout_method, app_data)
        self.timeout_data = timeout_data


    def remove(self) -> None:
        if self.timeout_data in self.app_data['timeout']:
            del self.app_data['timeout'][self.timeout_data]


    def minutes(self) -> None:
        timeout_name, timeout_value = self.timeout_data.split(':', 1)
        if float(timeout_value) > 0:
            self.app_data['timeout'][timeout_name] = time_monotonic() + (float(timeout_value) * 60)


    def seconds(self) -> None:
        timeout_name, timeout_value = self.timeout_data.split(':', 1)
        if float(timeout_value) > 0:
            self.app_data['timeout'][timeout_name] = time_monotonic() + float(timeout_value)

