#!/bin/sh

CIRCUITPY_DEVICE=${1:-/dev/sda1}
CIRCUITPY_MOUNT=${2:-/media/${USERNAME}/CIRCUITPY}

GIT_REPODIR=`git rev-parse --show-toplevel`

USER_UID=`id -u ${USERNAME}`
USER_GID=`id -g ${USERNAME}`


if [ -d "${CIRCUITPY_MOUNT}" ]; then
	sudo umount -q "${CIRCUITPY_DEVICE}"
	if [ $? -ne 0 ]; then
		echo "ERROR umount"
		exit 1
	fi
fi

sudo mkfs.vfat -F 12 -n PECKUS -I "${CIRCUITPY_DEVICE}"
if [ $? -ne 0 ]; then
	echo "ERROR mkfs.vfat"
	exit 1
fi

if [ ! -d "${CIRCUITPY_MOUNT}" ]; then
	sudo mkdir "${CIRCUITPY_MOUNT}"
fi

sudo mount -t vfat -o rw,nosuid,nodev,relatime,uid=${USER_UID},gid=${USER_GID},fmask=0022,dmask=0022,iocharset=ascii,shortname=mixed,utf8,flush "${CIRCUITPY_DEVICE}" "${CIRCUITPY_MOUNT}"
if [ $? -ne 0 ]; then
	echo "ERROR mount"
	exit 1
fi


( cd "${GIT_REPODIR}/CIRCUITPY/" ; cp -rLv . "${CIRCUITPY_MOUNT}/" )
if [ $? -ne 0 ]; then
	echo "ERROR cp"
	exit 1
fi

sudo umount -q "${CIRCUITPY_DEVICE}"

