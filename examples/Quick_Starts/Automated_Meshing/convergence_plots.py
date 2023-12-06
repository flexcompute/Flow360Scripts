"""Plot the loads and residuals convergence plots for ONERA M6 quick-start"""

import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

with open("case_name_list.dat", "r", encoding="utf-8") as file:
    case_name_list = file.read().splitlines()

loads = ["CL", "CD"]
residuals = ["0_cont", "1_momx", "2_momy", "3_momz", "4_energ", "5_nuHat"]
figures = []
axes = []


def plot_loads(data, plot_name):
    """Plot the loads"""
    x = data["pseudo_step"]
    for ax, load in zip(axes, loads):
        ax.plot(x, data[load], label=plot_name)
        ax.set_ylabel(load)
        ax.legend()
        ax.set_xlabel("Pseudo step")
        ax.grid(which="major", color="gray")
        if load == "CL":
            ax.set_ylim(0.27, 0.28)
        elif load == "CD":
            ax.set_ylim(0.017, 0.018)


def plot_residuals(data, plot_name):
    """Plot the residuals"""
    x = data["pseudo_step"]
    for ax, res in zip(axes, residuals):
        for res in residuals:
            ax.semilogy(x, data[res], label=plot_name + " " + res)
        ax.set_ylabel("Residuals")
        ax.legend(fontsize="8")
        ax.set_title("ONERAM6 - Automated Meshing Quick-Start")
        ax.grid(which="major", color="gray")
        ax.set_xlabel("Pseudo step")
        ax.set_yticks(10.0 ** np.arange(-14, -2))
        ax.set_ylim([1e-7, 1e-2])
        ax.set_xlim([0, 5000])


# set output directory
dir_path = os.path.join(os.getcwd(), "figures")
os.makedirs(dir_path, exist_ok=True)

# initialize figures & axes
for load in loads:
    fig, ax = plt.subplots(figsize=(8, 6))
    figures.append(fig)
    axes.append(ax)

# calculate and plot loads convergence histories
for case_name in case_name_list:
    csv_path = os.path.join(os.getcwd(), f"{case_name}", "total_forces_v2.csv")
    data = pd.read_csv(csv_path, skipinitialspace=True)
    plot_loads(data, case_name)

for i, load in enumerate(loads):
    figures[i].savefig(os.path.join(dir_path, load + ".png"), dpi=500)

for ax in axes:
    ax.cla()


# plot residual convergence histories
fig, ax = plt.subplots(figsize=(8, 6))
figures.append(fig)
axes.append(ax)

for case_name in case_name_list:
    csv_path = os.path.join(os.getcwd(), case_name, "nonlinear_residual_v2.csv")
    data = pd.read_csv(csv_path, skipinitialspace=True)
    plot_residuals(data, case_name)

figures[0].savefig(os.path.join(dir_path, "Residuals.png"), dpi=500)
