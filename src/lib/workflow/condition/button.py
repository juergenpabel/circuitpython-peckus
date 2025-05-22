from microcontroller import cpu as microcontroller_cpu, \
                            ResetReason as microcontroller_ResetReason
from board import BUTTON as board_BUTTON
from digitalio import DigitalInOut as digitalio_DigitalInOut, \
                      Pull as digitalio_Pull

from peckus.workflow.condition import AbstractCondition


class Condition(AbstractCondition):

    BUTTON_PULL = {'UP': digitalio_Pull.UP, 'DOWN': digitalio_Pull.DOWN}

    def __init__(self, button_method: str, button_data: str, app_data: dict):
        super().__init__('button', button_method, app_data)
        self.button_data = button_data
        if ':' in button_data:
            self.button_value, self.button_pull = button_data.split(':', 1)
        else:
            self.button_value = button_data
            self.button_pull = 'UP'
        if self.button_pull.upper() not in Condition.BUTTON_PULL:
            raise ValueError(f"Condition<button>({button_data}): '{self.button_pull}' is an unknown pull target (only 'UP' and 'DOWN' are)")
        self.button_pull = Condition.BUTTON_PULL[self.button_pull.upper()]


    def reset(self) -> bool:
        return str(microcontroller_cpu.reset_reason == microcontroller_ResetReason.RESET_PIN).upper() == self.button_value.upper()


    def user(self) -> bool:
        result = None
        try:
            button = digitalio_DigitalInOut(board_BUTTON)
            button.pull = self.button_pull
            result = not(button.value)
            button.deinit()
        except Exception as e:
            print(f"Condition<button>({self.button_data}).user() caused exception: {e}")
            return False
        return str(result).upper() == self.button_value.upper()

