from re import match as re_match


class Conditions:

    def __init__(self, conditions, appdata: dict):
        if 'condition_classes' not in appdata:
            appdata['condition_classes'] =  {}
        self.conditions = []
        for condition in conditions:
            matches = re_match(r'^(\w+):(\w+)=(.*)$', condition)
            if matches is None:
                raise NameError(f"Invalid condition syntax: {condition}")
            matches = matches.groups()
            if len(matches) == 3:
                condition_module = matches[0]
                condition_class  = f'Condition_{condition_module.upper()}'
                condition_method = matches[1]
                condition_params = matches[2]
                exec(f'from peckus.workflow.condition.{condition_module} import Condition as {condition_class}')
                appdata['condition_classes'][condition_class] = eval(condition_class)
                self.conditions.append(appdata['condition_classes'][condition_class](condition_method, condition_params, appdata))


    def __call__(self):
        for condition in self.conditions:
            if condition() is False:
                return False
        return True

