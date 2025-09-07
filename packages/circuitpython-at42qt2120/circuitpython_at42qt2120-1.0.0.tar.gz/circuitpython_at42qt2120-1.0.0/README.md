# CircuitPython-AT42QT2120

[![Documentation Status](https://readthedocs.org/projects/adafruit-circuitpython-mpr121/badge/?version=latest)][readthedocs]
[![Build Status](https://github.com/MikeCoats/CircuitPython_AT42QT2120/workflows/Build%20CI/badge.svg)][github-action]
[![Code Style: Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)][ruff]

A CircuitPython module for the AT42QT2120 capacitive touch sensor IC, (mostly) compatible with Adafruit's MPR121 library.

This library's interface is designed after Adafruit's MPR121 module.
The ICs diverge in functionality, so we only include functions available on both chips.
To determine which functionality is required, I surveyed several consumers of the MPR121 library.
This includes three examples from Adafruit, and many of the projects "dependent" on their library on GitHub.

A full list of all the projects I surveyed and their usage of the MPR121 library can be found in [the Compatibility Audit][audit].
This audit should let us cover enough of the design to use an AT42QT2120 as a drop-in replacement for most users of the MPR121.

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

## Documentation

API documentation for this library can be found on [Read the Docs][readthedocs].

## Contributing

Contributions are welcome! Please read our [Code of Conduct][conduct]
before contributing to help this project stay welcoming.

[readthedocs]: https://at42qt2120.readthedocs.io/en/latest/
[github-action]: https://github.com/MikeCoats/CircuitPython_AT42QT2120/actions
[ruff]: https://github.com/astral-sh/ruff
[audit]: mkdocs/compatibility.md
[pypi-at42qt2120]: https://pypi.org/project/circuitpython-at42qt2120/
[readthedocs]: https://at42qt2120.readthedocs.io/
[conduct]: ./CODE_OF_CONDUCT.md
