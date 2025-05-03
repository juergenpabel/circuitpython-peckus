from microcontroller import cpu as microcontroller_cpu

from . import AbstractCondition


class Condition(AbstractCondition):

    def __init__(self, system_method: str, system_params: str, app_data: dict):
        super().__init__('system', system_method, app_data)
        self.system_params = system_params


    def reset(self) -> bool:
        return str(microcontroller_cpu.reset_reason).split('.').pop().upper() == self.system_params.upper()

