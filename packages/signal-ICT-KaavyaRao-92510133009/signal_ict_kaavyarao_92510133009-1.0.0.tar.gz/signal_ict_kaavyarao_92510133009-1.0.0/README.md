
This Package demonstrates the fundamental concepts of Signals and Systems by implementing various unitary signals, trigonometric signals, and signal operations in a modular way. The project also includes a main.py script that showcases how to use these modules with the help of tasks.

---

Folder Structure:
signal_ICT_KaavyaRao_92510133009/
│
├── init.py
├── unitary_signals.py
├── trigonometric_signals.py
├── operations.py
│
├── main.py


---

Modules and Functions

1. unitary_signals.py
Implements basic discrete signals:
- unit_step(n) - Generates a unit step signal.
- unit_impulse(n) - Generates a unit impulse signal.
- ramp_signal(n) - Generates a ramp signal.

Each function:
- Returns a NumPy array
- Plots the signal using Matplotlib

---

2. trigonometric_signals.py
Implements continuous-time signals:
- sine_wave(A, f, phi, t) - Generates a sine wave
- cosine_wave(A, f, phi, t) - Generates a cosine wave
- exponential_signal(A, a, t) - Generates an exponential signal

---

3. operations.py
Implements signal operations:
- time_shift(signal, k) - Shifts signal by *k* units
- time_scale(signal, k) - Scales time axis by factor *k*
- signal_addition(signal1, signal2) - Adds two signals
- signal_multiplication(signal1, signal2) - Multiplies two signals point-wise

---

Main Script (main.py)
Demonstrates:
1. Generate and plot unit step and unit impulse signals (length = 20).
2. Generate and plot a sine wave (A=2, f=5 Hz, phase=0, t=0–1 sec).
3. Perform time shifting on sine wave (+5 units).
4. Perform addition of unit step and ramp signal.
5. Multiply a sine and cosine wave of same frequency.


