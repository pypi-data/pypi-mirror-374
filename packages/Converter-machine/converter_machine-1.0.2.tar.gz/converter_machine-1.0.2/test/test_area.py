import sys
import os
import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from converter_machine.area import converter_area

def test_Square_meters_to_Square_kilometers():
    assert converter_area(1000, "m^2", "km^2") == 0.001

def test_Square_kilometers_to_Square_meters():
    assert converter_area(1, "km^2", "m^2") == 1000000

def test_invalid_unit():
    with pytest.raises(ValueError):
        converter_area(100, 'mmm^1', 'km')
