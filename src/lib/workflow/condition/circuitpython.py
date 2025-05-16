from microcontroller import cpu as microcontroller_cpu
from supervisor import runtime as supervisor_runtime

from . import AbstractCondition


class Condition(AbstractCondition):

    def __init__(self, circuitpython_method: str, circuitpython_data: str, app_data: dict):
        super().__init__('circuitpython', circuitpython_method, app_data)
        self.circuitpython_data = circuitpython_data


    def reset(self) -> bool:
        return str(microcontroller_cpu.reset_reason).split('.').pop().upper() == self.circuitpython_data.upper()


    def console(self) -> bool:
        return str(supervisor_runtime.serial_connected).upper() == self.circuitpython_data.upper()
