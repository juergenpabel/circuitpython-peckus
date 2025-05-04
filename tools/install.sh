#!/bin/sh

sudo mkfs.vfat -F 16 -n PECKUS "${CIRCUITPY_DEVICE}"

cp -rL TODO
