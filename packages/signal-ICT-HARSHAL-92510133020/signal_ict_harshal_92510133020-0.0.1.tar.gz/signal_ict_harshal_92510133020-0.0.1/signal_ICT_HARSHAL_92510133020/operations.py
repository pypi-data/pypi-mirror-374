# operations.py

import numpy as np
import matplotlib.pyplot as plt

def time_shift(signal, n, k):
    """
    Shifts the signal by k units in time.
    Args:
        signal (numpy array): Input signal
        n (numpy array): Time indices
        k (int): Shift amount (positive = delay, negative = advance)
    Returns:
        (n_shifted, signal_shifted)
    """
    n_shifted = n + k
    plt.stem(n_shifted, signal)
    plt.title(f"Time-Shifted Signal (k={k})")
    plt.xlabel("n")
    plt.ylabel("Amplitude")
    plt.grid(True)
    plt.show()
    return n_shifted, signal


def time_scale(signal, n, k):
    """
    Scales the time axis by factor k.
    Args:
        signal (numpy array): Input signal
        n (numpy array): Time indices
        k (int): Scaling factor (k>1 = compression, 0<k<1 = expansion)
    Returns:
        (n_scaled, signal_scaled)
    """
    n_scaled = n * k
    plt.stem(n_scaled, signal)
    plt.title(f"Time-Scaled Signal (k={k})")
    plt.xlabel("n")
    plt.ylabel("Amplitude")
    plt.grid(True)
    plt.show()
    return n_scaled, signal


def signal_addition(signal1, signal2):
    """
    Adds two signals (point-wise).
    Args:
        signal1 (numpy array): First signal
        signal2 (numpy array): Second signal (same length as signal1)
    Returns:
        numpy array: Added signal
    """
    y = signal1 + signal2
    plt.stem(range(len(y)), y)
    plt.title("Signal Addition")
    plt.xlabel("n")
    plt.ylabel("Amplitude")
    plt.grid(True)
    plt.show()
    return y


def signal_multiplication(signal1, signal2):
    """
    Multiplies two signals (point-wise).
    Args:
        signal1 (numpy array): First signal
        signal2 (numpy array): Second signal (same length as signal1)
    Returns:
        numpy array: Multiplied signal
    """
    y = signal1 * signal2
    plt.stem(range(len(y)), y)
    plt.title("Signal Multiplication")
    plt.xlabel("n")
    plt.ylabel("Amplitude")
    plt.grid(True)
    plt.show()
    return y


# Example usage
if __name__ == "__main__":
    n = np.arange(-5, 6)
    x1 = np.where(n >= 0, 1, 0)   # unit step
    x2 = np.where(n == 0, 1, 0)   # unit impulse

    # Time shift
    time_shift(x1, n, k=2)

    # Time scale
    time_scale(x1, n, k=2)

    # Addition
    signal_addition(x1, x2)

    # Multiplication
    signal_multiplication(x1, x2)
