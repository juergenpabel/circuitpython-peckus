from time import monotonic as time_monotonic

from . import AbstractAction


class Action(AbstractAction):

    def __init__(self, timeout_method: str, timeout_data: str, app_data: dict):
        super().__init__("timeouts", timeout_method, app_data)
        self.timeout_data = timeout_data
        if 'timeouts' not in self.app_data:
            self.app_data['timeouts'] = {}

    def remove(self) -> None:
        if self.timeout_data in self.app_data['timeouts']:
            del self.app_data['timeouts'][self.timeout_data]

    def minutes(self) -> None:
        timeout_name, timeout_value = self.timeout_data.split(':', 1)
        self.app_data['timeouts'][timeout_name] = time_monotonic() + (float(timeout_value) * 60)

    def seconds(self) -> None:
        timeout_name, timeout_value = self.timeout_data.split(':', 1)
        self.app_data['timeouts'][timeout_name] = time_monotonic() + float(timeout_value)

