from re import match as re_match


class TransitionActions:

    def __init__(self, actions: list, appdata: dict):
        if 'action_classes' not in appdata:
            appdata['action_classes'] =  {}
        self.actions = []
        for action in actions:
            matches = re_match(r'^(\w+):(\w+)=(.*)$', action)
            if matches is None:
                raise NameError(f"Invalid action syntax: {action}")
            matches = matches.groups()
            if len(matches) == 3:
                action_module = matches[0]
                action_class  = f'Action_{action_module.upper()}'
                action_method = matches[1]
                action_params = matches[2]
                exec(f'from peckus.workflow.action.{action_module} import Action as {action_class}')
                appdata['action_classes'][action_class] = eval(action_class)
                self.actions.append(appdata['action_classes'][action_class](action_method, action_params, appdata))


    def __call__(self) -> None:
        for action in self.actions:
            try:
                action()
            except Exception as e:
                print(f"Action<{action.action_class}>.{action.action_method}() raised an exception: {e}")

