from board import LED_RED as board_LED_RED, \
                  LED_GREEN as board_LED_GREEN, \
                  LED_BLUE as board_LED_BLUE
from digitalio import DigitalInOut as digitalio_DigitalInOut, \
                      Direction as digitalio_Direction
from time import monotonic as time_monotonic

from peckus.workflow.job import AbstractJob


class Lifetime():
    STATE    = 'state'
    WORKFLOW = 'workflow'


class LED():
    RED   = 'RED'
    GREEN = 'GREEN'
    BLUE  = 'BLUE'


class Job(AbstractJob):

    LED_NAMES  = {LED.RED: board_LED_RED, LED.GREEN: board_LED_GREEN, LED.BLUE: board_LED_BLUE}
    LED_STATES = {'OFF': True, 'ON': False}

    def __init__(self, name: str, configuration: dict, app_data: dict):
        super().__init__('led', name, app_data)
        self.lifetime = configuration['lifetime'] if 'lifetime' in configuration else Lifetime.STATE
        self.states = []
        if 'states' not in configuration or len(configuration['states']) == 0:
            raise ValueError(f"missing 'states' definition in job '{name}'")
        for state_configuration in configuration['states']:
            led_configuration = {}
            for color in Job.LED_NAMES.keys():
                led_configuration[color] = Job.LED_STATES[state_configuration[color]] if color in state_configuration and state_configuration[color] in Job.LED_STATES else Job.LED_STATES['OFF']
            led_configuration['millis'] = state_configuration['millis'] if 'millis' in state_configuration else None
            self.states.append(led_configuration)
        self.current_state = None
        self.current_timeout = None


    def begin(self) -> None:
        for color, pin in Job.LED_NAMES.items():
            if color not in self.app_data['led']:
                try:
                    self.app_data['led'][color] = digitalio_DigitalInOut(pin)
                    self.app_data['led'][color].direction = digitalio_Direction.OUTPUT
                    self.app_data['led'][color].value = Job.LED_STATES['OFF']
                except Exception as e:
                    print(f"Job<led>.begin(): error initializing led '{color}': {e}")
                    self.app_data['led'][color] = None
        self.led_original_values = {}
        for color, led in self.app_data['led'].items():
            if led is not None:
                try:
                    self.led_original_values[color] = led.value
                    led.value = self.states[0][color] if color in self.states[0] else Job.LED_STATES['OFF']
                except Exception as e:
                    print(f"Job<led>.begin(): error processing '{color}': {e}")
        self.current_state = -1
        self.current_timeout = -1


    def update(self) -> None:
        if self.current_state is not None and self.current_timeout is not None:
            if time_monotonic() >= self.current_timeout:
                self.current_state += 1
                self.current_state %= len(self.states)
                for color, led in self.app_data['led'].items():
                    if led is not None:
                        led.value = self.states[self.current_state][color] if color in self.states[self.current_state] else Job.LED_STATES['OFF']
                if self.states[self.current_state]['millis'] not in [None, 0]:
                    self.current_timeout = time_monotonic() + (self.states[self.current_state]['millis'] / 1000)
                else:
                    self.current_timeout = None


    def finish(self) -> None:
        if self.current_state is not None:
            if self.lifetime == Lifetime.STATE:
                for color, led in self.app_data['led'].items():
                    if color in self.led_original_values:
                        if self.app_data['led'][color] is not None:
                            self.app_data['led'][color].value = self.led_original_values[color]
                self.current_state = None
                self.current_timeout = None

