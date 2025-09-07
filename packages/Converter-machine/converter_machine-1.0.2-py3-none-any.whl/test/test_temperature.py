import sys
import os
import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from converter_machine.temperature import converter_temperature

def test_celsius_to_kelvin():
    assert converter_temperature(10, "C", "K") == 283.15

def test_kelvin_to_celsius():
    assert converter_temperature(0, "K", "C") == -273.15
    
def test_invalid_unit():
    with pytest.raises(ValueError):
        converter_temperature(100, 'C', 'cc')
