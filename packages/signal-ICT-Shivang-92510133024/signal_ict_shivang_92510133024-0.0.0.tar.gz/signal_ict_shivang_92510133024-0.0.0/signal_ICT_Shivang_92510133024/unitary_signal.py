import numpy as np
import matplotlib.pyplot as plt
import os

PLOTS_DIR = "plots"
os.makedirs(PLOTS_DIR, exist_ok=True)

def unit_step(length=20):
    n = np.arange(length)
    x = np.heaviside(n, 1)
    plt.stem(n, x)
    plt.title("Unit Step Signal")
    plt.xlabel("n")
    plt.ylabel("x[n]")
    filename = os.path.join(PLOTS_DIR, f"unit_step_len{length}.png")
    plt.savefig(filename)
    plt.close()
    return n, x

def unit_impulse(length=20):
    n = np.arange(length)
    x = np.zeros(length)
    x[0] = 1
    plt.stem(n, x)
    plt.title("Unit Impulse Signal")
    plt.xlabel("n")
    plt.ylabel("δ[n]")
    filename = os.path.join(PLOTS_DIR, f"unit_impulse_len{length}.png")
    plt.savefig(filename)
    plt.close()
    return n, x

def ramp_signal(length=20):
    n = np.arange(length)
    x = n  
    plt.stem(n, x)
    plt.title("Ramp Signal")
    plt.xlabel("n")
    plt.ylabel("Amplitude")
    plt.grid(True)
    filename = os.path.join(PLOTS_DIR, f"ramp_signal_len{length}.png")
    plt.savefig(filename)
    plt.close()
    return n, x