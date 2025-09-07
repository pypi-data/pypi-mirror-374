import sys
import os
import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from converter_machine.mass import converter_mass

def test_grams_to_kilograms():
    assert converter_mass(1000, "g", "kg") == 1

def test_kilograms_to_grams():
    assert converter_mass(2, "kg", "g") == 2000
    
def test_invalid_unit():
    with pytest.raises(ValueError):
        converter_mass(100, 'stone', 'kg')
