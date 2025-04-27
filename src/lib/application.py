from microcontroller import nvm as microcontroller_nvm
from os import getenv as os_getenv
from io import BytesIO as io_BytesIO
from msgpack import unpack as msgpack_unpack, \
                    pack as msgpack_pack
from json import load as json_load
from re import match as re_match
from traceback import print_exception as traceback_print_exception

from cpstatemachine import StateMachineManager as cp_StateMachineManager

from peckus.workflow.transitionconditions import TransitionConditions
from peckus.workflow.transitionactions import TransitionActions


class OriginConfiguration():
    FILE = 'FILE'
    NVM  = 'NVM'

class StatusRuntime():
    UNINITIALIZED = 'UNINITIALIZED'
    INITIALIZED   = 'INITIALIZED'
    CONFIGURED    = 'CONFIGURED'
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
        self.data['configuration'] = {}
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
        result = False
        try:
            with open(configuration_filename, 'r') as f:
                self.configuration = json_load(f)
            if isinstance(self.configuration, dict) is False:
                print(f"...failed (json error in '{configuration_filename}')")
            else:
                self.data['configuration']['origin'] = OriginConfiguration.FILE
                result = True
                print(f"...successful")
        except Exception as e:
            print(f"...failed (exception: {e})")
        return result


    def parse_configuration(self) -> None:
        if self.data['configuration']['origin'] == OriginConfiguration.FILE:
            if 'parameters' not in self.configuration:
                self.configuration['parameters'] = {}
            parameters = self.configuration['parameters']
            for key, value in parameters.copy().items():
                matches = re_match(r'^\$([A-Z_]+)=(.*)$', value)
                if matches is not None:
                    matches = matches.groups()
                    value = os_getenv(matches[0])
                    if value is None:
                        value = matches[1]
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
                        raise ValueError(f"Missing name for state in workflow '{workflow['name']}'")
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
        self.data['status']['runtime'] = StatusRuntime.CONFIGURED


    def load_configuration_nvm(self) -> bool:
        print(f"loading configuration from NVM...")
        result = False
        try:
            nvm_offset_configuration = self.data['nvm']['config']['offset']
            nvm_length_configuration = self.data['nvm']['config']['length']
            self.configuration = msgpack_unpack(io_BytesIO(microcontroller_nvm[nvm_offset_configuration:nvm_length_configuration]))
            if isinstance(self.configuration, dict) is False:
                microcontroller_nvm[0] = 0x00
                print(f"...failed (data inconsistency, cleared NVM)")
            else:
                self.data['status']['runtime'] = StatusRuntime.CONFIGURED
                self.data['configuration']['origin'] = OriginConfiguration.NVM
                result = True
                print(f"...successful")
        except Exception as e:
            print(f"...failed (exception: {e})")
        return result


    def save_configuration_nvm(self) -> bool:
        print(f"saving configuration to NVM...")
        result = False
        try:
            data = io_BytesIO()
            msgpack_pack(self.configuration, data)
            data = data.getvalue()
            nvm_offset_configuration = self.data['nvm']['config']['offset']
            nvm_length_configuration = self.data['nvm']['config']['length']
            if len(data) <= nvm_length_configuration:
                microcontroller_nvm[nvm_offset_configuration:nvm_offset_configuration+len(data)] = data
                result = True
                print(f"...successful")
            else:
                print(f"...failed due to size ({len(data)} bytes, NVM configuration area is only {nvm_length_configuration} bytes)")
        except Exception as e:
            print(f"...failed (exception: {e})")
        return result


    def test_payload_nvm(self) -> bool:
        print(f"testing if payload is stored in NVM...")
        result = False
        try:
            nvm_offset_payload = self.data['nvm']['payload']['offset']
            nvm_length_payload = self.data['nvm']['payload']['length']
            msgpack_unpack(io_BytesIO(microcontroller_nvm[nvm_offset_payload:nvm_offset_payload+nvm_length_payload]))
            self.data['status']['payload'] = StatusPayload.INSTALLED
            result = True
            print(f"...successful")
        except Exception as e:
            print(f"...failed (exception: {e})")
        return result


    def save_payload_nvm(self) -> bool:
        print(f"saving payload to NVM...")
        result = False
        try:
            nvm_offset_payload = self.data['nvm']['payload']['offset']
            nvm_length_payload = self.data['nvm']['payload']['length']
            payload = io_BytesIO()
            msgpack_pack(self.data['payload'], payload)
            payload = payload.getvalue()
            if len(payload) <= nvm_length_payload-2:
                microcontroller_nvm[nvm_offset_payload:nvm_offset_payload+len(payload)] = payload
                result = True
                print(f"...successful")
            else:
                print(f"...failed due to size ({len(payload)} bytes, NVM payload area is only {nvm_length_payload} bytes)")
        except Exception as e:
            print(f"...failed (exception: {e})")
        return result


    def run(self):
        if self.configuration is not None:
            smm = cp_StateMachineManager()
            try:
                for workflow in self.configuration['workflows']:
                    print(f"creating workflow '{workflow['name']}'")
                    sm = smm.CreateStateMachine(workflow['name'])
                    for state in workflow['states']:
                        print(f"  adding state '{state['name']}' to workflow '{workflow['name']}'")
                        sm.AddState(state['name'], TransitionActions(state['actions'], self.data))
                    print(f"  setting initial state '{workflow['initial-state']}' for workflow '{workflow['name']}'")
                    sm.SetState(workflow['initial-state'])
                    for state in workflow['states']:
                        for transition in state['transitions']:
                            sm.AddTransition(state['name'], TransitionConditions(transition['conditions'], self.data), transition['state'])
                self.data['status']['runtime'] = StatusRuntime.RUNNING
                print(f"executing workflows...")
                while True:
                    smm.Update()
            except Exception as e:
                print(f"Application.run(): {e}")
                traceback_print_exception(e)
                self.data['status']['runtime'] = StatusRuntime.HALTED

