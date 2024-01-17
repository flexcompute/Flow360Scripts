"""Plot the sectional loads for the ONERA M6 wing automeshing quick-start case"""

import os

import matplotlib.pyplot as plt
import pandas as pd
from flow360 import MyCases

with open("case_name_list.dat", "r", encoding="utf-8") as file:
    case_name_list = file.read().splitlines()

loads = ["wing_CFx_per_span", "wing_CFz_per_span"]
figures = []
axes = []


def plot_sectional_forces(data, plot_name):
    """Plots the sectional loads"""
    for ax, load in zip(axes, loads):
        ax.plot(data["Y"], data["fluid/" + load], label=plot_name)
        ax.set_ylabel(load)
        ax.legend()
        ax.set_xlabel("Y")
        ax.grid(which="major", color="gray")


case = None
my_cases = MyCases(limit=None)

for case_name in case_name_list:
    case_folder = os.path.join(os.getcwd(), case_name)
    os.makedirs(case_folder, exist_ok=True)
    # Find the latest case with the name corresponding to the name in caseNameList
    for case in my_cases:
        if case.name == case_name:
            break
    print(case.name)
    forces = "results/postprocess/forceDistribution.csv"
    # print(case.results)
    case._download_file(forces, to_folder=case_folder)

# set output directory
dir_path = os.path.join(os.getcwd(), "figures")
os.makedirs(dir_path, exist_ok=True)

# initialize figures & axes
for load in loads:
    fig, ax = plt.subplots(figsize=(8, 6))
    figures.append(fig)
    axes.append(ax)

for case_name in case_name_list:
    csv_path = os.path.join(os.getcwd(), f"{case_name}", "forceDistribution.csv")
    data = pd.read_csv(csv_path, skipinitialspace=True)
    plot_sectional_forces(data, case_name)

for i, load in enumerate(loads):
    figures[i].savefig(os.path.join(dir_path, load + ".png"), dpi=500)
