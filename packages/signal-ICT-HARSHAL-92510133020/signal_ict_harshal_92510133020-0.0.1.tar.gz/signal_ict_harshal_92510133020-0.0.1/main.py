# main.py

import numpy as np
import matplotlib.pyplot as plt

# Import from our custom modules
from signal_ICT_HARSHAL_92510133020.unitary_signals import unit_step, unit_impulse, ramp_signal
from signal_ICT_HARSHAL_92510133020.trigonometric_signals import sine_wave, cosine_wave
from signal_ICT_HARSHAL_92510133020.operations import time_shift, signal_addition, signal_multiplication


if __name__ == "__main__":
    # 1. Generate and plot a unit step signal and unit impulse signal of length 20
    n = np.arange(0, 20)   # discrete range of 20 samples
    step = unit_step(n)
    impulse = unit_impulse(n)

    # 2. Generate a sine wave of amplitude 2, frequency 5 Hz, phase 0, over t = 0 to 1 sec
    t = np.linspace(0, 1, 500)   # continuous time vector
    sine = sine_wave(A=2, f=5, phi=0, t=t)

    # 3. Perform time shifting on the sine wave by +5 units and plot both
    n_sine = np.arange(len(sine))   # discrete index for sine samples
    n_shifted, sine_shifted = time_shift(sine, n_sine, k=5)

    plt.plot(n_sine, sine, label="Original Sine")
    plt.plot(n_shifted, sine_shifted, label="Shifted Sine (+5)")
    plt.title("Sine Wave Time Shift")
    plt.xlabel("Sample Index")
    plt.ylabel("Amplitude")
    plt.legend()
    plt.grid(True)
    plt.show()

    # 4. Perform addition of the unit step and ramp signal
    ramp = ramp_signal(n)
    added = signal_addition(step, ramp)

    # 5. Multiply a sine and cosine wave of same frequency
    sine2 = sine_wave(A=1, f=5, phi=0, t=t)
    cosine2 = cosine_wave(A=1, f=5, phi=0, t=t)
    multiplied = signal_multiplication(sine2, cosine2)

    plt.plot(t, multiplied)
    plt.title("Sine x Cosine (Same Frequency)")
    plt.xlabel("Time (s)")
    plt.ylabel("Amplitude")
    plt.grid(True)
    plt.show()
