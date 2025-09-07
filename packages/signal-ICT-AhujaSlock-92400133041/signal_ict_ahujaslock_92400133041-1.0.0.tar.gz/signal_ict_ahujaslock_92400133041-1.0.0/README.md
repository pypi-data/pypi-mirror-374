# signal_ICT_AhujaSlock_92400133041

A Python package for generating and operating on signals, demonstrating fundamental concepts of Signals and Systems.

## Installation

### From Source
1. Clone the repository:
   ```
   git clone https://github.com/yourusername/signal_ICT_AhujaSlock_92400133041.git
   cd signal_ICT_AhujaSlock_92400133041
   ```

2. Install the package:
   ```
   pip install .
   ```

### From Wheel
1. Download the .whl file from the dist/ folder.
2. Install using pip:
   ```
   pip install signal_ICT_AhujaSlock_92400133041-1.0.0-py3-none-any.whl
   ```

### From TestPyPI
```
pip install -i https://test.pypi.org/simple/ signal_ICT_AhujaSlock_92400133041
```

## Usage

### Importing the Package
```python
from signal_ICT_AhujaSlock_92400133041 import unit_step, unit_impulse, ramp_signal
from signal_ICT_AhujaSlock_92400133041 import sine_wave, cosine_wave, exponential_signal
from signal_ICT_AhujaSlock_92400133041 import time_shift, time_scale, signal_addition, signal_multiplication
```

### Example Usage
```python
import numpy as np
import matplotlib.pyplot as plt

# Generate unit step signal
step = unit_step(20)

# Generate sine wave
t = np.linspace(0, 1, 500)
sine = sine_wave(A=2, f=5, phi=0, t=t)

# Time shift
shifted = time_shift(sine, 5)

# Addition
ramp = ramp_signal(20)
added = signal_addition(step, ramp)

# Multiplication
cosine = cosine_wave(A=2, f=5, phi=0, t=t)
multiplied = signal_multiplication(sine, cosine)
```

## Modules

### unitary_signals.py
- `unit_step(n)`: Generates a unit step signal of length n.
- `unit_impulse(n)`: Generates a unit impulse signal of length n.
- `ramp_signal(n)`: Generates a ramp signal of length n.

### trigonometric_signals.py
- `sine_wave(A, f, phi, t)`: Generates a sine wave with amplitude A, frequency f, phase phi, over time vector t.
- `cosine_wave(A, f, phi, t)`: Generates a cosine wave.
- `exponential_signal(A, a, t)`: Generates an exponential signal.

### operations.py
- `time_shift(signal, k)`: Shifts the signal by k units.
- `time_scale(signal, k)`: Scales the time axis by factor k.
- `signal_addition(signal1, signal2)`: Adds two signals.
- `signal_multiplication(signal1, signal2)`: Multiplies two signals point-wise.

## Dependencies
- numpy
- matplotlib

## License
MIT License
