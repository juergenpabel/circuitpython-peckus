PECKUS: **P**resence **E**nforcing **C**rypto-**K**ey **U**SB-**S**torage


# tl;dr
A (very small) USB mass-storage device that is only active when you want it to be.

A circuitpython program that stores a bit of data (only a few kilobytes, presumably some crypto-key) in an internal storage (non-volatile-memory) of the microcontroller. To the USB host, it is just a (rather small) USB drive - however, it doesn't expose its storage immediately, but only after the (configurable) presence-enforcing steps have been completed - and than only until the configured relocking criteria are triggered.

# Why?
You might want to store some crypto-key ("payload") of yours on a portable device - not because of the portability benefits, but rather for the "air-gap" security benefits while the payload is not being used.

An example of this use-case might be a cryptographic key for (sporadic) message signing/encryption/decryption; for more common applications, there are integration standards for securely storing/using the cryptographic key from a hardware (PKCS11, FIDO2 and such) - but for various application-specific scenarios it's pretty much a password encrypted (if this at least) keyfile stored in the filesystem. Security-conscious users might put such a keyfile on a USB stick in order to be able to minimize the time the keyfile is accessible by the computer (and this might even be users that are remotely connecting to that computer). 

The previously described scenario is very use-case specific, but exactly the reason why PECKUS was implemented:
1. software based disk/file-encryption did not protect against the specific threats identified in our target environment
2. hardware based disk-encryption (encrypted USB-sticks) were a threat-effective measure, but ranged from awful to okay'ish in terms of usability and carried a relevant price tag

Essentially, hardware-encrypted USB sticks that feature unlocking via Bluetooth and/or WLAN were good matches, adressing our core requirements:
1. Protection against unauthorized use of contained payload when the device is lost or stolen (at least for untargeted scenarios)
2. Activation based on user-presence (based on user's Bluetooth and/or WLAN device being in range)
3. Automatic deactivation after either a preconfigured time, or once the used presence-detection mechanism reports absence (of the user...or at least their Bluetooth/WLAN device) 
4. Ability to "expose" the payload in a read-only mode (for both immutability as well as filesystem integrity reasons)

So I started thinking about what would it take to implement these requirements on an open-source software stack? I quickly determined that micropython/circuitpython running on a mid-sized microcontroller featuring Bluetooth LE should be possible and rather quick to implement. I settled on circuitpython due to the better common baseline support of supported boards (see also section "Hardware" below).


# User journey
The entire user journey consists of three phases (with the first two being the one-time installation/deployment phases):
1. Installation of circuitpython and PECKUS
2. Deployment of the payload and (only if configured) pairing of a Bluetooth LE device
3. Usage (unlocking, payload usage, relocking after timeout/user-absence)

Let's assume the provided default configuration: unlocking the device is done by first pushing the button and than establishing the Bluetooth LE connection with the paired device (most likely: a smartphone).

First off: CircuitPython (firmware) installation - let's say that has already been completed, okay? Next up (in the first phase): installation of the circuitpython application (PECKUS), just run `install.sh` from the `tools` directory in this repository. Unplug the device thereafter. Done.

Now for the deployment/provisioning phase: Plug it back in, it starts blinking its blue LED after about 10-15 seconds - indicating that it is ready for pairing/bonding via Bluetooth LE. Once the pairing is completed, the stick continues with the payload provisioning step (green LED blinks), waiting for you to save your precious data in the file `secret.txt` on the device (or whatever filename was set via `PECKUS_APP_PAYLOAD_FILENAME` in `settings.toml` during phase 1). Once the payload file is saved to the device, its contents are copied to NVM, the file is deleted and the device resets and (from than on always) enters phase 3 (usage).

Now for the usage phase: Wait for the red LED to turn on, push the (reset-)button on the device, wait for the red-blue blinking LEDs to come on, make sure your Bluetooth device makes the connection (should happen automatically for Android & Apple devices) and wait for the green LED. Now your precious `secret.txt` should be (read-only) accessible via USB.

**Important**: The default configuration has DEBUG settings activated - PECKUS factory resets its (internal) configuration whenever it is plugged into an USB port (circuitpython reports this as power-on). The intention for this default configuration is to eliminate any risk of unintentionally bricking the device when evaluating different configuration/workflow settings. 


# Implementation
This circuitpython application runs two-staged: the first part runs in `boot.py` and configures the storage as to if/how it is exposed via USB as a mass storage device (because `boot.py` is where this needs to be configured: whether the storage should be exposed via USB in read-write, read-only mode or not at all to the host computer). The part of the application that runs as part of `code.py` essentially handles whatever state the application is currently in (like initialization, deployment and regular usage).

With the exception of the initial configuration phase, all application states are implemented as workflows that run on a (finite-)state-machine; the workflow definition is stored in a JSON file, which is referenced by the circuitpython configuration key `PECKUS_APP_CONFIG_FILENAME` (in `settings.toml`). Also note that the application configuration (essentially the workflow definitions plus some configuration values) is copied from the (user-accessible) filesystem to non-volatile-memory (NVM) of the microcontroller as the very first deployment/installation phase. The relevant files (`settings.toml` and `peckus.json` or whatever filename was chosen) are thereafter no longer used - this is both a security measure (to avoid re-configuration after deployment is completed) and a robustness feature (the NVM is not exposed to the USB host computer and thus should be "safe" with respect to user actions).


# Hardware
PECKUS was developed on and for the [nRF52840 Micro Dev Kit USB Dongle by MakerDiary](https://circuitpython.org/board/makerdiary_nrf52840_mdk_usb_dongle/):

![nRF52840 Micro Dev Kit USB Dongle by MakerDiary](https://circuitpython.org/assets/images/boards/small/nRF52840_micro_dev_kit_usb_dongle.jpg)

Please note that [Makerdiary also sell this board with a case](https://makerdiary.com/products/nrf52840-mdk-usb-dongle-w-case), so it looks and feels just as one would expect from a commercial product.

As a circuitpython application, PECKUS should run on any supported board with circuitpython support for:
1. USB device operations (for exposing its storage as a USB mass-storage device) - especially ESP32 pre-S3 boards lack this capability
2. An internal non-volatile-memory (NVM), exposed by circuitpython as `microcontroller.nvm`, with at least 8KB - this should be available on all but the smallest boards

Obviously, for Bluetooth LE based presence-detection the board must support Bluetooth LE (BLE presence detection can be disabled by setting `PECKUS_UNLOCK_PRESENCE_BLE` to `FALSE` in `settings.toml` before deployment).

Another hardware dependency are the LED indicators, the current implementation uses the `board.LED_RED`, `board.LED_GREEN` and `board.LED_BLUE` objects - if they are not present the code will still run fine (exception handling, see `src/lib/workflow/job/led.py`), just without any LED indications.


# Installation and deployment
Files from this repository can be copied manually onto a CIRCUITPY drive (an already active circuitpython device), just copy the CIRCUITPY directory in this repository (copy with resolving symlinks though) and unmount the device, than un- and re-plug it. As an alternative, there is an installations script (`tools/install.sh`) - it will also copy those files but will also first create a new FAT12 filesystem on the device for a clean and known device baseline.

Now the deployment begins: PECKUS loads the workflow configuration (as per `PECKUS_APP_CONFIG_FILENAME` in `settings.toml`), does parameter evaluation (see `parameter` section in the workflow file) and copies it to the NVM. If this is successful, it restarts and starts the provisioning steps (BLE pairing and putting the payload file on the device). Once that's completed, it restarts and enters the usage phase/workflows.

**Important**: The default configuration (`settings.toml`) has DEBUG settings activated, the most relevant implications:
- `PECKUS_DEBUG_BOOTPY_FACTORYRESET_ON_POWERON` is set to `TRUE`, therefore any unplugging of the device will reset the PECKUS configuration upon next power-on of the device (it will essentially erase all NVM data and thus be in the uninitialized state again); this is on purpose for evluation/testing purposes - for "production" usage, you'd would most likely change some parameters or even workflow logic anyhow.
- `PECKUS_CONSOLE_USB` is activated (`TRUE`), so a connection to circuitpython console/REPL is possible - it is therefore possible to manipulate the device/application even once fully deployed (usage phase)


# Reference: settings.toml (for the default PECKUS configuration)
The following table lists all implemented settings (as in entries in `settings.toml`), their default values and some explanations.
| Setting | Default value | Details |
| ------- | ------------- | ------- |
| PECKUS_APP_CONFIG_FILENAME | peckus.json | TODO |
| PECKUS_APP_PAYLOAD_FILENAME | secret.txt | TODO |
| PECKUS_UNLOCK_PRESENCE_BTN | TRUE | TODO |
| PECKUS_UNLOCK_PRESENCE_BLE | FALSE | TODO |
| PECKUS_UNLOCK_PRESENCE_BLE_CONNECT_SECS  | 60 | TODO |
| PECKUS_RELOCK_DURATION_SECS | 300 | TODO |
| PECKUS_RELOCK_PRESENCE_BLE_RECONNECT_SECS  | 15 | TODO |
| PECKUS_DEVICE_USB_VENDOR | CIRCUITPYTHON | TODO |
| PECKUS_DEVICE_USB_PRODUCT | PECKUS | TODO |
| PECKUS_DEVICE_USB_VID | 239A | TODO |
| PECKUS_DEVICE_USB_PID | 2025 | TODO |
| PECKUS_DEVICE_BLE_NAME | PECKUS | TODO |
| PECKUS_CONSOLE_USB | FALSE | TODO |
| PECKUS_DEBUG | FALSE | TODO |
| PECKUS_DEBUG_BOOTPY_FACTORYRESET_ON_POWERON | FALSE | TODO |
| PECKUS_DEBUG_CODEPY_WAIT4CONSOLE | FALSE | TODO |
| PECKUS_DEBUG_CODEPY_WAIT4SECONDS | 0 | TODO |
Please note that all settings should be set as TOML strings, validation of and conversion to target types (boolean, integer, hexadecimal, string) are implemented in the application.

# Reference: LED codes (in default PECKUS configuration)
The following table lists the LED codes implemented in the default PECKUS workflows (and code.py for two error cases). `ON` and `OFF` should be obvious, `FAST` means 2 blinking cycles per seconds and `SLOW` means 1 blinking cycle per second. Please not that two slow blinking cycles can be combined, then it is 1 (full) blinking cycle every 2 seconds.

| RED   | GREEN | BLUE  | Status |
| ----- | ----- | ----- | ------ |
| OFF   | OFF   | OFF   | Circuitpython is either currently loading/starting (should be no more than 5 seconds), PECKUS is not installed - or something has gone horribly wrong (please report a bug) |
| FAST  | OFF   | OFF   | This indicates an error, the PECKUS application has terminated - please file a bug report with as much context information as possible (which lifecycle phase, ...) |
| OFF   | FAST  | OFF   | Only during deployment (configuration not yet imported into NVM): the configuration (peckus.json?) could not be loaded; the USB storage should be read-write accessible |
| OFF   | OFF   | FAST  | Not yet used | 
| ON    | OFF   | OFF   | PECKUS is active (and locked): it is waiting for a button-press to continue in the unlocking workflow |
| OFF   | ON    | OFF   | PECKUS is active (and unlocked): the USB storage (including the payload file) should be read-only accessible |
| OFF   | OFF   | ON    | PECKUS is active: the BLE connection is established, the next state should be upcoming shortly |
| SLOW  | OFF   | OFF   | Not yet used |
| OFF   | SLOW  | OFF   | Only during deployment (configuration has been imported into NVM): Waiting for the payload file (`secret.txt` in the default configuration, see `settings.toml`) to be saved on the USB storage (read-write mode) |
| OFF   | OFF   | SLOW  | Only during deployment (configuration has been imported into NVM) and with BLE presences configured: Waiting for BLE pairing - pair your personal device to continue | 
| SLOW  | OFF   | SLOW  | PECKUS is active (and locked): the BLE connection has not been established (as part of the unlocking process) |
| OFF   | SLOW  | SLOW  | PECKUS is active (and unlocked): the BLE device has disconnected, the grace period (15 seconds by default) is active - reconnect quickly or wait for relocking to occur |


# Security targets and assumptions
TODO

# Developer guidance
TODO

