import unittest
import numpy as np
from operations import time_shift, time_scale, signal_addition, signal_multiplication

class TestOperations(unittest.TestCase):

    def test_time_shift(self):
        signal = np.array([1, 2, 3, 4, 5])
        shifted = time_shift(signal, 2)
        expected = np.roll(signal, 2)
        np.testing.assert_array_equal(shifted, expected)

    def test_time_scale(self):
        signal = np.array([1, 2, 3, 4, 5, 6])
        scaled = time_scale(signal, 2)
        expected = signal[::2]
        np.testing.assert_array_equal(scaled, expected)

    def test_signal_addition(self):
        signal1 = np.array([1, 2, 3])
        signal2 = np.array([4, 5, 6])
        added = signal_addition(signal1, signal2)
        expected = signal1 + signal2
        np.testing.assert_array_equal(added, expected)

    def test_signal_multiplication(self):
        signal1 = np.array([1, 2, 3])
        signal2 = np.array([4, 5, 6])
        multiplied = signal_multiplication(signal1, signal2)
        expected = signal1 * signal2
        np.testing.assert_array_equal(multiplied, expected)

if __name__ == '__main__':
    unittest.main()
