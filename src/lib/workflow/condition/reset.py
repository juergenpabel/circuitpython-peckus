from microcontroller import cpu as microcontroller_cpu

from . import AbstractCondition


class Condition(AbstractCondition):

    def __init__(self, reset_method: str, reset_criteria: str, app_data: dict):
        super().__init__("reset", reset_method, app_data)
        self.reset_criteria = reset_criteria.upper()

    def reason(self) -> bool:
        return str(microcontroller_cpu.reset_reason).split('.').pop().upper() == self.reset_criteria

