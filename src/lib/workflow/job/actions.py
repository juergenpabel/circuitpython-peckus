from time import monotonic as time_monotonic
from re import match as re_match
from traceback import print_exception as traceback_print_exception

from peckus.workflow.job import AbstractJob

class Job(AbstractJob):

    def __init__(self, actions: dict, app_data: dict):
        super().__init__('actions', 'state', app_data)
        if 'action_classes' not in self.app_data:
            self.app_data['action_classes'] =  {}
        self.actions = []
        for action in actions:
            matches = re_match(r'^(\w+):([\w-]+)=(.*)$', action)
            if matches is None:
                raise NameError(f"Invalid action syntax: {action}")
            matches = matches.groups()
            if len(matches) == 3:
                action_module = matches[0]
                action_class  = f'Action_{action_module.upper()}'
                action_method = matches[1]
                action_params = matches[2]
                exec(f'from peckus.workflow.action.{action_module} import Action as {action_class}')
                app_data['action_classes'][action_class] = eval(action_class)
                self.actions.append(app_data['action_classes'][action_class](action_method, action_params, self.app_data))


    def begin(self) -> None:
        for action in self.actions:
            try:
                action()
            except Exception as e:
                print(f"Action<{action.action_class}>.{action.action_method.__name__.split('.').pop()}() raised an exception: {e}")
                traceback_print_exception(e)


    def update(self) -> None:
        pass


    def finish(self) -> None:
        pass

