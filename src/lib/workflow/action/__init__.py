from re import match as re_match


class AbstractAction:

    def __init__(self, action_class: str, action_method: str, app_data: dict):
        self.action_class = action_class
        self.action_method = getattr(self, action_method, None)
        self.app_data = app_data
        if action_class not in self.app_data:
            self.app_data[action_class] = {}
        if callable(self.action_method) is False:
            raise NotImplementedError(f"Action<{self.action_class}>.{self.action_method}() is not implemented")

    def __call__(self) -> bool:
            return self.action_method()

