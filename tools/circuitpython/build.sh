#!/bin/sh

export CIRCUITPYTHON_VERSION="${CIRCUITPYTHON_VERSION:-10.1.4}"
export CIRCUITPYTHON_PORT="${CIRCUITPYTHON_PORT:-nordic}"
export CIRCUITPYTHON_BOARD="${CIRCUITPYTHON_BOARD:-makerdiary_nrf52840_mdk_usb_dongle}"
export CIRCUITPYTHON_SAFEMODE="${CIRCUITPYTHON_SAFEMODE:-1}"

if [ "${CIRCUITPYTHON_SAFEMODE}" = "0" ]; then
	export CIRCUITPYTHON_BUILD_SAFEMODE_PY="0"
	export CIRCUITPYTHON_BUILD_SAFEMODE_SKIP="1"
else
	export CIRCUITPYTHON_BUILD_SAFEMODE_PY="1"
	export CIRCUITPYTHON_BUILD_SAFEMODE_SKIP="0"
fi

CMD_BUILD_SH=`realpath "$0"`
DIR_BUILD_SH=`dirname "${CMD_BUILD_SH}"`

DIR_CIRCUITPYTHON_DEFAULT="${DIR_BUILD_SH}/build/circuitpython"
DIR_CIRCUITPYTHON=`realpath ${1:-"${DIR_CIRCUITPYTHON_DEFAULT}"}`

if [ ! -d "${DIR_CIRCUITPYTHON}" ]; then
	if [ "${DIR_CIRCUITPYTHON}" = "${DIR_CIRCUITPYTHON_DEFAULT}" ]; then
		mkdir "${DIR_CIRCUITPYTHON}"
	else
		echo "PECKUS-BUILD: non-existing directory '${DIR_CIRCUITPYTHON}'"
		exit 1
	fi
fi

cd "${DIR_CIRCUITPYTHON}"
git status >/dev/null 2>/dev/null
if [ $? -ne 0 ]; then
	git clone https://github.com/adafruit/circuitpython.git "${DIR_CIRCUITPYTHON}"
fi
git checkout --detach "${CIRCUITPYTHON_VERSION}"
git checkout "ports/${CIRCUITPYTHON_PORT}/boards/${CIRCUITPYTHON_BOARD}/mpconfigboard.mk"
echo "CIRCUITPY_SAFEMODE_PY         = ${CIRCUITPYTHON_BUILD_SAFEMODE_PY}"   >> ports/${CIRCUITPYTHON_PORT}/boards/${CIRCUITPYTHON_BOARD}/mpconfigboard.mk
echo "CIRCUITPY_SKIP_SAFE_MODE_WAIT = ${CIRCUITPYTHON_BUILD_SAFEMODE_SKIP}" >> ports/${CIRCUITPYTHON_PORT}/boards/${CIRCUITPYTHON_BOARD}/mpconfigboard.mk
echo "CIRCUITPY_BOOT_OUTPUT_FILE ="                                         >> ports/${CIRCUITPYTHON_PORT}/boards/${CIRCUITPYTHON_BOARD}/mpconfigboard.mk


cd "${DIR_BUILD_SH}"
podman build -t circuitpython-peckus -f build.Containerfile -v "${DIR_CIRCUITPYTHON}":"/circuitpython" \
	--build-arg CIRCUITPYTHON_VERSION="${CIRCUITPYTHON_VERSION}" \
	--build-arg CIRCUITPYTHON_PORT="${CIRCUITPYTHON_PORT}" \
	--build-arg CIRCUITPYTHON_BOARD="${CIRCUITPYTHON_BOARD}"

podman run --rm -e "CIRCUITPYTHON_*" -v "${DIR_CIRCUITPYTHON}":"/circuitpython" -t circuitpython-peckus make clean all V=0 BOARD="${CIRCUITPYTHON_BOARD}"
if [ "${CIRCUITPYTHON_BOARD}" = "makerdiary_nrf52840_mdk_usb_dongle" ]; then
	podman run --rm -v "${DIR_CIRCUITPYTHON}":"/circuitpython" -t circuitpython-peckus \
	           /bin/sh -c '. /circuitpython/.venv/bin/activate ;
	                       uf2conv -f 0xADA52840 -c -o "/circuitpython/circuitpython_'${CIRCUITPYTHON_VERSION}'.uf2" "build-'${CIRCUITPYTHON_BOARD}'/firmware.hex"'
else
	podman run --rm -v "${DIR_CIRCUITPYTHON}":"/circuitpython" -t circuitpython-peckus \
	           /bin/sh -c 'cp                          "/circuitpython/circuitpython_'${CIRCUITPYTHON_VERSION}'.uf2" "build-'${CIRCUITPYTHON_BOARD}'/firmware.uf2"'
fi
echo " "
if [ ! -f "${DIR_CIRCUITPYTHON}/circuitpython_${CIRCUITPYTHON_VERSION}.uf2" ]; then
	echo "build.sh: Failed to build CircuitPython UF2"
	exit 1
fi
mv "${DIR_CIRCUITPYTHON}/circuitpython_${CIRCUITPYTHON_VERSION}.uf2" "${DIR_BUILD_SH}/build/"

echo "build.sh: CircuitPython UF2 (SAFEMODE=${CIRCUITPYTHON_SAFEMODE}) saved as 'circuitpython_${CIRCUITPYTHON_VERSION}.uf2' in '`dirname $0`/build'"
