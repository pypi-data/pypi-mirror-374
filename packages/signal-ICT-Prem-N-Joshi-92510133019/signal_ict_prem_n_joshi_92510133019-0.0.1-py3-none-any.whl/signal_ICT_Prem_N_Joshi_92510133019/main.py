import numpy as np
import matplotlib.pyplot as plt

from signal_ICT_Prem_N_Joshi_92510133019 import (
    unit_step, unit_impulse, ramp_signal,
    sine_wave, cosine_wave, exponential_signal,
    time_shift, time_scale, signal_addition, signal_multiplication
)

def main():
    # Generate signals
    u = unit_step(20, show=True)
    d = unit_impulse(20, k=0, show=True)
    r = ramp_signal(20, show=True)

    t = np.linspace(0, 1, 1000, endpoint=False)
    s = sine_wave(A=2, f=5, phi=0, t=t, show=True)
    c = cosine_wave(A=2, f=5, phi=0, t=t, show=True)
    e = exponential_signal(A=1, a=0.1, t=t, show=True)

    # Operations
    shifted = time_shift(s, 5, show=True)
    scaled = time_scale(s, 2, show=True)
    added = signal_addition(s, c, show=True)
    multiplied = signal_multiplication(s, c, show=True)

    # Save plots
    import os
    os.makedirs("plots", exist_ok=True)
    for i, num in enumerate(plt.get_fignums(), start=1):
        fig = plt.figure(num)
        fig.savefig(os.path.join("plots", f"figure_{i}.png"))
    print("✅ All signals generated and plots saved in 'plots/'.")

    plt.show()

if __name__ == "__main__":
    main()
