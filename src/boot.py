from microcontroller import cpu as microcontroller_cpu, \
                            ResetReason as microcontroller_ResetReason
from usb_hid import disable as usb_hid_disable
from supervisor import runtime as supervisor_runtime, \
                       set_usb_identification as supervisor_set_usb_identification
from os import getenv as os_getenv
from time import monotonic as time_monotonic
from gc import mem_free as gc_mem_free, \
               collect as gc_collect
from traceback import print_exception as traceback_print_exception

from peckus.application import Application, \
                               ApplicationState
from peckus.workflow.action.peckus import Action as ActionPECKUS
from peckus.util.print import Print


g_print = Print(os_getenv('PECKUS_DEBUG', 'FALSE') == 'TRUE')
print(f"boot.py: starting (RESET: {str(microcontroller_cpu.reset_reason).split('.').pop()} / RAM: {gc_mem_free()} bytes free / TIME: {time_monotonic():.3f})")
try:
    if microcontroller_cpu.reset_reason == microcontroller_ResetReason.POWER_ON:
        if os_getenv('PECKUS_DEBUG', 'FALSE') == 'TRUE':
            if os_getenv('PECKUS_DEBUG_BOOTPY_FACTORYRESET_ON_POWERON', 'FALSE') == 'TRUE':
                ActionPECKUS('factory_reset', None, {}).factory_reset()
    application = Application('boot.py')
    application.set_session(ApplicationState.WORKFLOW, None)
    if application.load_configuration_nvm() is True or application.load_configuration_file() is True:
        supervisor_set_usb_identification(application.getenv('PECKUS_DEVICE_USB_VENDOR', None), \
                                          application.getenv('PECKUS_DEVICE_USB_PRODUCT', None), \
                                          int(application.getenv('PECKUS_DEVICE_USB_VID', '-1'), 16), \
                                          int(application.getenv('PECKUS_DEVICE_USB_PID', '-1'), 16))
        application.workflows_create()
        application.workflows_run()
except Exception as e:
    g_print.enable()
    print(f"PECKUS: exception '{e}'")
    traceback_print_exception(e)
    g_print.disable()

supervisor_runtime.autoreload = False
usb_hid_disable()
gc_collect()
print(f"boot.py: finished (RAM: {gc_mem_free()} bytes free / TIME: {time_monotonic():.3f})")

