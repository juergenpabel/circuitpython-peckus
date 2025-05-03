from microcontroller import ResetReason as microcontroller_ResetReason, \
                            cpu as microcontroller_cpu
from usb_cdc import disable as usb_cdc_disable
from usb_hid import disable as usb_hid_disable
from storage import disable_usb_drive as storage_disable_usb_drive
from os import getenv as os_getenv
from supervisor import runtime as supervisor_runtime
from gc import mem_free as gc_mem_free

from peckus.application import Application
from peckus.workflow.action.nvm import Action as ActionNVM
from peckus.workflow.action.filesystem import Action as ActionFilesystem


print(f"boot.py: starting (RESET: {str(microcontroller_cpu.reset_reason).split('.').pop()} / RAM: {gc_mem_free()} bytes free)")
peckus_debug = True if os_getenv('PECKUS_DEBUG', 'FALSE').upper().strip(' ') == 'TRUE' else False
reset_reason = str(microcontroller_cpu.reset_reason).split('.').pop().upper()

if peckus_debug is False and os_getenv('PECKUS_USB_CONSOLE', 'FALSE').upper().strip(' ') != 'TRUE':
    usb_cdc_disable()
    print(f"PECKUS disabled USB CDC endpoints (check PECKUS_DEBUG & PECKUS_USB_CONSOLE)")

if peckus_debug is False or os_getenv('PECKUS_BLE_CONSOLE', 'FALSE').upper().strip(' ') != 'TRUE':
    supervisor_runtime.ble_workflow = False
    print(f"PECKUS disabled BLE workflow (check PECKUS_DEBUG & PECKUS_BLE_CONSOLE)")

if peckus_debug is True and os_getenv('PECKUS_DEBUG_BOOTPY_FACTORYRESET_ON_POWERON', 'FALSE').upper().strip(' ') == 'TRUE':
    if reset_reason == str(microcontroller_ResetReason.POWER_ON).split('.').pop().upper():
        ActionNVM("erase", None, {}).erase()
        print(f"PECKUS is now factory-resetted") ## (due to PECKUS_DEBUG_FACTORYRESET_ON_POWERON)")

ActionFilesystem("remount", "READWRITE", {}).remount()
ActionFilesystem("file_shred", os_getenv('PECKUS_PAYLOAD_FILENAME'), {}).file_shred()
if Application().test_configuration_nvm() is False or Application().test_payload_nvm() is False:
    ActionFilesystem("remount", "READONLY", {}).remount()
    print(f"{reset_reason}: PECKUS is UNINITIALIZED")
else:
    if reset_reason != str(microcontroller_ResetReason.RESET_PIN).split('.').pop().upper():
        storage_disable_usb_drive()
        print(f"{reset_reason}: PECKUS is now LOCKED")
    else:
        print(f"{reset_reason}: PECKUS is preparing for UNLOCKED (further processing in workflow)")
supervisor_runtime.autoreload = False
usb_hid_disable()
print(f"boot.py: finished (RAM: {gc_mem_free()} bytes free)")

