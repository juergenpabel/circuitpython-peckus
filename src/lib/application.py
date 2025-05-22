from microcontroller import nvm as microcontroller_nvm
from os import getenv as os_getenv
from gc import collect as gc_collect
from io import BytesIO as io_BytesIO
from time import monotonic as time_monotonic
from json import load as json_load
from traceback import print_exception as traceback_print_exception

from cpstatemachine import StateMachineManager as cp_StateMachineManager

from peckus.workflow.jobs import Jobs
from peckus.workflow.job.actions import Job as JobAction
from peckus.workflow.conditions import Conditions
from peckus.util.datastream import DataStream
from peckus.util.session import Session
from peckus.util.storage import Storage


class StatusRuntime():
    UNKNOWN       = 'UNKNOWN'
    INSTALLED     = 'INSTALLED'
    CONFIGURED    = 'CONFIGURED'
    DEPLOYED      = 'DEPLOYED'
    FAILED        = 'FAILED'
    EXITED        = 'EXITED'


class ApplicationState():
    RUNTIME     = 'runtime'
    WORKFLOW    = 'workflow'
    ERROR       = 'error'
    USB_STORAGE = 'usb-storage'
    USB_SERIAL  = 'usb-serial'
    BLE_NETWORK = 'ble-network'


class Application:

    def __init__(self, name: str):
        self.name = name
        self.data = {}
        self.data['nvm'] = {}
        self.data['nvm']['size'] = len(microcontroller_nvm)
        self.data['nvm']['storage'] = {}
        self.data['nvm']['storage']['offset'] = 0
        self.data['nvm']['storage']['length'] = 64
        self.data['nvm']['config'] = {}
        self.data['nvm']['config']['offset'] = 64
        self.data['nvm']['config']['length'] = len(microcontroller_nvm)-64
        self.data['session'] = Session()
        self.data['storage'] = Storage(self.data['nvm']['storage']['offset'], self.data['nvm']['storage']['length'])
        if self.data['storage'].get(ApplicationState.RUNTIME) is None:
            self.data['storage'].set(ApplicationState.RUNTIME, StatusRuntime.UNKNOWN)
        self.data['configuration'] = None


    def get_storage(self, key: str) -> Any:
        return self.data['storage'].get(key)


    def set_storage(self, key: str, value: Any) -> None:
        return self.data['storage'].set(key, value)


    def get_session(self, key: str) -> Any:
        return self.data['session'].get(key)


    def set_session(self, key: str, value: Any, validity: int=0) -> None:
        return self.data['session'].set(key, value, validity)


    def getenv(self, key: str, default: str = None) -> str:
        if self.data['configuration'] is None:
            return os_getenv(key, default)
        key = key[7:None] # remove 'PECKUS_' prefix
        if key not in self.data['configuration']['settings']:
            return default
        return self.data['configuration']['settings'][key]


    def load_configuration_file(self) -> bool:
        configuration_filename = os_getenv('PECKUS_APP_CONFIG_FILENAME')
        if configuration_filename is None:
            print(f"no configuration file configured (PECKUS_APP_CONFIG_FILENAME in settings.toml) or missing settings.tonl")
            return False
        try:
            with open(configuration_filename, 'r') as f:
                self.data['configuration'] = json_load(f)
            if isinstance(self.data['configuration'], dict) is False:
                self.data['configuration'] = None
                raise ValueError(f"data error in '{configuration_filename}'")
            if 'description' in self.data['configuration']:
                del self.data['configuration']['description']
            if 'settings' not in self.data['configuration']:
                self.data['configuration']['settings'] = {}
            if 'application' not in self.data['configuration']:
                raise ValueError(f"No 'application' in configuration")
            if self.name not in self.data['configuration']['application']:
                raise ValueError(f"Application '{self.name}' not in configuration")
            if 'workflows' not in self.data['configuration']['application'][self.name]:
                raise ValueError(f"No workflows defined in configuration")
            for setting_name, setting_data in self.data['configuration']['settings'].items():
                setting_value = os_getenv(f'PECKUS_{setting_name}', setting_data['default'])
                if 'validator' in setting_data:
                    try:
                        if setting_data['validator'].lower() == 'boolean':
                            setting_value = str(setting_value.upper() == str(True).upper()).upper()
                        elif setting_data['validator'].lower() == 'integer':
                            setting_value = str(int(setting_value))
                        elif setting_data['validator'].lower() == 'hexadecimal':
                            setting_value = hex(int(setting_value, 16))
                        elif setting_data['validator'].lower() == 'string':
                            setting_value = str(setting_value)
                    except ValueError:
                        setting_value = setting_data['default']
                self.data['configuration']['settings'][setting_name] = str(setting_value)
            for workflow in self.data['configuration']['application'][self.name]['workflows']:
                if 'name' not in workflow:
                    raise ValueError(f"Missing name for workflow in application '{self.name}'")
                if 'states' not in workflow:
                    raise ValueError(f"No states defined for workflow '{workflow['name']}' in application '{self.name}'")
                for state in workflow['states']:
                    if 'name' not in state:
                        raise ValueError(f"Missing 'name' item for state in workflow '{workflow['name']}' in application '{self.name}'")
                    if 'jobs' not in state:
                        raise ValueError(f"No jobs defined for state '{state['name']}' in workflow '{workflow['name']}' in application '{self.name}'")
                    if 'actions' not in state:
                        raise ValueError(f"No actions defined for state '{state['name']}' in workflow '{workflow['name']}' in application '{self.name}'")
                    if 'transitions' not in state:
                        raise ValueError(f"No transitions defined for state '{state['name']}' in workflow '{workflow['name']}' in application '{self.name}'")
                if workflow['name'] not in [state['name'] for state in workflow['states']]:
                    raise ValueError(f"Missing state '{workflow['name']}' as initial state for workflow '{workflow['name']}' in application '{self.name}'")
            settings = self.data['configuration']['settings'].copy()
            for application in self.data['configuration']['application'].keys():
                for workflow in self.data['configuration']['application'][application]['workflows']:
                    for state in workflow['states']:
                        for action_pos in range(0, len(state['actions'])):
                            formatted = False
                            while formatted is False:
                                try:
                                    state['actions'][action_pos] = state['actions'][action_pos].format(**settings)
                                    formatted = True
                                except KeyError as e:
                                    print(f"undefined setting '{str(e)}' referenced in state '{state['name']}' in workflow '{workflow['name']}', using empty string as value")
                                    settings[str(e)] = ''
                        for transition_pos in range(0, len(state['transitions'])):
                            for condition_pos in range(0, len(state['transitions'][transition_pos]['conditions'])):
                                formatted = False
                                while formatted is False:
                                    try:
                                        state['transitions'][transition_pos]['conditions'][condition_pos] = state['transitions'][transition_pos]['conditions'][condition_pos].format(**settings)
                                        formatted = True
                                    except KeyError as e:
                                        print(f"undefined setting '{str(e)}' referenced in state '{state['name']}' in workflow '{workflow['name']}', using empty string as value")
                                        settings[str(e)] = ''
            self.data['storage'].set(ApplicationState.RUNTIME, StatusRuntime.INSTALLED)
        except Exception as e:
            print(f"error loading configuration '{configuration_filename}' from CIRCUITPY: {e}")
            traceback_print_exception(e)
            return False
        return True


    def test_configuration_nvm(self) -> bool:
        nvm_offset = self.data['nvm']['config']['offset']
        nvm_length = self.data['nvm']['config']['length']
        if DataStream('NVM:config').test(microcontroller_nvm, nvm_offset, nvm_length) is False:
            return False
        return True


    def load_configuration_nvm(self) -> bool:
        nvm_offset = self.data['nvm']['config']['offset']
        nvm_length = self.data['nvm']['config']['length']
        self.data['configuration'] = DataStream('NVM:config').load(microcontroller_nvm, nvm_offset, nvm_length)
        if isinstance(self.data['configuration'], dict) is False:
            print(f"no configuration stored in NVM")
            self.data['configuration'] = None
            return False
        return True


    def save_configuration_nvm(self) -> bool:
        nvm_offset = self.data['nvm']['config']['offset']
        nvm_length = self.data['nvm']['config']['length']
        if DataStream('NVM:config').save(self.data['configuration'], microcontroller_nvm, nvm_offset, nvm_length) is False:
            print(f"error saving configuration to NVM")
            return False
        self.data['storage'].set(ApplicationState.RUNTIME, StatusRuntime.CONFIGURED)
        return True


    def workflows_create(self):
        self.data['workflows'] = []
        if self.data['configuration'] is not None:
            try:
                self.smm = cp_StateMachineManager()
                workflow_name = self.data['session'].get(ApplicationState.WORKFLOW)
                workflow_names = []
                for workflow in self.data['configuration']['application'][self.name]['workflows']:
                    if workflow_name is None:
                        workflow_names.append(workflow['name'])
                    elif workflow['name'] == workflow_name:
                        workflow_names.append(workflow['name'])
                        if 'sub-workflows' in workflow:
                            workflow_names.extend(workflow['sub-workflows'])
                print(f"creating workflows based on session value 'workflow': {workflow_name if workflow_name is not None else '*'}")
                for workflow in self.data['configuration']['application'][self.name]['workflows']:
                    if workflow['name'] in workflow_names:
                        print(f"creating workflow '{workflow['name']}'")
                        sm = self.smm.CreateStateMachine(workflow['name'])
                        for state in workflow['states']:
                            print(f"  adding state '{state['name']}' to workflow '{workflow['name']}'")
                            jobs = Jobs(state['jobs'], self.data)
                            jobs.add(JobAction(state['actions'], self.data))
                            sm.AddState(state['name'], jobs.begin, jobs.update, jobs.finish)
                            for transition in state['transitions']:
                                sm.AddTransition(state['name'], Conditions(transition['conditions'], self.data), transition['state'])
                        self.data['workflows'].append(workflow['name'])
            except Exception as e:
                print(f"Application.workflows_create(): {e}")
                traceback_print_exception(e)
                self.smm = None
                self.data['storage'].set(ApplicationState.RUNTIME, StatusRuntime.FAILED)
                self.data['session'].set(ApplicationState.ERROR, str(e))


    def workflows_run(self):
        if self.smm is not None and self.data['storage'].get(ApplicationState.RUNTIME) not in [StatusRuntime.UNKNOWN, StatusRuntime.FAILED]:
            if 'peckus' in self.data:
                self.data['peckus']['application'] = self # hack for accessing application instance
            try:
                for name in self.data['workflows']:
                    self.smm.GetStateMachine(name).SetState(name)
                while True:
                    self.smm.Update()
                    gc_collect()
            except SystemExit:
                pass
            except Exception as e:
                self.smm = None
                self.data['storage'].set(ApplicationState.RUNTIME, StatusRuntime.FAILED)
                self.data['session'].set(ApplicationState.ERROR, str(e))
                print(f"Application.workflows_run(): {e}")
                traceback_print_exception(e)

