"""Plot the residuals convergence plots for the ramp and adaptive CFL cases"""

import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

with open("case_name_list.dat", "r", encoding="utf-8") as file:
    case_name_list = file.read().splitlines()

residuals = ["0_cont", "1_momx", "2_momy", "3_momz", "4_energ", "5_nuHat"]
figures = []
axes = []


def add_accum_pseudo_step(history):
    "Compute the accumulated pseudo-step"
    pseudo_steps = history["pseudo_step"]
    accum = []
    accum.append(0)
    for i in range(1, len(pseudo_steps)):
        if pseudo_steps[i] > pseudo_steps[i - 1]:
            accum.append(accum[-1] + abs(pseudo_steps[i] - pseudo_steps[i - 1]))
        else:
            accum.append(accum[-1] + 1)
    history["accum_pseudo_step"] = accum


def plot_residuals(data, plot_name):
    "Plot the residuals"
    x = data["accum_pseudo_step"]
    for ax, res in zip(axes, residuals):
        for res in residuals:
            if "ramp" in plot_name:
                ax.semilogy(x, data[res], label=plot_name + " " + res)
            else:
                ax.semilogy(x, data[res], "--", label=plot_name + " " + res)

        ax.legend(loc="upper right")
        ax.grid(which="major", color="gray")
        ax.set_title("XV15 Rotor - Residuals")
        ax.set_xlabel("Accumulated Pseudo step")
        ax.set_yticks(10.0 ** np.arange(-11, -3))
        ax.set_ylim([1e-9, 1e-3])
        ax.set_xlim([3000, 4000])
        ax.set_ylabel("Residuals")


# set output directory
dir_path = os.path.join(os.getcwd(), "figures")
os.makedirs(dir_path, exist_ok=True)

fig, ax = plt.subplots(figsize=(8, 6))
figures.append(fig)
axes.append(ax)

for case_name in case_name_list:
    if "2nd_order" in case_name:
        if "adaptive" in case_name:
            figures[0].gca().set_prop_cycle(None)
        csv_path = os.path.join(os.getcwd(), case_name, "nonlinear_residual_v2.csv")
        data = pd.read_csv(csv_path, skipinitialspace=True)
        add_accum_pseudo_step(data)
        plot_residuals(data, case_name)
figures[0].savefig(os.path.join(dir_path, "residuals.png"), dpi=500)
axes[0].set_xlim([3450, 3550])
figures[0].savefig("figures/residuals_zoomed.png", dpi=500)
