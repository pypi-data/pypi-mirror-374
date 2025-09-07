# SPDX-FileCopyrightText: 2017 Tony DiCola for Adafruit Industries
# SPDX-FileCopyrightText: 2025 Mike Coats
# SPDX-License-Identifier: MIT

# Simple test of the AT42QT2120 capacitive touch sensor library.
# Will print out a message when any of the 12 capacitive touch inputs of the
# board are touched.  Open the serial REPL after running to see the output.
# Author: Tony DiCola
# Author: Mike Coats
import time

import board
import busio

# Import AT42QT2120 module.
import at42qt2120

# Create I2C bus.
i2c = busio.I2C(board.SCL, board.SDA)

# Create AT42QT2120 object.
at42qt = at42qt2120.AT42QT2120(i2c)

# Note you can optionally change the address of the device:
# at42qt = at42qt2120.AT42QT2120(i2c, address=0x91)

# Loop forever testing each input and printing when they're touched.
while True:
    # Loop through all 12 inputs (0-11).
    for i in range(12):
        # Call is_touched and pass it then number of the input.  If it's touched
        # it will return True, otherwise it will return False.
        if at42qt[i].value:
            print(f"Input {i} touched!")
    time.sleep(0.25)  # Small delay to keep from spamming output messages.


# "    __"
# "   (oo)"
# "    \/  u"
# "   /  \/"
# " / |  |"
# " n |__|"
# "  _|  |"
# " n    |"
# "      n"
