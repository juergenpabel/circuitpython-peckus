from peckus.application import ApplicationState
from peckus.workflow.action import AbstractAction


class Action(AbstractAction):

    def __init__(self, session_method: str, session_data: str, app_data: dict):
        super().__init__('session', session_method, app_data)
        self.session_data = session_data


    def workflow(self) -> None:
        self.app_data['session'].set(ApplicationState.WORKFLOW, self.session_data)


    def set(self) -> None:
        if ':' not in self.session_data:
            raise ValueError(f"Action<session>.set('{self.session_data}'): invalid data (missing ':')")
        key, value = self.session_data.split(':', 1)
        self.app_data['session'].set(key, value, 0)

