from peckus.application import ApplicationState
from peckus.workflow.action import AbstractAction


class Action(AbstractAction):

    def __init__(self, storage_method: str, storage_data: str, app_data: dict):
        super().__init__('storage', storage_method, app_data)
        self.storage_data = storage_data


    def application(self) -> None:
        self.app_data['storage'].set(ApplicationState.RUNTIME, self.storage_data)


    def set(self) -> None:
        if ':' not in self.storage_data:
            raise ValueError(f"Action<storage>.set('{self.storage_data}'): invalid data (missing ':')")
        key, value = self.storage_data.split(':', 1)
        self.app_data['storage'].set(key, value)

