FROM debian:13-slim

ARG CIRCUITPYTHON_VERSION
ARG CIRCUITPYTHON_BOARD
ARG CIRCUITPYTHON_PORT="nordic"
ARG CIRCUITPYTHON_DPKGS="python3-intelhex"
ARG CIRCUITPYTHON_PATHS="/usr/share/python3-intelhex"

ARG CIRCUITPYTHON_BUILD_SAFEMODE_PY="1"
ARG CIRCUITPYTHON_BUILD_SAFEMODE_SKIP="0"

ENV DEBIAN_FRONTEND="noninteractive"
ENV PATH="${PATH}":"${CIRCUITPYTHON_PATHS}"

RUN \
  apt update -y \
  && apt install -y build-essential gcc-arm-none-eabi pkg-config \
                 libffi-dev wget git gettext python3 python3-venv python3-pip python-is-python3 \
                 ninja-build cmake libusb-1.0-0-dev ${CIRCUITPYTHON_DPKGS}

WORKDIR "/circuitpython"

RUN \
  git checkout "${CIRCUITPYTHON_VERSION}"

RUN \
  python -m venv .venv \
  && . .venv/bin/activate \
  && pip install --no-cache-dir -r requirements-dev.txt \
  && pip install --no-cache-dir huffman adafruit-nrfutil \
  && pip install --pre -U git+https://github.com/makerdiary/uf2utils.git@main \
  && make -C mpy-cross

WORKDIR "/circuitpython/ports/${CIRCUITPYTHON_PORT}"

RUN \
  make fetch-port-submodules

