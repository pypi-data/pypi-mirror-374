# signal_ICT_Trupalijasani_92510133011

Educational package for Signals & Systems course assignments.

## Modules
- `unitary_signals` — unit_step, unit_impulse, ramp_signal
- `trigonometric_signals` — sine_wave, cosine_wave, exponential_signal
- `operations` — time_shift, time_scale, signal_addition, signal_multiplication

## Usage
```python
from signal_ICT_Trupalijasani_92510133011 import unitary_signals, trigonometric_signals, operations
import numpy as np
n = np.arange(-10,10)
step = unitary_signals.unit_step(n)
imp = unitary_signals.unit_impulse(n)
ramp = unitary_signals.ramp_signal(n)

t = np.linspace(0,1,500)
sine = trigonometric_signals.sine_wave(2,5,0,t)
cosine = trigonometric_signals.cosine_wave(2,5,0,t)

shifted = operations.time_shift(sine, 5)
added = operations.signal_addition(step, ramp)
mult = operations.signal_multiplication(sine[:len(cosine)], cosine)
```

## Build / Install locally
Run:
```
python setup.py sdist bdist_wheel
pip install dist/signal_ICT_Trupalijasani_92510133011-0.1-py3-none-any.whl
```

