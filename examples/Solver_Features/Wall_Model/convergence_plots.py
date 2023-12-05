"""Plot the loads and residuals convergence plots for the wall-resolved and wall-modeled cases"""

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


def compute_cl_cd(data):
    """Compute the Windsor body lift and drag from surface forces"""

    cl_0 = np.add(data["Windsor_CL"], data["Windsor_rear_CL"])
    data["CL"] = np.add(data["Windsor_supports_CL"], cl_0)
    cd_0 = np.add(data["Windsor_CD"], data["Windsor_rear_CD"])
    data["CD"] = np.add(data["Windsor_supports_CD"], cd_0)


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
            ax.set_ylim(-0.2, -0.1)
        elif load == "CD":
            ax.set_ylim(0.25, 0.45)


def plot_residuals(data, plot_name):
    """Plot the residuals"""

    x = data["pseudo_step"]
    for ax, res in zip(axes, residuals):
        ax.semilogy(x, data[res], label=plot_name)
        ax.set_ylabel(res)
        ax.legend()
        ax.grid(which="major", color="gray")
        ax.set_xlabel("Pseudo step")
        ax.set_yticks(10.0 ** np.arange(-14, -3))
        ax.set_ylim([1e-13, 1e-3])
        ax.set_xlim([0, 10000])


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
    csv_path = os.path.join(os.getcwd(), f"{case_name}", "surface_forces_v2.csv")
    data = pd.read_csv(csv_path, skipinitialspace=True)
    compute_cl_cd(data)
    plot_loads(data, case_name)

# save loads figures
for i, load in enumerate(loads):
    figures[i].savefig(os.path.join(dir_path, load + ".png"), dpi=500)

for ax in axes:
    ax.cla()

# plot residual convergence histories
for res in residuals:
    fig, ax = plt.subplots(figsize=(8, 6))
    figures.append(fig)
    axes.append(ax)

for case_name in case_name_list:
    csv_path = os.path.join(os.getcwd(), case_name, "nonlinear_residual_v2.csv")
    data = pd.read_csv(csv_path, skipinitialspace=True)
    plot_residuals(data, case_name)
for i, res in enumerate(residuals):
    figures[i].savefig(os.path.join(dir_path, res + ".png"), dpi=500)
