from microcontroller import cpu as microcontroller_cpu, \
                            ResetReason as microcontroller_ResetReason
from supervisor import runtime as supervisor_runtime
from time import sleep as time_sleep
from gc import mem_free as gc_mem_free
from traceback import print_exception as traceback_print_exception

from peckus.application import Application, \
                               ApplicationState
from peckus.workflow.job.led import Job as JobLed


job_blink_led_red   = JobLed('red:blink',   {'states': [{'RED':'ON',   'millis':250}, {'RED':'OFF',   'millis':250}]}, None)
job_blink_led_green = JobLed('green:blink', {'states': [{'GREEN':'ON', 'millis':250}, {'GREEN':'OFF', 'millis':250}]}, None)

g_looping_led_job = job_blink_led_red

try:
    g_application = Application('code.py')
    if g_application.getenv('PECKUS_DEBUG', 'FALSE').upper() == 'TRUE':
        time_sleep(float(g_application.getenv('PECKUS_DEBUG_CODEPY_WAIT4SECONDS', '0')))
        if g_application.getenv('PECKUS_DEBUG_CODEPY_WAIT4CONSOLE', 'FALSE').upper() == 'TRUE':
            while supervisor_runtime.serial_connected is False:
                time_sleep(0.1)

    if g_application.load_configuration_nvm() is False and g_application.load_configuration_file() is False:
        g_looping_led_job = job_blink_led_green
        raise RuntimeError("PECKUS: no valid configuration (NVM & Filesystem) present")

    print(f"code.py: starting (WORKFLOW: {g_application.get_session(ApplicationState.WORKFLOW)} / RESET: {str(microcontroller_cpu.reset_reason).split('.').pop()} / RAM: {gc_mem_free()} bytes free)")
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

