
import numpy as np
import matplotlib.pyplot as plt

from signal_ICT_Prem.N.Joshi_92510133019.unitary_signals import unit_step, unit_impulse, ramp_signal
from signal_ICT_Prem.N.Joshi_92510133019.trigonometric_signals import sine_wave, cosine_wave, exponential_signal
from signal_ICT_Prem.N.Joshi_92510133019.operations import time_shift, time_scale, signal_addition, signal_multiplication

def main():
    # 1. Generate and plot a unit step and unit impulse of length 20
    n = 20
    u = unit_step(n, show=True)
    d = unit_impulse(n, k=0, show=True)

    # 2. Generate sine wave A=2, f=5Hz, phi=0 over t=[0,1]
    fs = 1000  # sample rate for smooth plotting
    t = np.linspace(0, 1, fs, endpoint=False)
    s = sine_wave(A=2, f=5, phi=0, t=t, show=True)

    # 3. Time shifting on the sine wave by +5 samples
    # To apply discrete shift, convert sine to discrete samples first
    s_disc = s.copy()
    s_shifted = time_shift(s_disc, k=5, show=True)

    # 4. Addition of unit step and ramp
    r = ramp_signal(n, show=True)
    add = signal_addition(u, r, show=True)

    # 5. Multiply sine and cosine wave of same frequency
    c = cosine_wave(A=2, f=5, phi=0, t=t, show=False)  # don't show individually
    mul = signal_multiplication(s, c, show=True)

    # Save all open figures
    import os
    os.makedirs("plots", exist_ok=True)
    for i, num in enumerate(plt.get_fignums(), start=1):
        fig = plt.figure(num)
        fig.savefig(os.path.join("plots", f"figure_{i}.png"))
    print("All plots saved to ./plots")

if __name__ == "__main__":
    main()
