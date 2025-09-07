# SPDX-FileCopyrightText: Copyright (c) 2025 Mike Coats
# SPDX-License-Identifier: MIT

from at42qt2120 import bit_on, tuple_of_bits, two_byte_int


def test_valid_two_byte_int():
    """Test valid two byte integer conversions."""
    assert two_byte_int(0x00, 0x00) == 0x0000
    assert two_byte_int(0xFF, 0xFF) == 0xFFFF
    assert two_byte_int(0xFF, 0x00) == 0xFF00
    assert two_byte_int(0x00, 0xFF) == 0x00FF


def test_invalid_two_byte_int():
    """Test invalid two byte integer conversions."""

    # Try converting two 16-bit integers instead of two 8-bit integers, losing the upper bytes of
    # each.
    assert two_byte_int(0xFF00, 0xFF00) == 0x0000


def test_bit_on_all_zeros():
    """Test the bit_on function with 12 off bits."""
    assert bit_on(0x0000, 0) == False
    assert bit_on(0x0000, 1) == False
    assert bit_on(0x0000, 2) == False
    assert bit_on(0x0000, 3) == False
    assert bit_on(0x0000, 4) == False
    assert bit_on(0x0000, 5) == False
    assert bit_on(0x0000, 6) == False
    assert bit_on(0x0000, 7) == False
    assert bit_on(0x0000, 8) == False
    assert bit_on(0x0000, 9) == False
    assert bit_on(0x0000, 10) == False
    assert bit_on(0x0000, 11) == False
    assert bit_on(0x0000, 12) == False


def test_bit_on_all_one_zeros():
    """Test the bit_on function with alternating on and off bits."""
    assert bit_on(0x0555, 0) == True
    assert bit_on(0x0555, 1) == False
    assert bit_on(0x0555, 2) == True
    assert bit_on(0x0555, 3) == False
    assert bit_on(0x0555, 4) == True
    assert bit_on(0x0555, 5) == False
    assert bit_on(0x0555, 6) == True
    assert bit_on(0x0555, 7) == False
    assert bit_on(0x0555, 8) == True
    assert bit_on(0x0555, 9) == False
    assert bit_on(0x0555, 10) == True
    assert bit_on(0x0555, 11) == False
    assert bit_on(0x0555, 12) == False


def test_bit_on_all_zero_ones():
    """Test the bit_on function with alternating off and on bits."""
    assert bit_on(0x0AAA, 0) == False
    assert bit_on(0x0AAA, 1) == True
    assert bit_on(0x0AAA, 2) == False
    assert bit_on(0x0AAA, 3) == True
    assert bit_on(0x0AAA, 4) == False
    assert bit_on(0x0AAA, 5) == True
    assert bit_on(0x0AAA, 6) == False
    assert bit_on(0x0AAA, 7) == True
    assert bit_on(0x0AAA, 8) == False
    assert bit_on(0x0AAA, 9) == True
    assert bit_on(0x0AAA, 10) == False
    assert bit_on(0x0AAA, 11) == True
    assert bit_on(0x0AAA, 12) == False


def test_bit_on_all_ones():
    """Test the bit_on function with 12 on bits."""
    assert bit_on(0x0FFF, 0) == True
    assert bit_on(0x0FFF, 1) == True
    assert bit_on(0x0FFF, 2) == True
    assert bit_on(0x0FFF, 3) == True
    assert bit_on(0x0FFF, 4) == True
    assert bit_on(0x0FFF, 5) == True
    assert bit_on(0x0FFF, 6) == True
    assert bit_on(0x0FFF, 7) == True
    assert bit_on(0x0FFF, 8) == True
    assert bit_on(0x0FFF, 9) == True
    assert bit_on(0x0FFF, 10) == True
    assert bit_on(0x0FFF, 11) == True
    assert bit_on(0x0FFF, 12) == False


def test_tuple_of_bits():
    """Test the tuple_of_bits function with 12 off bits, alternating on and off bits, alternating
    off and on bits, and 12 on bits."""
    assert tuple_of_bits(0x0000, 12) == (
        False,
        False,
        False,
        False,
        False,
        False,
        False,
        False,
        False,
        False,
        False,
        False,
    )
    assert tuple_of_bits(0x0555, 12) == (
        True,
        False,
        True,
        False,
        True,
        False,
        True,
        False,
        True,
        False,
        True,
        False,
    )
    assert tuple_of_bits(0x0AAA, 12) == (
        False,
        True,
        False,
        True,
        False,
        True,
        False,
        True,
        False,
        True,
        False,
        True,
    )
    assert tuple_of_bits(0x0FFF, 12) == (
        True,
        True,
        True,
        True,
        True,
        True,
        True,
        True,
        True,
        True,
        True,
        True,
    )
