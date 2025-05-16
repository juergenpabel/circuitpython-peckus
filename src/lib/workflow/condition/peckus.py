from . import AbstractCondition

from peckus.application import ApplicationState


class Condition(AbstractCondition):

    def __init__(self, peckus_method: str, peckus_data: str, app_data: dict):
        super().__init__('peckus', peckus_method, app_data)
        self.peckus_data = peckus_data


    def workflow(self) -> bool:
        return self.app_data['session'].get(ApplicationState.WORKFLOW) == self.peckus_data


    def runtime(self) -> bool:
        return self.app_data['storage'].get(ApplicationState.RUNTIME) == self.peckus_data.upper()


    def requirement_valid(self) -> bool:
        requirement = self.peckus_data
        validity_delta = 0
        if ':' in self.peckus_data:
            requirement, validity_delta = self.peckus_data.split(':', 1)
            try:
                validity_delta = int(validity_delta)
            except ValueError as e:
                print(f"Condition<peckus>.requirement_valid({self.peckus_data}) validity delta is not a number ('{validity_delta}'), using 0 instead")
        return self.app_data['session'].get(requirement, validity_delta) is not None


    def requirement_invalid(self) -> bool:
        return not(self.requirement_valid())

