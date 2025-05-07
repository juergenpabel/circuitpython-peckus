from microcontroller import cpu as microcontroller_cpu, \
                            ResetReason as microcontroller_ResetReason
from gc import mem_free as gc_mem_free
from time import sleep as time_sleep
from traceback import print_exception as traceback_print_exception

from peckus.application import Application
from peckus.workflow.job.led import Job as JobLed
from peckus.workflow.action.ble import Action as ActionBLE
from peckus.workflow.action.system import Action as ActionSystem


g_looping_led_job = JobLed('red:blink', {'states': [{'RED':'ON', 'millis':250},{'RED':'OFF', 'millis':250}]})
g_application = Application()


if g_application.getenv('PECKUS_DEBUG', 'FALSE').upper() == 'TRUE':
    ActionSystem('delay', g_application.getenv('PECKUS_DEBUG_CODEPY_WAIT4SECONDS', '0'), {}).delay()
    ActionSystem('console', g_application.getenv('PECKUS_DEBUG_CODEPY_WAIT4CONSOLE', 'FALSE'), {}).console()

print(f"code.py: starting (RESET: {str(microcontroller_cpu.reset_reason).split('.').pop()} / RAM: {gc_mem_free()} bytes free)")
try:
    if g_application.load_configuration_nvm() is False:
        if g_application.load_configuration_file() is False:
            g_looping_led_job = JobLed('green:blink', {'states': [{'GREEN':'ON', 'millis':250},{'GREEN':'OFF', 'millis':250}]})
            raise RuntimeError(f"PECKUS is uninitialized (running regular CIRCUITPY mode for configuration)")
        g_application.save_configuration_nvm()
        ActionBLE('reset', None, {}).reset()
        ActionSystem('reset', None, {}).reset()

    g_application.workflows_create()
    print(f"code.py: running (RAM: {gc_mem_free()} bytes free)")
    g_application.workflows_run()
except RuntimeError as e:
    for arg in e.args:
        print(arg)
except Exception as e:
    print(f"code.py: caught exception {e} (RAM: {gc_mem_free()} bytes free)")
    traceback_print_exception(e)

print(f"code.py: looping (RAM: {gc_mem_free()} bytes free)")
g_looping_led_job.begin()
while True:
    g_looping_led_job.update()
    time_sleep(0.01)

