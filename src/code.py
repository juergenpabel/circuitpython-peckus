from microcontroller import cpu as microcontroller_cpu, \
                            ResetReason as microcontroller_ResetReason
from gc import mem_free as gc_mem_free
from os import getenv as os_getenv
from time import sleep as time_sleep
from traceback import print_exception as traceback_print_exception

from peckus.application import Application
from peckus.workflow.job.led import Job as JobLed
from peckus.workflow.action.ble import Action as ActionBLE
from peckus.workflow.action.system import Action as ActionSystem


if os_getenv('PECKUS_DEBUG', 'FALSE').upper() == 'TRUE':
    ActionSystem('delay', os_getenv('PECKUS_DEBUG_CODEPY_WAIT4SECONDS', '0'), {}).delay()
    ActionSystem('console', os_getenv('PECKUS_DEBUG_CODEPY_WAIT4CONSOLE', 'FALSE'), {}).console()

print(f"code.py: starting (RESET: {str(microcontroller_cpu.reset_reason).split('.').pop()} / RAM: {gc_mem_free()} bytes free)")
looping_led_job = JobLed('red:blink', {'states': [{'RED':'ON', 'millis':250},{'RED':'OFF', 'millis':250}]})
application = Application()
try:
    if application.load_configuration_nvm() is False:
        if application.load_configuration_file() is False:
            looping_led_job = JobLed('green:blink', {'states': [{'GREEN':'ON', 'millis':250},{'GREEN':'OFF', 'millis':250}]})
            raise RuntimeError(f"PECKUS is uninitialized (running regular CIRCUITPY mode for configuration)")
        application.save_configuration_nvm()
        ActionBLE('reset', None, {}).reset()
        ActionSystem('reset', None, {}).reset()
    application.workflows_load()
    print(f"code.py: running (RAM: {gc_mem_free()} bytes free)")
    application.workflows_run()
except RuntimeError as e:
    for arg in e.args:
        print(arg)
except Exception as e:
    print(f"code.py: caught exception {e} (RAM: {gc_mem_free()} bytes free)")
    traceback_print_exception(e)

print(f"code.py: looping (RAM: {gc_mem_free()} bytes free)")
looping_led_job.begin()
while True:
    looping_led_job.update()
    time_sleep(0.01)

