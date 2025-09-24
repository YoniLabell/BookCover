import sys, pathlib
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1] / 'app'))
from services.spine import calculate_spine

def test_spine_calc():
    assert abs(calculate_spine(100, '90gsm') - 3.0) < 0.1
    assert abs(calculate_spine(101, '90gsm') - 3.06) < 0.1
