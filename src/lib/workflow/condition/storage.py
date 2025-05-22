from . import AbstractCondition

from peckus.application import ApplicationState


class Condition(AbstractCondition):

    def __init__(self, storage_method: str, storage_data: str, app_data: dict):
        super().__init__('storage', storage_method, app_data)
        self.storage_data = storage_data


    def application(self) -> bool:
        return self.app_data['storage'].get(ApplicationState.RUNTIME) == self.storage_data.upper()

