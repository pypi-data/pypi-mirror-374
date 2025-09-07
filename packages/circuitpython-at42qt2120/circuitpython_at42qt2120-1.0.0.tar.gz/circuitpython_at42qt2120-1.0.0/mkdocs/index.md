# Introduction

[![Documentation Status](https://readthedocs.org/projects/adafruit-circuitpython-mpr121/badge/?version=latest)][readthedocs]
[![Build Status](https://github.com/MikeCoats/CircuitPython_AT42QT2120/workflows/Build%20CI/badge.svg)][github-action]
[![Code Style: Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)][ruff]

A CircuitPython module for the AT42QT2120 capacitive touch sensor IC, (mostly) compatible with [Adafruit's MPR121 library][adafruit-mpr121].

## Installing from PyPI

On supported GNU/Linux systems like the Raspberry Pi, you can install the driver locally [from PyPI][pypi-at42qt2120].
To install in a virtual environment in your current project:

```shell
mkdir project-name && cd project-name
python3 -m venv .venv
source .venv/bin/activate
pip3 install circuitpython-at42qt2120
```

## Usage Example

```python
import busio
import board
from adafruit_bus_device import i2c_device

from at42qt2120 import AT42QT2120

i2c_bus = busio.I2C(board.SCL, board.SDA, frequency=100000)
at = AT42QT2120(i2c_bus)

print(at.touched_pins)
print([at[i].raw_value for i in range(12)])
```

## Dependencies

This driver depends on:

- [Adafruit CircuitPython][adafruit-circuitpython]
- [Bus Device][adafruit-bus-device]

Please ensure all dependencies are available on the CircuitPython filesystem.
This is easily achieved by downloading [the Adafruit library and driver bundle][adafruit-bundle].

[readthedocs]: https://at42qt2120.readthedocs.io/en/latest/
[github-action]: https://github.com/MikeCoats/CircuitPython_AT42QT2120/actions
[ruff]: https://github.com/astral-sh/ruff
[adafruit-mpr121]: https://docs.circuitpython.org/projects/mpr121/en/latest/index.html
[pypi-at42qt2120]: https://pypi.org/project/circuitpython-at42qt2120/
[adafruit-circuitpython]: https://github.com/adafruit/circuitpython
[adafruit-bus-device]: https://github.com/adafruit/Adafruit_CircuitPython_BusDevice
[adafruit-bundle]: https://github.com/adafruit/Adafruit_CircuitPython_Bundle
