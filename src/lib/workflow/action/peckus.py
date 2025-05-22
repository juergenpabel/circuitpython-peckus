from microcontroller import nvm as microcontroller_nvm, \
                            reset as microcontroller_reset
from os import stat as os_stat
from alarm import sleep_memory as alarm_sleep_memory
from traceback import print_exception as traceback_print_exception

from peckus.application import StatusRuntime, ApplicationState
from peckus.util.datastream import DataStream
from peckus.workflow.action.sm import Action as ActionSM
from peckus.workflow.action.nvm import Action as ActionNVM
from peckus.workflow.action.filesystem import Action as ActionFilesystem
from peckus.workflow.action.circuitpython import Action as ActionCircuitPython
from peckus.workflow.condition.button import Condition as ConditionButton
from . import AbstractAction


class Action(AbstractAction):

    def __init__(self, peckus_method: str, peckus_data: str, app_data: dict):
        super().__init__('peckus', peckus_method, app_data)
        self.peckus_data = peckus_data


    def reload(self) -> None:
        application = self.app_data['peckus']['application'].name
        for workflow in self.app_data['configuration']['application'][application]['workflows']:
            if workflow['name'] == self.peckus_data:
                print(f"PECKUS: reloading application (workflow='{self.peckus_data}')")
                self.app_data['session'].set(ApplicationState.WORKFLOW, workflow['name'])
                ActionCircuitPython('reload', None, self.app_data).reload()


    def restart(self) -> None:
        for workflow in self.app_data['configuration']['application']['boot.py']['workflows']:
            if workflow['name'] == self.peckus_data:
                print(f"PECKUS: restarting system (workflow='{self.peckus_data}')")
                self.app_data['session'].set(ApplicationState.WORKFLOW, workflow['name'])
                ActionCircuitPython('reset', None, self.app_data).reset()


    def configure(self) -> None:
        self.app_data['peckus']['application'].save_configuration_nvm()


    def requirements(self) -> None:
        try:
            requirements_action = eval(self.peckus_data)
            if isinstance(requirements_action, list) is False:
                raise ValueError(f"eval('{self.peckus_data}') did not return a list")
            for requirement in requirements_action:
                if '=' not in requirement:
                    raise ValueError(f"eval('{self.peckus_data}') did not return a list with all elements having a requirements value (like ['KEY=VALUE', ...])")
            requirements_action = {requirement.split('=', 1).pop(0): requirement.split('=', 1).pop(1) for requirement in requirements_action}
            for key in self.app_data['session'].get('REQUIREMENTS', {}).keys():
                if key not in requirements_action:
                    self.app_data['session'].set(key, None)
            requirements_session = {}
            for key, value in requirements_action.items():
                requirements_session[key] = value
            self.app_data['session'].set('REQUIREMENTS', requirements_session, 0)
        except Exception as e:
            print(f"invalid value for 'peckus:requirements': {self.peckus_data}")
            traceback_print_exception(e)


    def requirement(self) -> None:
        try:
            requirement, value, validity = self.peckus_data.split(':', 2)
            if requirement in self.app_data['session'].get('REQUIREMENTS', {}):
                self.app_data['session'].set(requirement, value, int(validity))
        except Exception as e:
            print(f"Action<peckus>('{self.peckus_data}').requirement(): invalid data (NAME:bool(VALUE):int(VALIDITY))")
            traceback_print_exception(e)


    def requirement_button_reset(self) -> None:
        if ConditionButton('reset', 'TRUE', {}).reset() is True:
            self.requirement()


    def factory_reset(self) -> None:
        ActionFilesystem('remount', 'READWRITE', {}).remount()
        ActionFilesystem('file_shred', self.peckus_data, {}).file_shred()
        ActionNVM('erase', None, self.app_data).erase()
        ActionSM('erase', None, self.app_data).erase()
        ActionCircuitPython('reset', None, self.app_data).reset()

