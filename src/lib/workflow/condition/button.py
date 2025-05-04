from microcontroller import cpu as microcontroller_cpu
from board import BUTTON as board_button
from digitalio import DigitalInOut as digitalio_DigitalInOut, \
                      Pull as digitalio_Pull

from . import AbstractCondition


class Condition(AbstractCondition):

    BUTTON_PULL = {'UP': digitalio_Pull.UP, 'DOWN': digitalio_Pull.DOWN}

    def __init__(self, button_method: str, button_params: str, app_data: dict):
        super().__init__('button', button_method, app_data)
        self.button_params = button_params
        if ':' in button_params:
            self.button_value, self.button_pull = button_params.split(':', 1)
        else:
            self.button_value = button_params
            self.button_pull = 'UP'
        if self.button_pull.upper() not in Condition.BUTTON_PULL:
            raise ValueError(f"Condition<button>({button_params}): '{self.button_pull}' is an unknown pull target (only 'UP' and 'DOWN' are)")
        self.button_pull = Condition.BUTTON_PULL[self.button_pull.upper()]


    def reset(self) -> bool:
        return str(microcontroller_cpu.reset_reason).split('.').pop().upper() == 'RESET_PIN'


    def user(self) -> bool:
        result = None
        try:
            button = digitalio_DigitalInOut(board_BUTTON)
            button.pull = self.button_pull
            result = button.value
            button.deinit()
        except Exception as e:
            print(f"Condition<button>({self.button_params}).user() caused exception: {e}")
            return False
        return str(result).upper() == self.button_value.upper()

