signal_ICT_Keshvi_92510133028/
│── __init__.py
│── unitary_signals.py         # Unit step, unit impulse, ramp
│── trigonometric_signals.py   # Sine, cosine, exponential
│── operations.py              # Time shift, time scale, add, multiply
main.py                        # Demo script
pyproject.toml                 # Packaging details
README.md                      # Documentation


This models will display:
Unitary signals → step, impulse, ramp
Trigonometric signals → sine, cosine
Exponential signals → growth & decay
Operations → time shift, scaling, addition, multiplication

### 1. `unitary_signals.py`
Implements **basic discrete-time signals**:
- `unit_step(n)` – Generates a unit step signal.
- `unit_impulse(n)` – Generates a unit impulse signal.
- `ramp_signal(n)` – Generates a ramp signal.

### 2. `trigonometric_signals.py`
Implements **continuous-time signals**:
- `sine_wave(A, f, phi, t)` – Generates a sine wave with amplitude `A`, frequency `f`, phase `phi`, and time vector `t`.
- `cosine_wave(A, f, phi, t)` – Generates a cosine wave.
- `exponential_signal(A, a, t)` – Generates an exponential signal (growth/decay).

### 3. `operations.py`
Implements **signal operations**:
- `time_shift(signal, n, k)` – Shifts a signal by `k` units (delay/advance).
- `time_scale(signal, n, k)` – Scales a signal’s time axis by factor `k`.
- `signal_addition(signal1, signal2)` – Adds two signals element-wise.
- `signal_multiplication(signal1, signal2)` – Multiplies two signals element-wise.

### 4. `main.py`
Main script to demonstrate:
1. Generate and plot a unit step and unit impulse signal (length 20).  
2. Generate a sine wave of amplitude 2, frequency 5 Hz, phase 0, over `t = 0 to 1 sec`.  
3. Perform time shifting on the sine wave by +5 units and plot both original and shifted signals.  
4. Perform addition of unit step and ramp signals.  
5. Multiply a sine and cosine wave of same frequency and plot the result.