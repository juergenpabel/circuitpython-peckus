from board import LED_RED as board_LED_RED, \
                  LED_GREEN as board_LED_GREEN, \
                  LED_BLUE as board_LED_BLUE
from digitalio import DigitalInOut as digitalio_DigitalInOut, \
                      Direction as digitalio_Direction
from time import monotonic as time_monotonic

from . import AbstractJob


class LED():
    RED   = 'RED'
    GREEN = 'GREEN'
    BLUE  = 'BLUE'


class Job(AbstractJob):

    LED_NAMES  = {LED.RED: board_LED_RED, LED.GREEN: board_LED_GREEN, LED.BLUE: board_LED_BLUE}
    LED_STATES = {'OFF': True, 'ON': False}

    def __init__(self, name: str, configuration: dict, scope: str):
        super().__init__('led', name, scope)
        self.states = []
        if 'states' not in configuration or len(configuration['states']) == 0:
            raise ValueError(f"missing 'states' definition in job '{name}'")
        for conf in configuration['states']:
            state = {}
            for color in Job.LED_NAMES.keys():
                state[color] = Job.LED_STATES[conf[color]] if color in conf and conf[color] in Job.LED_STATES else Job.LED_STATES['OFF']
            state['millis'] = conf['millis'] if 'millis' in conf else None
            self.states.append(state)
        self.current_state = None
        self.current_timeout = None


    def begin(self) -> None:
        self.leds = {}
        for color, pin in Job.LED_NAMES.items():
            try:
                led = digitalio_DigitalInOut(pin)
                led.direction = digitalio_Direction.OUTPUT
                led.value = Job.LED_STATES['OFF']
                self.leds[color] = led
            except Exception as e:
                self.leds[color] = None
        self.current_state = -1
        self.current_timeout = -1
        self.update()


    def update(self) -> None:
        if self.current_state is not None and self.current_timeout is not None:
            if time_monotonic() >= self.current_timeout:
                self.current_state += 1
                self.current_state %= len(self.states)
                for color in Job.LED_NAMES.keys():
                    if self.leds[color] is not None:
                        self.leds[color].value = self.states[self.current_state][color]
                if self.states[self.current_state]['millis'] not in [None, 0]:
                    self.current_timeout = time_monotonic() + (self.states[self.current_state]['millis'] / 1000)
                else:
                    self.current_timeout = None


    def finish(self) -> None:
        self.current_state = None
        self.current_timeout = None
        for led in self.leds.values():
            if led is not None:
                led.value = Job.LED_STATES['OFF']
                led.deinit()


    def concurrency(self) -> bool:
        return False

