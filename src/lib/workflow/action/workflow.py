from . import AbstractAction


class Action(AbstractAction):

    def __init__(self, workflow_method: str, workflow_data: str, app_data: dict):
        super().__init__('workflow', workflow_method, app_data)
        self.workflow_data = workflow_data


    def exit(self) -> None:
        raise SystemExit()

