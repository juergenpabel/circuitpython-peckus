from re import match as re_match


class AbstractCondition:

    def __init__(self, condition_class: str, condition_method: str, app_data: dict):
        if condition_class not in app_data:
            app_data[condition_class] = {}
        self.condition_class = condition_class
        self.condition_method = getattr(self, condition_method.replace('-', '_'), None)
        self.app_data = app_data
        if callable(self.condition_method) is False:
            raise NotImplementedError(f"Condition<{condition_class}>.{condition_method}() is not implemented")

    def __call__(self) -> bool:
            return self.condition_method()

