from . import AbstractCondition


class Condition(AbstractCondition):

    def __init__(self, boolean_method: str, boolean_params: str, app_data: dict):
        super().__init__('boolean', boolean_method, app_data)
        self.boolean_params = boolean_params


    def true(self) -> bool:
        return 'TRUE' == self.boolean_params.upper()


    def false(self) -> bool:
        return 'FALSE' == self.boolean_params.upper()

