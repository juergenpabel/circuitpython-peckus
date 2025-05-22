PECKUS: **P**resence **E**nforcing **C**rypto-**K**ey **U**SB-**S**torage


# tl;dr
A (very small) USB mass-storage device that is only active when you want it to be.

[![PECKUS demo video]](https://github.com/user-attachments/assets/72ebf683-7b52-421f-9b85-f4247cbbd9ef)

A circuitpython program that stores a file (think "kilobytes", presumably some crypto-key) in an internal storage of the microcontroller. To the USB host, it is just a (rather small) USB drive - however, it doesn't expose its storage immediately, but only after the (configurable) presence-enforcing steps have been completed - and than only until the configured relocking criteria are triggered.


# Why?
You might want to store some files ("payload") of yours on a portable device - not because of the portability benefits, but rather for the "air-gap" security benefits while the payload is not being used.

An example of this use-case might be a cryptographic key for (sporadic) message signing/encryption/decryption; for more common applications, there are integration standards for securely storing/using the cryptographic key from a hardware (PKCS11, FIDO2 and such) - but for various application-specific scenarios it's pretty much a password encrypted (if this at least) keyfile stored in the filesystem. Security-conscious users might put such a keyfile on a USB stick in order to minimize the time the keyfile is accessible by the computer.

The previously described scenario is very use-case specific, but exactly the reason why PECKUS was implemented:
1. the target application stores crypto-keys in (password encrypted, at least) files
2. software based disk/file-encryption did not protect against the specific threats identified in our target environment
3. hardware based disk-encryption (encrypted USB-sticks) were a threat-effective measure, but ranged from awful to okay'ish in terms of usability and carried a relevant price tag

Essentially, hardware-encrypted USB sticks that feature unlocking via Bluetooth and/or WIFI were good matches, adressing our core requirements:
1. Protection against unauthorized use of contained payload when the device is lost, stolen or even just left unattended for a while
2. Activation based on user-presence (based on user's Bluetooth and/or WIFI device being in range)
3. Automatic deactivation after either a preconfigurable time, or once the used presence-detection mechanism reports absence (of the user...or at least their Bluetooth/WIFI device) 
4. Ability to "expose" the payload in a read-only mode (for both immutability as well as filesystem integrity reasons)

So I started thinking about what would it take to implement this functionality on an open-source software stack? I quickly determined that micropython/circuitpython running on a mid-sized microcontroller featuring Bluetooth LE should be possible and rather quick to implement. I settled on circuitpython due to the better common baseline support of supported boards (see also section "Hardware" below).


# User journey
The entire user journey consists of four phases (with the first three being the one-time installation/deployment phases):
1. Installation of circuitpython firmware on the board
2. Installation of the PECKUS application on circuitpython
3. Deployment of the payload and (only if configured) pairing of a Bluetooth LE device
∞. Usage (unlocking, accessing the stored file(s), automatic relocking after timeout/user-absence)

Let's assume the (provided) default configuration: unlocking the device is achieved by pushing the button and establishing the Bluetooth LE connection (most likely: a smartphone).

Step 1: CircuitPython (firmware) installation - let's say that has already been completed, okay? Go to https://circuitpython.org/downloads and get a firmware image, install it.

Step 2: Installation of the circuitpython application (PECKUS), just run `install.sh` from the `tools` directory in this repository. Unplug the device thereafter. Done.

Step 3: Plug it back in, it starts blinking its blue LED after about 5-10 seconds - indicating that it is ready for pairing/bonding via Bluetooth LE. Once the pairing is completed, the stick continues with the payload provisioning step (green LED blinks), waiting for you to save your precious data in the file `secret.txt` on the device (or whatever filename was set via `PECKUS_APP_PAYLOAD_FILENAME` in `settings.toml` during step 1). Once the payload file is saved to the device, the device is ready for usage (indicated by a white LED) - just make sure to safely unmount/eject the USB storage to avoid filesystem integrity warnings/errors...this is the last time write-access is possible). Unplug the device.

Step ∞: Plug it in, wait for the red LED to turn on, push the button on the device, wait for the green LED to come on (assuming the bonded BluetoothLE device is nearby). Now your precious file should be accessible (in read-only mode). PECKUS will automatically relock itself after either the preconfigured timeout is hit (`PECKUS_RELOCK_TIMEOUT` and `PECKUS_RELOCK_TIMEOUT_SECS` in `settings.toml`) or the BluetoothLE connection is disconnected (`PECKUS_RELOCK_PRESENCE_BLE` and `PECKUS_RELOCK_PRESENCE_BLE_GRACE_SECS` in `settings.toml`).

**Security warning**: The stock circuitpython firmware has a user-triggerable safe-mode (https://learn.adafruit.com/circuitpython-safe-mode/safemode-py), in which the application code is not run and the filesystem is exposed. If you want to use PECKUS "for real", you should:
1. Install a circuitpython firmware image that was compiled with `CIRCUITPY_SAFEMODE_PY=0`and `CIRCUITPY_SKIP_SAFE_MODE_WAIT=1` (take a look at `tools/build.sh` for that)
2. Disable the circuitpython console (REPL) by setting `PECKUS_CONSOLE_USB` to `FALSE` in `settings.toml`
3. Disable DEBUG mode by setting `PECKUS_DEBUG` to `FALSE` in `settings.toml` (`PECKUS_DEBUG_...` settings are all ignored if `PECKUS_DEBUG` is disabled)
The only way (that I know of) to reset/recover the board after that is if the installed bootloader of the board can be triggered to go into flashing mode (via a quick double-reset on most boards).


# Implementation
This circuitpython application runs two-staged: the first part runs in `boot.py` and configures the storage as to if/how it is exposed via USB as a mass storage device (because `boot.py` is where this needs to be configured: whether the storage should be exposed via USB in read-write, read-only mode or not at all to the host computer). The part of the application that runs as part of `code.py` essentially handles whatever state the application is currently in (configuration, deployment and unlocking/relocking).

All application states are implemented as workflows that run on a (finite-)state-machine; the workflow definitions are stored in a JSON file, which is referenced by the circuitpython configuration setting `PECKUS_APP_CONFIG_FILENAME` (in `settings.toml`). Also note that the application configuration (essentially the workflow definitions plus some configuration values) is copied from the (user-accessible) filesystem to non-volatile-memory (NVM) of the microcontroller as the very first deployment/installation phase. The relevant files (`settings.toml` and `peckus.json` or whatever filename was chosen) are thereafter no longer used - this is both a security measure (to avoid re-configuration after deployment is completed) and a robustness feature (that part of the NVM is not exposed to the USB host computer and thus should be "safe" from any user actions).


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
| PECKUS_APP_CONFIG_FILENAME | peckus.json | PECKUS application logic configuration file (workflow definitions that implement the functionality) |
| PECKUS_APP_PAYLOAD_FILENAME | secret.txt | Your "payload" file, used during deployment to determine that deployment is complete - additional files can be added (best before this one)  |
| PECKUS_UNLOCK_PRESENCE_BTN | TRUE | If a button-click is required as part of the unlocking process, to ensure physical presence |
| PECKUS_UNLOCK_PRESENCE_BTN_VALIDITY_SECS  | 60 | For how long after a button was clicked (only if `PECKUS_UNLOCK_PRESENCE_BTN` is set to `TRUE`) should the presence be considered as given (should not be lower than 10sec if you're using a device whose button is a reset-button) |
| PECKUS_UNLOCK_PRESENCE_BLE | FALSE | If a bluetooth connection to a bonded device (bonding occurs during deployment) is required as part of the unlocking process, ensuring the user (not anyone just clicking the button) is physically present |
| PECKUS_UNLOCK_PRESENCE_BLE_VALIDITY_SECS  | 60 | For how long after a bluetooth connection was established (only if `PECKUS_UNLOCK_PRESENCE_BLE` is set to `TRUE`) should the bluetooth presence be considered as given (should not be lower than 10sec if you're using a device whose button is a reset-button) |
| PECKUS_RELOCK_TIMEOUT | TRUE | Whether a maximum time in unlocked state should be enfored |
| PECKUS_RELOCK_TIMEOUT_SECS | 300 | The maximum time (only if `PECKUS_RELOCK_TIMEOUT` is set to `TRUE`), after which the device relocks itself after being unlocked |
| PECKUS_RELOCK_PRESENCE_BLE | FALSE | Whether the presence of the bonded bluetooth device should be enfored in unlocked state |
| PECKUS_RELOCK_PRESENCE_BLE_GRACE_SECS  | 15 | the meximum time during which the bluetooth connection might be disconnected before relocking (only if `PECKUS_RELOCK_PRESENCE_BLE` is set to `TRUE`) |
| PECKUS_DEVICE_USB_VENDOR | CIRCUITPYTHON | Vendor description for USB device identification |
| PECKUS_DEVICE_USB_PRODUCT | PECKUS | Product description for USB device identification |
| PECKUS_DEVICE_USB_VID | 239A | Vendor ID for USB device identification (hex number) |
| PECKUS_DEVICE_USB_PID | 2025 | Product ID for USB device identification (hex number) |
| PECKUS_DEVICE_BLE_NAME | PECKUS | Name for Blueooth device identification |
| PECKUS_CONSOLE_USB | FALSE | Whether to expose a serial endpoint via USB (allowing connections to circuitpython console/REPL...a major security loophole, but great for testing) |
| PECKUS_DEBUG | FALSE | Whether to activate debug mode (other `PECKUS_DEBUG_...` settings are evaluated only if `PECKUS_DEBUG`is set to `TRUE`) |
| PECKUS_DEBUG_BOOTPY_FACTORYRESET_ON_POWERON | FALSE | Whether to factory-reset the device upon power-on (plugging it in), great for testing purposes |
| PECKUS_DEBUG_CODEPY_WAIT4CONSOLE | FALSE | Whether the application code (`code.py`) should wait for a connection to the console/REPL before continuing, great for testing purposes |
Please note that all settings should be set as TOML strings, validation of and conversion to target types (boolean, integer, hexadecimal, string) are implemented in the application. Use all-upper-case letters for strings used as booleans (`TRUE` or `FALSE`) |

# Reference: LED codes (for default PECKUS workflow)
The following table lists the LED codes implemented in the default PECKUS workflows (and in code.py for two specific error cases). `ON` and `OFF` should be obvious, `FAST` means 2 blinking cycles per seconds and `SLOW` means 1 blinking cycle per second. Please not that two slow blinking cycles can be combined, then the LED color alternates between those two colors.

| RED   | GREEN | BLUE  | Status |
| ----- | ----- | ----- | ------ |
| OFF   | OFF   | OFF   | Circuitpython is either currently loading/starting (should be no more than 5 seconds), or PECKUS is not installed - or something has gone horribly wrong (please report a bug) |
| FAST  | OFF   | OFF   | This indicates an error: PECKUS has terminated - please file a bug report with as much context information as possible (which lifecycle phase, ...) |
| OFF   | FAST  | OFF   | This indicates an error during deployment (the configuration has not yet imported into NVM): the configuration (peckus.json?) could not be loaded; the USB storage should be read-write accessible |
| OFF   | OFF   | FAST  | Not (yet?) used | 
| ON    | OFF   | OFF   | PECKUS is active (and locked): it is waiting for a button-press to continue in the unlocking workflow |
| OFF   | ON    | OFF   | PECKUS is active (and unlocked): the USB storage (including the payload file) should be read-only accessible |
| OFF   | OFF   | ON    | Not (yet?) used |
| SLOW  | OFF   | OFF   | Not (yet?) used |
| OFF   | SLOW  | OFF   | Only during deployment (configuration has been imported into NVM): Waiting for the payload file (`secret.txt` in the default configuration, see `settings.toml`) to be saved on the USB storage (read-write mode) |
| OFF   | OFF   | SLOW  | Only during deployment (configuration has been imported into NVM) and with BLE presences configured: Waiting for BLE pairing - pair your bluetooth device to continue | 
| ON  | OFF   | ON  | (results in purple on most boards) PECKUS is active (and locked): the BLE connection has been established (as part of the unlocking process), but a button-click has to be done for unlocking to occur |
| OFF   | SLOW  | SLOW  | PECKUS is active (and unlocked): the BLE device has disconnected, the grace period (15 seconds by default) is active - reconnect quickly or wait for relocking to occur |
| SLOW   | SLOW  | OFF  | PECKUS is active (and unlocked): this is a user "notice": the maximum unlocking timeout is approaching (less than 15 seconds remaining by default) - prepare for device going into locked state |


# Security assumptions and goals
Foremost: PECKUS **does not encrypt** any data at all. It is not an encrypted USB drive, the project name implies that (most likely) a crypto-key can be stored on the device. There are three reasons why encryption has not been implemented:
1. There is no support for (really) securely storing cryptographic key material in circuitpython. All data (inlcuding the small filesystem) is stored inside the microcontroller in non-volatile-memory (NVM), any encryption/decryption keys would therefore have to be stored "right next" to the encrypted data.
2. Cryptographic keys need to be generated randomly/unpredictably ("entropy"), but circuitpython doesn't provide any entropy sources.
3. Always encrypting/decrypting data upon unlocking/relocking introduces an additional risk for failure (filesystem integrity, ...)
What PECKUS does is to restrict access to the stored file(s) by means of verification steps regarding user presence (make sure to follow the steps detailed in the security warning in the 'User journey' section above). 

Security assumptions/limits:
1. When storing your precious data (key files?) on a PECKUS device, you have wheighted the risks and benefits - the (new) risk of losing the device or having it stolen (vs. the same but for your computer), the risk of the device not working anymore (store a backup copy of your data somewhere safe!) and also: if you're using the Bluetooth-feature (you really should, otherwise anyone in possesion of the stick can unlock it): what if your bonded device (smartphone?) is lost/stolen - or even if by "fat-fingering" the BluetoothLE bonding is reset)?
2. You aren't looking to protect your data from resourceful/capable attackers - the probably easiest way to get your data is to unsolder the microcontroller (and thus the NVM) and than extract the NVM data.
3. You (or in the context of a club/organisation/company: other people) are not side-stepping this "solution" by copying the contained files off of PECKUS onto the computer - this can't be prevented (by concept/design) and thus, it must be in the interest of the user to actually go through the (albeit small) hassle of using this "solution".

Security goals (constrained by the aforementioned assumptions/limits):
1. Prevent access to the payload (files) stored in PECKUS, unless the configured unlocking steps are successfully completed.
2. Enforcement of re-locking criteria when PECKUS is unlocked.
3. Prevent modifications of the application, its configuration or the contained payload (files) after deployment has completed.

# Developer guidance
TODO (probably something for the wiki)

