from microcontroller import cpu as microcontroller_cpu, \
                            ResetReason as microcontroller_ResetReason
from usb_cdc import disable as usb_cdc_disable
from usb_hid import disable as usb_hid_disable
from storage import disable_usb_drive as storage_disable_usb_drive, \
                    remount as storage_remount
from os import getenv as os_getenv
from supervisor import runtime as supervisor_runtime
from gc import mem_free as gc_mem_free

from peckus.application import Application
from peckus.workflow.action.nvm import Action as NVM
from peckus.workflow.action.storage import Action as Storage


print(f"boot.py: starting (RAM: {gc_mem_free()} bytes free)")
supervisor_runtime.autoreload = False
usb_hid_disable()
peckus_debug = True if os_getenv('PECKUS_DEBUG', 'FALSE').upper().strip(' ') == 'TRUE' else False
peckus_reset_reason = str(microcontroller_cpu.reset_reason).split('.').pop().upper()

if peckus_debug is False and os_getenv('PECKUS_USB_CONSOLE', 'FALSE').upper().strip(' ') != 'TRUE':
    usb_cdc_disable()
    print(f"PECKUS disabled USB CDC endpoints (check PECKUS_DEBUG & PECKUS_USB_CONSOLE)")

if peckus_debug is True and os_getenv('PECKUS_DEBUG_FACTORYRESET_ON_POWERON', 'FALSE').upper().strip(' ') == 'TRUE':
    if peckus_reset_reason == str(microcontroller_ResetReason.POWER_ON).split('.').pop().upper():
        NVM("erase", None, {}).erase()
        print(f"PECKUS erased all NVM contents (check PECKUS_DEBUG_FACTORYRESET_ON_POWERON)")

Storage("remount", "READWRITE", {}).remount()
Storage("wipe", os_getenv('PECKUS_PAYLOAD_FILENAME'), {}).wipe()
if Application().load_configuration_nvm() is True:
    if peckus_reset_reason != str(microcontroller_ResetReason.RESET_PIN).split('.').pop().upper():
        storage_disable_usb_drive()
        print(f"{peckus_reset_reason}: PECKUS is now LOCKED")
    else:
        print(f"{peckus_reset_reason}: PECKUS is preparing for UNLOCKED (further processing in workflow)")
else:
    Storage("remount", "READONLY", {}).remount()
    print(f"{peckus_reset_reason}: PECKUS is UNINITIALIZED")
print(f"boot.py: finished (RAM: {gc_mem_free()} bytes free)")

