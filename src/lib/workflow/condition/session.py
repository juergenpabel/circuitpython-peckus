from . import AbstractCondition

from peckus.application import ApplicationState


class Condition(AbstractCondition):

    def __init__(self, session_method: str, session_data: str, app_data: dict):
        super().__init__('session', session_method, app_data)
        self.session_data = session_data


    def workflow(self) -> bool:
        return self.app_data['session'].get(ApplicationState.WORKFLOW) == self.session_data


