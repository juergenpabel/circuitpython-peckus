from alarm import sleep_memory as alarm_sleep_memory

from . import AbstractAction


class Action(AbstractAction):

    def __init__(self, sm_method: str, sm_data: Any, app_data: dict):
        super().__init__('sm', sm_method, app_data)
        if sm_data is not None:
            self.sm_data = sm_data
        else:
            self.sm_data = 0xc0


    def erase(self) -> None:
        for chunk_offset in range(0, len(alarm_sleep_memory)):
            alarm_sleep_memory[chunk_offset] = self.sm_data

