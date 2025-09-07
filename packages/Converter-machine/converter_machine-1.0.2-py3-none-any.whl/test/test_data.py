import sys
import os
import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from converter_machine.data import converter_data

def test_bit_to_Byte():
    assert converter_data(8, "b", "B") == 1

def test_Byte_to_bit():
    assert converter_data(1, "B", "b") == 8

def test_invalid_unit():
    with pytest.raises(ValueError):
        converter_data(100, 'Bb', 'TB')
