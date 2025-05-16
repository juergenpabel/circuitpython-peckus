#!/bin/bash

PECKUS_GIT_DIR=`git rev-parse --show-toplevel`

CIRCUITPY_DEVICE=${1:-/dev/sda1}
CIRCUITPY_MOUNT=${2:-/media/${USERNAME}/PECKUS}
CIRCUITPY_DIR=${CIRCUITPY_DIR:-${PECKUS_GIT_DIR}/CIRCUITPY}


USER_UID=`id -u ${USERNAME}`
USER_GID=`id -g ${USERNAME}`


if [ ! -b "${CIRCUITPY_DEVICE}" ]; then
	echo "ERROR: device '${CIRCUITPY_DEVICE}' doesn't exist, please specify device-filename as first parameter (/dev/sda1 is default if not provided)"
	exit 1
fi

echo "PECKUS-INSTALL: unmounting '${CIRCUITPY_DEVICE}'"
sudo umount -q "${CIRCUITPY_DEVICE}"
echo "PECKUS-INSTALL: creating FAT-filesystem on '${CIRCUITPY_DEVICE}'"
sudo mkfs.vfat -g 255/63 -S 512 -s 1 -F 12 -f 1 -n PECKUS -I "${CIRCUITPY_DEVICE}" >/dev/null
if [ $? -ne 0 ]; then
	echo "ERROR mkfs.vfat"
	exit 1
fi

if [ ! -d "${CIRCUITPY_MOUNT}" ]; then
	sudo mkdir -p "${CIRCUITPY_MOUNT}"
fi

echo "PECKUS-INSTALL: mounting '${CIRCUITPY_DEVICE}' on '${CIRCUITPY_MOUNT}'"
sudo mount -t vfat -o rw,nosuid,nodev,relatime,uid=${USER_UID},gid=${USER_GID},fmask=0022,dmask=0022,iocharset=ascii,shortname=mixed,utf8,flush "${CIRCUITPY_DEVICE}" "${CIRCUITPY_MOUNT}"
if [ $? -ne 0 ]; then
	echo "ERROR mount"
	exit 1
fi


echo "PECKUS-INSTALL: copying application files to '${CIRCUITPY_MOUNT}' (might take about 30 seconds)"
( cd "${CIRCUITPY_DIR}" ; cp -rL . "${CIRCUITPY_MOUNT}/" )
if [ $? -ne 0 ]; then
	echo "ERROR cp"
	exit 1
fi

echo "PECKUS-INSTALL: cross-compiling MPY files on '${CIRCUITPY_MOUNT}/lib/{cpstatemachine,peckus}' (might take about 15 seconds)"
find "${CIRCUITPY_MOUNT}/lib/cpstatemachine/" "${CIRCUITPY_MOUNT}/lib/peckus/" -name "*.py" -type f -exec ../../other/circuitpython/mpy-cross/build/mpy-cross {} \;
find "${CIRCUITPY_MOUNT}/lib/cpstatemachine/" "${CIRCUITPY_MOUNT}/lib/peckus/" -name "*.mpy" -type f | while read MPY ; do PY="${MPY:0:-4}.py" ; if [ -f "${PY}" ]; then rm "${PY}" ; fi ; done

echo "PECKUS-INSTALL: unmounting '${CIRCUITPY_DEVICE}'"
sudo umount -q "${CIRCUITPY_MOUNT}"
sudo rmdir "${CIRCUITPY_MOUNT}"
echo "PECKUS-INSTALL: syncing"
sudo sync
sleep 1
echo "PECKUS-INSTALL: DONE!"
echo "Please remove and re-attach device to start PECKUS deployment"

