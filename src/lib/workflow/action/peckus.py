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


    def runtime(self) -> None:
        self.app_data['storage'].set(ApplicationState.RUNTIME, self.peckus_data)


    def workflow(self) -> None:
        self.app_data['session'].set(ApplicationState.WORKFLOW, self.peckus_data)


    def session(self) -> None:
        if ':' not in self.peckus_data:
            raise ValueError(f"Action<peckus>.session('{self.peckus_data}'): invalid data (missing ':')")
        key, value = self.peckus_data.split(':', 1)
        self.app_data['session'].set(key, value, None)


    def storage(self) -> None:
        if ':' not in self.peckus_data:
            raise ValueError(f"Action<peckus>.session('{self.peckus_data}'): invalid data (missing ':')")
        key, value = self.peckus_data.split(':', 1)
        self.app_data['storage'].set(key, value, None)


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
            requirements = eval(self.peckus_data)
            if requirements is None:
                requirements = self.app_data['session'].get('REQUIREMENTS')
                if isinstance(requirements, dict) is True:
                    for requirement in requirements.keys():
                        self.app_data['session'].set(requirement, None)
                self.app_data['session'].set('REQUIREMENTS', {}, None)
                return
            if isinstance(requirements, list) is False:
                raise ValueError(f"eval('{self.peckus_data}') did not return a list")
            requirements_data = self.app_data['session'].get('REQUIREMENTS')
            if isinstance(requirements_data, dict) is False:
                requirements_data = {}
            for requirement in requirements:
                key, value = requirement.split('=', 1)
                if value != 'FALSE': #TODO: non-hardcoded concept
                    requirements_data[key] = value
            self.app_data['session'].set('REQUIREMENTS', requirements_data, None)
        except Exception as e:
            print(f"invalid value for 'peckus:requirements': {self.peckus_data}")
            traceback_print_exception(e)


    def requirement_validity(self) -> None:
        if ':' in self.peckus_data:
            try:
                requirement, validity = self.peckus_data.split(':', 1)
                validity = int(validity) if int(validity) != 0 else None
                requirements_data = self.app_data['session'].get('REQUIREMENTS')
                if isinstance(requirements_data, dict) is False:
                    requirements_data = {}
                if requirement in requirements_data:
                    self.app_data['session'].set(requirement, requirements_data[requirement], validity)
            except Exception as e:
                print(f"invalid value for 'peckus:requirement-validity': {self.peckus_data}")
                traceback_print_exception(e)


    def requirement_validity_button_reset(self) -> None:
        if ConditionButton('reset', 'TRUE', {}).reset() is True:
            self.requirement_validity()


    def factory_reset(self) -> None:
        ActionFilesystem('remount', 'READWRITE', {}).remount()
        ActionFilesystem('file_shred', self.peckus_data, {}).file_shred()
        ActionNVM('erase', None, self.app_data).erase()
        ActionSM('erase', None, self.app_data).erase()
        ActionCircuitPython('reset', None, self.app_data).reset()

