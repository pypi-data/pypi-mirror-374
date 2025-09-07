
# signal_ICT_JenishDesai_92510133025

**Student:** Jenish Desai  
**Enrollment:** 92510133025

This package demonstrates basic Signals & Systems:
- Unitary signals: unit step, impulse, ramp
- Trigonometric/exponential signals
- Operations: time shift (zero-padded), time scale (interpolated), addition, multiplication

## Install from wheel
```bash
pip install dist/signal_ICT_JenishDesai_92510133025-0.1.0-py3-none-any.whl
```

## Usage
```python
import numpy as np
from signal_ICT_JenishDesai_92510133025 import unit_step, unit_impulse, ramp_signal
n = np.arange(-10, 10)
x = unit_step(n)
```

## Run the demo
```bash
python main.py
```

## Build (creates wheel + sdist)
```bash
python -m pip install --upgrade build
python -m build
```

## TestPyPI Upload (example)
```bash
python -m pip install --upgrade twine
twine upload -r testpypi dist/*
```

## Notes
- Time shift uses zero-padding (no circular wrap).
- Time scaling uses linear interpolation to keep output length unchanged.
