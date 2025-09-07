import numpy as np
import matplotlib.pyplot as plt
import os

PLOTS_DIR = "plots"
os.makedirs(PLOTS_DIR, exist_ok=True)

def sine(A=1, f=5, phi=0, length=100, fs=100):
    n = np.arange(length)
    t = n / fs
    x = A * np.sin(2 * np.pi * f * t + phi)
    plt.plot(t, x)
    plt.title(f"Sine Signal: A={A}, f={f}, phi={phi}")
    plt.xlabel("t")
    plt.ylabel("x(t)")
    filename = os.path.join(PLOTS_DIR, f"sine_A{A}_f{f}_phi{phi}.png")
    plt.savefig(filename)
    plt.close()
    return t, x

def cosine(A=1, f=5, phi=0, length=100, fs=100):
    n = np.arange(length)
    t = n / fs
    x = A * np.cos(2 * np.pi * f * t + phi)
    plt.plot(t, x)
    plt.title(f"Cosine Signal: A={A}, f={f}, phi={phi}")
    plt.xlabel("t")
    plt.ylabel("x(t)")
    filename = os.path.join(PLOTS_DIR, f"cosine_A{A}_f{f}_phi{phi}.png")
    plt.savefig(filename)
    plt.close()
    return t, x

def exponential_signal(A, a, t):
    signal = A * np.exp(a * t)
    plt.plot(t, signal)
    plt.title("Exponential Signal")
    plt.xlabel("Time (s)")
    plt.ylabel("Amplitude")
    plt.grid(True)
    filename = os.path.join(PLOTS_DIR, f"exponential_A{A}_a{a}.png")
    plt.savefig(filename)
    plt.show()
    return signal