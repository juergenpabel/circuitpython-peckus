from gc import mem_free as gc_mem_free
from os import getenv as os_getenv
from time import sleep as time_sleep
from traceback import print_exception as traceback_print_exception

from peckus.application import Application, StatusRuntime
from peckus.workflow.action.board import Action as ActionBoard
from peckus.workflow.action.system import Action as ActionSystem


if os_getenv('PECKUS_DEBUG', 'FALSE').upper().strip(' ') == 'TRUE':
    ActionSystem('delay', os_getenv('PECKUS_DEBUG_DELAY', ''), {}).delay()

print(f"code.py: starting (RAM: {gc_mem_free()} bytes free)")
application = Application()
halting_board_led_on  = ActionBoard('led', 'RED:ON',  application.data)
halting_board_led_off = ActionBoard('led', 'RED:OFF', application.data)
try:
    if application.load_configuration_nvm() is True:
        application.test_payload_nvm()
    else:
        if application.load_configuration_file() is True:
            application.parse_configuration()
            application.save_configuration_nvm()
        else:
            halting_board_led_on  = ActionBoard('led', 'GREEN:ON',  application.data)
            halting_board_led_off = ActionBoard('led', 'GREEN:OFF', application.data)
    print(f"code.py: running (RAM: {gc_mem_free()} bytes free)")
    application.run()
except Exception as e:
    print(f"code.py: caught exception: {e} (RAM: {gc_mem_free()} bytes free)")
    traceback_print_exception(e)

print(f"code.py: halting (RAM: {gc_mem_free()} bytes free)")
while True:
    halting_board_led_on.led()
    time_sleep(0.5)
    halting_board_led_off.led()
    time_sleep(0.5)

