# SPDX-FileCopyrightText: Copyright (c) 2025 Mike Coats
# SPDX-License-Identifier: MIT

import busio
from adafruit_bus_device import i2c_device
from micropython import const

__version__ = "1.0.0"
__repo__ = "https://github.com/MikeCoats/CircuitPython_at42qt2120.git"

AT42QT2120_I2CADDR_DEFAULT = const(0x1C)
AT42QT2120_KEY_STATUS = const(3)  # -> const(4)
AT42QT2120_KEY_SIGNAL_0 = const(52)  # -> const(75)


def two_byte_int(high: int, low: int) -> int:
    """Combine two separate bytes (high and low) into a single 16-bit integer.

    This function takes two integers representing the high and low bytes of
    a 16-bit integer and combines them to produce the resulting integer. Both
    bytes are masked to ensure only the least significant 8 bits of each are
    used. The result is also masked to fit within 16 bits.

    Args:
        high: The high byte of the 16-bit integer.
        low: The low byte of the 16-bit integer.

    Returns:
         The resulting 16-bit integer combined from the high and low bytes.

    Examples:
        Build a 16-bit integer from two 8-bit integers:
        >>> two_byte_int(0xFF, 0x00) == 0xFF00
        True

        Build a 16-bit integer from two incorrect 16-bit integers, losing
        their upper bytes:
        >>> two_byte_int(0xFF11, 0xFF22) == 0x1122
        True
    """
    return ((high & 0xFF) << 8 | (low & 0xFF)) & 0xFFFF


def bit_on(value: int, bit: int) -> bool:
    """Determines whether a specific bit is set in the binary representation of
    a given integer value.

    This function checks if the bit at the specified position is set to 1
    in the binary representation of the provided integer. The bit position
    is zero-indexed, where the least significant bit is at position 0.

    Args:
        value: An integer in which the bit is to be checked.
        bit: The zero-indexed position of the bit to check.

    Returns:
        True if the bit at the specified position is set (1), otherwise False.

    Examples:
        The 0th bit of 0b1010 is off.
        >>> bit_on(0b1010, 0)
        False

        The 4th bit of 0x15 is on.
        >>> bit_on(0x15, 4)
        True
    """
    return bool(value & (1 << bit))


def tuple_of_bits(value: int, bits: int) -> tuple[bool, ...]:
    """Generates a tuple of boolean values representing the binary state of each bit
    in an integer, from the least significant bit to the most significant bit, for
    a specified number of bits.

    Each position in the tuple corresponds to whether the bit at that position is set (True) or not
    (False).

    Args:
        value: The integer value whose bits are to be represented as a tuple.
        bits: The number of bits to consider starting from the least
            significant bit.

    Returns:
        A tuple of boolean values, where each value indicates whether the corresponding bit is set
            (True) or not (False).

    Examples:
        The 4 bits of 0xF are all on.
        >>> tuple_of_bits(0xF,4)
        (True, True, True, True)

        The 5 bits of 0x15 are alternatingly on or off.
        >>> tuple_of_bits(0x15,5)
        (True, False, True, False, True)
    """
    return tuple(bit_on(value, i) for i in range(bits))


class AT42QT2120Channel:
    """A specific channel of an AT42QT2120 capacitive touch sensor.

    This provides access to the state and raw measurement of a specified
    channel on the AT42QT2120 sensor. The channel can be checked to determine
    whether it is being touched or to retrieve its raw measurement data.
    """

    _at42qt2120: "AT42QT2120"
    _channel: int

    def __init__(self, at42qt2120: "AT42QT2120", channel: int) -> None:
        """Creates a new ``AT42QT2120Channel`` instance.

        Args:
            at42qt2120: An instance of the touch sensor driver.
            channel: The channel this instance represents (0-11).
        """
        self._at42qt2120 = at42qt2120
        self._channel = channel

    @property
    def value(self) -> bool:
        """The current touch state of the sensor.

        Returns:
            True if the sensor is touched, False otherwise
        """
        return bit_on(self._at42qt2120.touched(), self._channel)

    @property
    def raw_value(self) -> int:
        """The raw signal measurement value for the specified channel.

        Returns:
            The raw signal measurement as an integer.
        """

        high = self._at42qt2120.read_register_byte(AT42QT2120_KEY_SIGNAL_0 + self._channel * 2 + 1)
        low = self._at42qt2120.read_register_byte(AT42QT2120_KEY_SIGNAL_0 + self._channel * 2)
        return two_byte_int(high, low)


class AT42QT2120:
    """An AT42QT2120 capacitive touch sensing chip.

    This interfaces with the AT42QT2120 to read touch inputs from its 12
    channels. Each channel's touch state can be accessed and queried to
    determine if it is activated or not. The class encapsulates low-level I2C
    communication and provides higher-level abstractions for working with the
    chip.

    Todo:
        * Implement the ``reset()`` method.
    """

    _i2c: i2c_device.I2CDevice
    _channels: list[AT42QT2120Channel | None]

    def __init__(self, i2c: busio.I2C, address: int = AT42QT2120_I2CADDR_DEFAULT) -> None:
        """Creates a new ``AT42QT2120`` instance.

        Args:
            i2c: The I2C bus to use.
            address: The I2C address of the sensor.
        """
        self._i2c = i2c_device.I2CDevice(i2c, address)
        self._channels = [None] * 12

    def __getitem__(self, key: int) -> AT42QT2120Channel:
        """Gets the channel at the specified key.

        Args:
            key: The index of the channel to retrieve.

        Returns:
            The channel corresponding to the specified key.
        """
        if key < 0 or key > 11:
            raise IndexError("pin must be a value 0-11")
        if self._channels[key] is None:
            self._channels[key] = AT42QT2120Channel(self, key)
        return self._channels[key]

    @property
    def touched_pins(self) -> tuple[bool, ...]:
        """Get a tuple of the touched state for all pins.

        Returns:
            A tuple of boolean values, where each value indicates whether the corresponding pin is
                touched (True) or not (False).
        """
        return tuple_of_bits(self.touched(), 12)

    def write_register_byte(self, register: int, value: int) -> None:
        """Write a single byte to a specified register.

        Args:
            register: The register to write to.
            value: The value to write to the register.
        """
        with self._i2c:
            self._i2c.write(bytes([register, value]))

    def read_register_byte(self, register: int) -> int:
        """Read a single byte from a specified register.

        Args:
            register: The register to read from.

        Returns:
            The value read from the register.
        """
        with self._i2c:
            request = bytes([register])
            response = bytearray(1)
            self._i2c.write_then_readinto(request, response)
            return response[0]

        # If anything goes wrong, return 0. Our code should handle this.
        return 0

    def touched(self) -> int:
        """Get the touch state of all pins as a 12-bit value.

        Returns: A 12-bit value representing the touch state of each pin. Each state in the value
            is represented by either a 1 or 0; touched or not.
        """
        high = self.read_register_byte(AT42QT2120_KEY_STATUS + 1)
        low = self.read_register_byte(AT42QT2120_KEY_STATUS)
        return two_byte_int(high, low)

    def is_touched(self, pin: int) -> bool:
        """Get if ``pin`` is being touched.

        Args:
            pin: The pin to check.

        Raises:
            ValueError: If ``pin`` is out of range.

        Returns:
            True if ``pin`` is being touched; otherwise False.
        """
        if pin < 0 or pin > 11:
            raise ValueError("Pin must be a value 0-11.")

        return bit_on(self.touched(), pin)
