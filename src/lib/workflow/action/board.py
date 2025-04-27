from board import LED_RED as board_LED_RED, \
                  LED_GREEN as board_LED_GREEN, \
                  LED_BLUE as board_LED_BLUE
from digitalio import DigitalInOut as digitalio_DigitalInOut, \
                      Direction as digitalio_Direction

from . import AbstractAction


class Action(AbstractAction):

    LED_NAMES  = {'RED': board_LED_RED, 'GREEN': board_LED_GREEN, 'BLUE': board_LED_BLUE}
    LED_STATES = {'OFF': True, 'ON': False}

    def __init__(self, action_method: str, action_data: str, app_data: dict):
        super().__init__("board", action_method, app_data)
        self.action_data = action_data
        if 'board' not in self.app_data:
            self.app_data['board'] = {}
        if 'led' not in self.app_data['board']:
            self.app_data['board']['led'] = Action.LED_NAMES
            for color, pin in self.app_data['board']['led'].copy().items():
                self.app_data['board']['led'][color] = digitalio_DigitalInOut(pin)
                self.app_data['board']['led'][color].direction = digitalio_Direction.OUTPUT
                self.app_data['board']['led'][color].value = Action.LED_STATES['OFF']

    def led(self) -> None:
        led, state = self.action_data.upper().split(':', 1)
        if led not in self.app_data['board']['led']:
            raise ValueError(f"Action<board>.led('{self.action_data}') refers to no known LED on this board")
        if state not in Action.LED_STATES.keys():
            raise ValueError(f"Action<board>.led('{self.action_data}') refers to no known LED state")
        self.app_data['board']['led'][led].value = Action.LED_STATES[state]

