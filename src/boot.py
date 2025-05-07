from microcontroller import ResetReason as microcontroller_ResetReason, \
                            cpu as microcontroller_cpu
from usb_cdc import disable as usb_cdc_disable
from usb_hid import disable as usb_hid_disable
from storage import disable_usb_drive as storage_disable_usb_drive
from supervisor import runtime as supervisor_runtime
from gc import mem_free as gc_mem_free, \
               collect as gc_collect

from peckus.application import Application
from peckus.workflow.action.filesystem import Action as ActionFilesystem


print(f"boot.py: starting (RESET: {str(microcontroller_cpu.reset_reason).split('.').pop()} / RAM: {gc_mem_free()} bytes free)")
application = Application()
application.load_configuration_nvm() 
reset_reason = str(microcontroller_cpu.reset_reason).split('.').pop()

if application.getenv('PECKUS_DEBUG', 'FALSE').upper() == 'TRUE' and application.getenv('PECKUS_DEBUG_BOOTPY_FACTORYRESET_ON_POWERON', 'FALSE').upper() == 'TRUE':
    if reset_reason == str(microcontroller_ResetReason.POWER_ON).split('.').pop():
        application.factory_reset()
        print(f"PECKUS is now factory-resetted")

if application.getenv('PECKUS_CONSOLE_USB', 'FALSE').upper() != 'TRUE':
    usb_cdc_disable()
    print(f"PECKUS disabled USB console")

ActionFilesystem("remount", "READWRITE", {}).remount()
ActionFilesystem("file_shred", application.getenv('PECKUS_PAYLOAD_FILENAME'), {}).file_shred()
if application.getenv('PECKUS_FILESYSTEM_KEEP_CONFIG_JSON', 'TRUE').upper() != 'TRUE':
    ActionFilesystem("file_shred", application.getenv('PECKUS_CONFIG_FILENAME'), {}).file_shred()
if application.getenv('PECKUS_FILESYSTEM_KEEP_SETTINGS_TOML', 'TRUE').upper() != 'TRUE':
    ActionFilesystem("file_shred", 'settings.toml', {}).file_shred()

if application.test_configuration_nvm() is False or application.test_payload_nvm() is False:
    ActionFilesystem("remount", "READONLY", {}).remount()
    print(f"PECKUS is UNINITIALIZED")
else:
    if application.getenv('PECKUS_UNLOCK_PRESENCE_BLE', 'FALSE').upper() == 'TRUE':
        supervisor_runtime.ble_workflow = True
    if reset_reason != str(microcontroller_ResetReason.RESET_PIN).split('.').pop():
        storage_disable_usb_drive()
        print(f"PECKUS is now LOCKED")
    else:
        print(f"PECKUS is preparing for UNLOCKED (further processing in workflow)")
supervisor_runtime.autoreload = False
usb_hid_disable()
gc_collect()
print(f"boot.py: finished (RAM: {gc_mem_free()} bytes free)")

