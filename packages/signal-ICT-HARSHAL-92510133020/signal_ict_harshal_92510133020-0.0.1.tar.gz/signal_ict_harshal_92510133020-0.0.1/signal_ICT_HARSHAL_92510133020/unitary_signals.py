# unitary_signals.py

import numpy as np
import matplotlib.pyplot as plt

def unit_step(n):
    """
    Generates a unit step signal.
    Args:
        n (numpy array): Discrete time index
    Returns:
        numpy array: Unit step signal
    """
    u = np.where(n >= 0, 1, 0)
    plt.stem(n, u)
    plt.title("Unit Step Signal")
    plt.xlabel("n")
    plt.ylabel("u[n]")
    plt.grid(True)
    plt.show()
    return u

def unit_impulse(n):
    """
    Generates a unit impulse signal.
    Args:
        n (numpy array): Discrete time index
    Returns:
        numpy array: Unit impulse signal
    """
    d = np.where(n == 0, 1, 0)
    plt.stem(n, d)
    plt.title("Unit Impulse Signal")
    plt.xlabel("n")
    plt.ylabel("δ[n]")
    plt.grid(True)
    plt.show()
    return d

def ramp_signal(n):
    """
    Generates a ramp signal.
    Args:
        n (numpy array): Discrete time index
    Returns:
        numpy array: Ramp signal
    """
    r = np.where(n >= 0, n, 0)
    plt.stem(n, r)
    plt.title("Ramp Signal")
    plt.xlabel("n")
    plt.ylabel("r[n]")
    plt.grid(True)
    plt.show()
    return r

# Example usage
if __name__ == "__main__":
    n = np.arange(-10, 11)  # discrete range from -10 to 10
    unit_step(n)
    unit_impulse(n)
    ramp_signal(n)
