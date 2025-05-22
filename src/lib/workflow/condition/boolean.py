from . import AbstractCondition


class Condition(AbstractCondition):

    def __init__(self, boolean_method: str, boolean_params: str, app_data: dict):
        super().__init__('boolean', boolean_method, app_data)
        self.boolean_params = boolean_params


    def true(self) -> bool:
        return str(True).upper() == self.boolean_params.upper()


    def false(self) -> bool:
        return str(False).upper() == self.boolean_params.upper()

