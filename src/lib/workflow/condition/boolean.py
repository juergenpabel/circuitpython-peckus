from . import AbstractCondition


class Condition(AbstractCondition):

    def __init__(self, boolean_method: str, boolean_criteria: str, app_data: dict):
        super().__init__("boolean", boolean_method, app_data)
        self.boolean_criteria = boolean_criteria

    def false(self) -> bool:
        return False

    def true(self) -> bool:
        return True

