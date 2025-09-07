# trigonometric_signals.py

import numpy as np
import matplotlib.pyplot as plt

def sine_wave(A, f, phi, t):
    """
    Generates a sine wave.
    Args:
        A (float): Amplitude
        f (float): Frequency in Hz
        phi (float): Phase in radians
        t (numpy array): Time vector
    Returns:
        numpy array: Sine wave signal
    """
    y = A * np.sin(2 * np.pi * f * t + phi)
    plt.plot(t, y)
    plt.title(f"Sine Wave: A={A}, f={f}Hz, phi={phi} rad")
    plt.xlabel("Time (s)")
    plt.ylabel("Amplitude")
    plt.grid(True)
    plt.show()
    return y


def cosine_wave(A, f, phi, t):
    """
    Generates a cosine wave.
    Args:
        A (float): Amplitude
        f (float): Frequency in Hz
        phi (float): Phase in radians
        t (numpy array): Time vector
    Returns:
        numpy array: Cosine wave signal
    """
    y = A * np.cos(2 * np.pi * f * t + phi)
    plt.plot(t, y)
    plt.title(f"Cosine Wave: A={A}, f={f}Hz, phi={phi} rad")
    plt.xlabel("Time (s)")
    plt.ylabel("Amplitude")
    plt.grid(True)
    plt.show()
    return y


def exponential_signal(A, a, t):
    """
    Generates an exponential signal.
    Args:
        A (float): Amplitude
        a (float): Exponential rate
        t (numpy array): Time vector
    Returns:
        numpy array: Exponential signal
    """
    y = A * np.exp(a * t)
    plt.plot(t, y)
    plt.title(f"Exponential Signal: A={A}, a={a}")
    plt.xlabel("Time (s)")
    plt.ylabel("Amplitude")
    plt.grid(True)
    plt.show()
    return y


# Example usage
if __name__ == "__main__":
    t = np.linspace(0, 1, 500)  # time vector from 0 to 1 sec, 500 samples
    
    sine_wave(A=1, f=5, phi=0, t=t)      # 5 Hz sine
    cosine_wave(A=1, f=5, phi=0, t=t)    # 5 Hz cosine
    exponential_signal(A=1, a=-2, t=t)   # decaying exponential
