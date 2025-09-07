import unittest
import numpy as np
from trigonometric_signals import sine_wave, cosine_wave, exponential_signal

class TestTrigonometricSignals(unittest.TestCase):

    def test_sine_wave(self):
        t = np.linspace(0, 1, 100)
        signal = sine_wave(A=1, f=1, phi=0, t=t)
        expected = np.sin(2 * np.pi * 1 * t)
        np.testing.assert_array_almost_equal(signal, expected)

    def test_cosine_wave(self):
        t = np.linspace(0, 1, 100)
        signal = cosine_wave(A=1, f=1, phi=0, t=t)
        expected = np.cos(2 * np.pi * 1 * t)
        np.testing.assert_array_almost_equal(signal, expected)

    def test_exponential_signal(self):
        t = np.linspace(0, 1, 100)
        signal = exponential_signal(A=1, a=1, t=t)
        expected = np.exp(1 * t)
        np.testing.assert_array_almost_equal(signal, expected)

if __name__ == '__main__':
    unittest.main()
