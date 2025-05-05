#!/bin/sh

GIT_CIRCUITPYTHON=/home/juergen/Git/github.com/other/circuitpython


cd `dirname $0`
podman build -t circuitpython-peckus -f build/Containerfile -v ${GIT_CIRCUITPYTHON}:/circuitpython
