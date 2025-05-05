#!/bin/sh

GIT_CIRCUITPYTHON=${1:-/tmp/circuitpython}

if [ ! -d "${GIT_CIRCUITPYTHON}" ]; then
	echo "PECKUS-BUILD: non-existing directory '${GIT_CIRCUITPYTHON}'"
	exit 1
fi

cd "${GIT_CIRCUITPYTHON}"
git status >/dev/null 2>/dev/null
if [ $? -ne 0 ]; then
	git clone https://github.com/adafruit/circuitpython.git .
fi

cd -

cd `dirname $0`
podman build -t circuitpython-peckus -f build/Containerfile -v ${GIT_CIRCUITPYTHON}:/circuitpython
