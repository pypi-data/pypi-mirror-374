import numpy as np
import matplotlib.pyplot as plt
import os

PLOTS_DIR = "plots"
os.makedirs(PLOTS_DIR, exist_ok=True)

def signal_addition(x1, x2):
    n = np.arange(len(x1))
    y = x1 + x2
    plt.plot(n, x1, label="x1")
    plt.plot(n, x2, label="x2")
    plt.plot(n, y, label="x1+x2")
    plt.legend()
    plt.title("Signal Addition")
    filename = os.path.join(PLOTS_DIR, "signal_addition.png")
    plt.savefig(filename)
    plt.close()
    return y

def signal_multiplication(x1, x2):
    n = np.arange(len(x1))
    y = x1 * x2
    plt.plot(n, x1, label="x1")
    plt.plot(n, x2, label="x2")
    plt.plot(n, y, label="x1*x2")
    plt.legend()
    plt.title("Signal Multiplication")
    filename = os.path.join(PLOTS_DIR, "signal_multiplication.png")
    plt.savefig(filename)
    plt.close()
    return y

def time_shift(x, k):
    n = np.arange(len(x))
    y = np.roll(x, k)
    plt.plot(n, x, label="Original")
    plt.plot(n, y, label=f"Shifted by {k}")
    plt.legend()
    plt.title("Time Shifting")
    filename = os.path.join(PLOTS_DIR, f"time_shift_{k}.png")
    plt.savefig(filename)
    plt.close()
    return y

def time_scale(signal, k):
    scaled = signal[::k] if k > 0 else signal
    plt.plot(signal, label="Original")
    plt.plot(np.arange(0, len(scaled) * k, k), scaled, label=f"Scaled by {k}")
    plt.title("Time Scaling Operation")
    plt.xlabel("n")
    plt.ylabel("Amplitude")
    plt.legend()
    plt.grid(True)
    filename = os.path.join(PLOTS_DIR, f"time_scale_{k}.png")
    plt.show()
    return scaled