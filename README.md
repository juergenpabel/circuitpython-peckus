PECKUS: **P**resence **E**nforcing **C**rypto-**K**ey **U**SB-**S**torage

# tl;dr
A circuitpython program that stores a bit of data (only a few kilobytes, presumably some crypto-key) in an internal storage (non-volatile-memory) of the microcontroller. When the microcontroller is attached to a USB port some presence-verifying steps have to be completed (those can be configured during installation) for the microcontroller to expose its filesystem to the USB host - thus allowing (read-only) access to the data. To the USB host, it is just a (rather small) USB drive - but it doesn't expose its storage immediately, but only after the (configured) presence-enforcing checks have been completed by the user.

# Why?
You might want to store some crypto-key ("payload") of yours on a portable device - not because of the portability benefits, but rather for the "air-gap" security benefits while the payload is not being used.

An example of this use-case might be a cryptographic key for (sporadic) message signing/encryption/decryption; for more common applications, there are integration standards for securely storing/using the cryptographic key from a hardware (PKCS11, FIDO2 and such) - but for various application-specific scenarios it's pretty much a password encrypted (if this at least) keyfile stored in the filesystem. Security-conscious users might put such a keyfile on a USB stick in order to be able to minimize the time the keyfile is accessible by the computer (and thus any potentially present malware). 

The previously described scenario is very use-case specific, but exactly the reason why PECKUS was implemented:
1. software based disk/file-encryption did not protect against the specific threats identified in our target environment
2. hardware based disk-encryption (encrypted USB-sticks) are a threat-effective measure, but ranged from awful to OKayish in terms of usability and carried a hefty price tag

Essentially, hardware-encrypted USB sticks that feature unlocking via Bluetooth/WLAN were good matches, adressing our core requirements:
1. Protection against unauthorized use of contained payload after loss/theft
2. Activation based on user-presence (based on user's Bluetooth/WLAN devices being in range)
3. Automatic deactivation after either a preconfigured time, or once the used presence-detection mechanism reports absence (of the user...or at least their Bluetooth/WLAN device) 
4. Ability to "expose" the payload in a read-only mode (for both immutability as well as filesystem integrity reasons)

So I started thinking about what would it take to implement these requirements on an open-source software stack? I quickly determined that micropython or circuitpython running on a mid-sized microcontroller featuring Bluetooth (LE?) should be possible and rather quick to implement (when compared to C/C++ with platformio/arduino).

# Concept

The lifecycle consists most likely of three phases:
1. Installation of circuitpython and peckus
2. Deployment of payload (and if Bluetooth LE presence is configured: pairing of Bluetooth LE device)
3. Usage (unlocking phase, payload usage, relocking after timeout/user-absence)

Essentially, the first phase can be anything from simply running a (provided) installation-script up to changes of workflow logic - so we'll skip this here (and refer you to the wiki for more information).

For the second and third phase in this context let's assume the default configuration: presence enforcement via button push and Bluetooth connectivity. Once the user plugs in the stick, it starts blinking its blue LED - indicating to the user that it is waiting for a pairing/bonding with a device by the user. Once the pairing completed, the stick restarts in payload provisioning mode (green LED blinks), waiting for the user to save a '/secret.txt' file (or whatever filename was set in settings.toml at installation time). Once the payload file is detected, its contents are saved to NVM, the file is deleted and the device enters phase 3 (usage).

Upon plugging in (reported as reset reason `POWER_ON` by circuitpython) the device is locked and waits for a reset via its reset button (user presence, part 1) - thereafter it waits for a bluetooth connection from the paired device; if the connections isn't established within a certain time (15 seconds by default), it resets and another button-press would be required. If the connection is established, the payload file is written to the storage (and thus exposed to the USB host computer, in read-only mode). This state remains until either the relocking timeout triggers or the bluetooth connections is lost beforehand (unless it is restored within a grace period, 15 seconds by default).

# Implementation

This circuitpython application runs two-staged: the first part runs in boot.py and configures the storage as to if/how it is exposed via USB as a mass storage device (because boot.py is where this needs to be configured: whether the storage should be exposed via USB in read-write, read-only mode or not at all to the host computer). The part of the application that runs as part of code.py essentially handles whatever state the application is currently in (like initialization, deployment and regular usage).

With the exception of the initial configuration phase, all application states are implemented as workflows that run on a (finite-)state-machine; the workflow definition is stored in a JSON file, which is referenced by the circuitpython configuration key `PECKUS_CONFIG_FILENAME` (in settings.toml). Also note that the application configuration (essentially the workflow definitions plus some configuration values) is copied from the (user-accessible) filesystem to non-volatile-memory (NVM) of the microcontroller as the very first deployment/installation phase. The relevant files (settings.toml and peckus.json) are thereafter no longer used - this is both a security measure (to avoid re-configuration after deployment is completed) and a robustness feature (the NVM is not exposed to the USB host computer and thus should be "safe" with respect to user actions).

# Security targets and assumptions

TODO

# Installation and deployment

TODO

# Reference: LED codes in default workflow definitions

TODO

# Developer guidance

TODO

