import sys
import os
import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from converter_machine.volume import converter_volume

def test_Cubic_centimeter_to_Cubic_meter():
    assert converter_volume(10, "cm^3", "m^3") == 0.00001

def test_Cubic_meter_to_Cubic_centimeter():
    assert converter_volume(25, "m^3", "cm^3") == 25000000
    
def test_invalid_unit():
    with pytest.raises(ValueError):
        converter_volume(100, 'sec', 'min')
