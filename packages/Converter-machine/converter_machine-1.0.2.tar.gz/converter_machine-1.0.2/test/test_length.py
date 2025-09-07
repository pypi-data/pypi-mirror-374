import sys
import os
import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from converter_machine.length import converter_length

def test_meters_to_kilometers():
    assert converter_length(1000, "m", "km") == 1

def test_kilometers_to_meters():
    assert converter_length(1.5, "km", "m") == 1500
    
def test_invalid_unit():
    with pytest.raises(ValueError):
        converter_length(100, 'm', 'as')
