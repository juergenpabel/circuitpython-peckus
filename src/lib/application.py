from microcontroller import nvm as microcontroller_nvm
from os import getenv as os_getenv
from gc import collect as gc_collect
from io import BytesIO as io_BytesIO
from msgpack import unpack as msgpack_unpack, \
                    pack as msgpack_pack
from json import load as json_load
from re import compile as re_compile
from traceback import print_exception as traceback_print_exception

from cpstatemachine import StateMachineManager as cp_StateMachineManager

from peckus.workflow.jobs import Jobs
from peckus.workflow.job.actions import Job as Actions
from peckus.workflow.conditions import Conditions


class OriginConfiguration():
    NONE = 'NONE'
    FILE = 'FILE'
    NVM  = 'NVM'

class StatusRuntime():
    UNINITIALIZED = 'UNINITIALIZED'
    INITIALIZED   = 'INITIALIZED'
    CONFIGURED    = 'CONFIGURED'
    LOADED        = 'LOADED'
    RUNNING       = 'RUNNING'
    HALTED        = 'HALTED'

class StatusPayload():
    UNINITIALIZED = 'UNINITIALIZED'
    INSTALLED     = 'INSTALLED'
    LOCKED        = 'LOCKED'
    UNLOCKED      = 'UNLOCKED'


class Application:

    def __init__(self):
        self.configuration = None
        self.data = {'status': {'runtime': StatusRuntime.UNINITIALIZED, 'payload': StatusPayload.UNINITIALIZED}}
        self.data['configuration'] = {'origin': OriginConfiguration.NONE}
        self.data['nvm'] = {}
        self.data['nvm']['size'] = len(microcontroller_nvm)
        self.data['nvm']['config'] = {}
        self.data['nvm']['config']['offset'] = 0
        self.data['nvm']['config']['length'] = min(int(len(microcontroller_nvm)/2), 4096)
        self.data['nvm']['payload'] = {}
        self.data['nvm']['payload']['offset'] = self.data['nvm']['config']['offset'] + self.data['nvm']['config']['length']
        self.data['nvm']['payload']['length'] = self.data['nvm']['size'] - self.data['nvm']['payload']['offset']


    def runtime_status(self) -> StatusRuntime:
        return self.data['status']['runtime']


    def payload_status(self) -> StatusPayload:
        return self.data['status']['payload']


    def load_configuration_file(self) -> bool:
        configuration_filename = os_getenv('PECKUS_CONFIG_FILENAME')
        if configuration_filename is None:
            print(f"no configuration file configured (PECKUS_CONFIG_FILENAME in settings.toml)")
            return False
        print(f"loading configuration '{configuration_filename}' from CIRCUITPY...")
        try:
            with open(configuration_filename, 'r') as f:
                self.configuration = json_load(f)
            if isinstance(self.configuration, dict) is False:
                raise ValueError(f"data error in '{configuration_filename}'")
            regex_check = re_compile(r'^.*\$\{.*\}.*$')
            regex_match = re_compile(r'^([^\$]*)\$\{([A-Za-z0-9_]+)=([^\}]+)\}(.*)$')
            if 'parameters' not in self.configuration:
                self.configuration['parameters'] = {}
            parameters = self.configuration['parameters']
            for key in parameters.keys():
                value = parameters[key]
                while regex_check.match(value) is not None:
                    matches = regex_match.match(value)
                    if matches is None:
                        raise ValueError(f"configuration parameter '{key}' contains invalid variable syntax (format must be '${{OS_ENV_NAME=DEFAULT_VALUE}}')")
                    matches = matches.groups()
                    data_prefix = matches[0]
                    var_name    = matches[1]
                    var_default = matches[2]
                    data_suffix = matches[3]
                    data_value = os_getenv(var_name)
                    if data_value is None:
                        data_value = var_default
                    value = f'{data_prefix}{data_value}{data_suffix}'
                parameters[key] = value
            if 'workflows' not in self.configuration:
                raise ValueError(f"No workflows defined in configuration")
            for workflow in self.configuration['workflows']:
                if 'name' not in workflow:
                    raise ValueError(f"Missing name for workflow")
                if 'states' not in workflow:
                    raise ValueError(f"No states defined for workflow '{workflow['name']}'")
                if 'initial-state' not in workflow:
                    raise ValueError(f"No initial state defined for workflow '{workflow['name']}'")
                for state in workflow['states']:
                    if 'name' not in state:
                        raise ValueError(f"Missing 'name' item for state in workflow '{workflow['name']}'")
                    if 'jobs' not in state:
                        raise ValueError(f"No jobs defined for state '{state['name']}' in workflow '{workflow['name']}'")
                    if 'actions' not in state:
                        raise ValueError(f"No actions defined for state '{state['name']}' in workflow '{workflow['name']}'")
                    if 'transitions' not in state:
                        raise ValueError(f"No transitions defined for state '{state['name']}' in workflow '{workflow['name']}'")
                if workflow['initial-state'] not in [state['name'] for state in workflow['states']]:
                    raise ValueError(f"Invalid state '{workflow['initial-state']}' specified as initial state for workflow '{workflow['name']}'")
            for workflow in self.configuration['workflows']:
                for state in workflow['states']:
                    for action_pos in range(0, len(state['actions'])):
                        formatted = False
                        while formatted is False:
                            try:
                                state['actions'][action_pos] = state['actions'][action_pos].format(**parameters)
                                formatted = True
                            except KeyError as e:
                                print(f"undefined parameter '{str(e)}' referenced in state '{state['name']}' in workflow '{workflow['name']}', using empty string as value")
                                parameters[str(e)] = ''
                    for transition_pos in range(0, len(state['transitions'])):
                        for condition_pos in range(0, len(state['transitions'][transition_pos]['conditions'])):
                            formatted = False
                            while formatted is False:
                                try:
                                    state['transitions'][transition_pos]['conditions'][condition_pos] = state['transitions'][transition_pos]['conditions'][condition_pos].format(**parameters)
                                    formatted = True
                                except KeyError as e:
                                    print(f"undefined parameter '{str(e)}' referenced in state '{state['name']}' in workflow '{workflow['name']}', using empty string as value")
                                    parameters[str(e)] = ''
            del self.configuration['parameters']
            self.data['configuration']['origin'] = OriginConfiguration.FILE
            self.data['status']['runtime'] = StatusRuntime.CONFIGURED
            print(f"...successful")
        except Exception as e:
            print(f"...failed (exception: {e})")
            return False
        return True


    def test_configuration_nvm(self) -> bool:
        print(f"testing if configuration is stored in NVM...")
        try:
            nvm_offset_config = self.data['nvm']['config']['offset']
            nvm_length_config = self.data['nvm']['config']['length']
            config = msgpack_unpack(io_BytesIO(microcontroller_nvm[nvm_offset_config:nvm_offset_config+nvm_length_config]))
            if isinstance(config, dict) is False:
                raise ValueError(f"no configuration data in NVM")
            print(f"...YES")
        except Exception as e:
            print(f"...NO (exception: {e})")
            return False
        return True


    def load_configuration_nvm(self) -> bool:
        print(f"loading configuration from NVM...")
        try:
            nvm_offset_config = self.data['nvm']['config']['offset']
            nvm_length_config = self.data['nvm']['config']['length']
            self.configuration = msgpack_unpack(io_BytesIO(microcontroller_nvm[nvm_offset_config:nvm_offset_config+nvm_length_config]))
            if isinstance(self.configuration, dict) is False:
                raise ValueError(f"no configuration data in NVM")
            self.data['configuration']['origin'] = OriginConfiguration.NVM
            self.data['status']['runtime'] = StatusRuntime.CONFIGURED
            print(f"...successful")
        except Exception as e:
            print(f"...failed (exception: {e})")
            return False
        return True


    def save_configuration_nvm(self) -> bool:
        print(f"saving configuration to NVM...")
        try:
            data = io_BytesIO()
            msgpack_pack(self.configuration, data)
            data = data.getvalue()
            nvm_offset_config = self.data['nvm']['config']['offset']
            nvm_length_config = self.data['nvm']['config']['length']
            if len(data) > nvm_length_config:
                raise ValueError("configuration too big for NVM configuration area ({len(data)} bytes > {nvm_length_config} bytes})")
            microcontroller_nvm[nvm_offset_config:nvm_offset_config+len(data)] = data
            print(f"...successful")
        except Exception as e:
            print(f"...failed (exception: {e})")
            return False
        return True


    def test_payload_nvm(self) -> bool:
        print(f"testing if payload is stored in NVM...")
        try:
            nvm_offset_payload = self.data['nvm']['payload']['offset']
            nvm_length_payload = self.data['nvm']['payload']['length']
            payload = msgpack_unpack(io_BytesIO(microcontroller_nvm[nvm_offset_payload:nvm_offset_payload+nvm_length_payload]))
            if isinstance(payload, bytes) is False:
                raise ValueError(f"no payload data in NVM")
            self.data['status']['payload'] = StatusPayload.INSTALLED
            print(f"...YES")
        except Exception as e:
            print(f"...NO ({e})")
            return False
        return True


    def load_payload_nvm(self) -> bool:
        print(f"loading payload from NVM...")
        try:
            nvm_offset_payload = self.data['nvm']['payload']['offset']
            nvm_length_payload = self.data['nvm']['payload']['length']
            self.payload = msgpack_unpack(io_BytesIO(microcontroller_nvm[nvm_offset_payload:nvm_offset_payload+nvm_length_payload]))
            if isinstance(self.configuration, dict) is False:
                raise ValueError(f"no payload data in NVM")
            self.data['status']['payload'] = StatusPayload.INSTALLED
            print(f"...successful")
        except Exception as e:
            print(f"...failed ({e})")
            return False
        return True


    def save_payload_nvm(self) -> bool:
        print(f"saving payload to NVM...")
        try:
            nvm_offset_payload = self.data['nvm']['payload']['offset']
            nvm_length_payload = self.data['nvm']['payload']['length']
            payload = io_BytesIO()
            msgpack_pack(self.data['payload'], payload)
            payload = payload.getvalue()
            if len(payload) > nvm_length_payload:
                raise ValueError("configuration too big for NVM configuration area ({len(payload)} bytes > {nvm_length_payload} bytes})")
            microcontroller_nvm[nvm_offset_payload:nvm_offset_payload+len(payload)] = payload
            print(f"...successful")
        except Exception as e:
            print(f"...failed ({e})")
            return False
        return True


    def workflows_load(self):
        if self.configuration is not None:
            self.smm = cp_StateMachineManager()
            try:
                print(f"using workflow configuration from {self.data['configuration']['origin']}")
                for workflow in self.configuration['workflows']:
                    print(f"creating workflow '{workflow['name']}'")
                    sm = self.smm.CreateStateMachine(workflow['name'])
                    for state in workflow['states']:
                        print(f"  adding state '{state['name']}' to workflow '{workflow['name']}'")
                        jobs = Jobs(state['jobs'], self.data)
                        jobs.add(Actions(state['actions'], self.data))
                        sm.AddState(state['name'], jobs.begin, jobs.update, jobs.finish)
                        for transition in state['transitions']:
                            sm.AddTransition(state['name'], Conditions(transition['conditions'], self.data), transition['state'])
                    print(f"  setting initial state '{workflow['initial-state']}' for workflow '{workflow['name']}'")
                    sm.SetState(workflow['initial-state'])
                self.data['status']['runtime'] = StatusRuntime.LOADED
            except Exception as e:
                print(f"Application.run(): {e}")
                traceback_print_exception(e)
                self.data['status']['runtime'] = StatusRuntime.HALTED


    def workflows_run(self):
        if self.data['status']['runtime'] == StatusRuntime.LOADED:
            try:
                self.data['status']['runtime'] = StatusRuntime.RUNNING
                self.test_payload_nvm()
                while True:
                    self.smm.Update()
                    gc_collect()
            except Exception as e:
                print(f"Application.run(): {e}")
                traceback_print_exception(e)
                self.data['status']['runtime'] = StatusRuntime.HALTED

