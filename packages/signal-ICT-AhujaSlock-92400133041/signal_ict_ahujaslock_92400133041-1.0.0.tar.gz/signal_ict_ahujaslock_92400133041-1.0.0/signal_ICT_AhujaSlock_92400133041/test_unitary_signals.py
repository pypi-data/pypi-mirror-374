import unittest
import numpy as np
from unitary_signals import unit_step, unit_impulse, ramp_signal

class TestUnitarySignals(unittest.TestCase):

    def test_unit_step(self):
        signal = unit_step(5)
        expected = np.array([1, 1, 1, 1, 1])
        np.testing.assert_array_equal(signal, expected)

    def test_unit_impulse(self):
        signal = unit_impulse(5)
        expected = np.array([1, 0, 0, 0, 0])
        np.testing.assert_array_equal(signal, expected)

    def test_ramp_signal(self):
        signal = ramp_signal(5)
        expected = np.array([0, 1, 2, 3, 4])
        np.testing.assert_array_equal(signal, expected)

if __name__ == '__main__':
    unittest.main()
