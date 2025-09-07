import sys
import os
import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from converter_machine.time import converter_time

def test_week_to_second():
    assert converter_time(60480000, "s", "wk") == 100

def test_second_to_week():
    assert converter_time(1, "wk", "s") == 604800
    
def test_invalid_unit():
    with pytest.raises(ValueError):
        converter_time(100, 'sec', 'min')
