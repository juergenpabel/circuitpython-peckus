from peckus.application import StatusPayload
from . import AbstractCondition


class Condition(AbstractCondition):

    def __init__(self, peckus_method: str, peckus_params: str, app_data: dict):
        super().__init__("peckus", peckus_method, app_data)
        self.peckus_params = peckus_params

    def runtime(self) -> bool:
        return self.app_data['status']['runtime'] == self.peckus_params.upper()

    def payload(self) -> bool:
        return self.app_data['status']['payload'] == self.peckus_params.upper()

