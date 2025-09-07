import sys
import os
import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from converter_machine.speed import converter_speed

def test_meter_per_second_to_kilometer_per_second():
    assert converter_speed(1000, "m/s", "km/s") == 1

def test_kilometer_per_second_to_meter_per_second():
    assert converter_speed(360, "km/s", "m/s") == 360000
    
def test_invalid_unit():
    with pytest.raises(ValueError):
        converter_speed(100, 'm/s', 'a/s')
