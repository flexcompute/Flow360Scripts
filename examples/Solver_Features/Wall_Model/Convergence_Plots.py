import matplotlib.pyplot as plt
from collections import defaultdict
import os, csv
import numpy as np
import pandas as pd

with open('caseNameList.dat', 'r') as file:
    caseNameList = file.read().splitlines()

loads = ['CL', 'CD']
residuals = ['0_cont', '1_momx', '2_momy', '3_momz', '4_energ', '5_nuHat']
figures = []
axes = []


def computeCLCD(data):
    CL0 = np.add(data['Windsor_CL'], data['Windsor_rear_CL'])
    data['CL'] = np.add(data['Windsor_supports_CL'], CL0)
    CD0 = np.add(data['Windsor_CD'], data['Windsor_rear_CD'])
    data['CD'] = np.add(data['Windsor_supports_CD'], CD0)
     

def plotLoads(data, plotName):
    x = data['pseudo_step']
    for ax, load in zip(axes, loads):
        ax.plot(x, data[load], label=plotName)
        ax.set_ylabel(load)
        ax.legend()
        ax.set_xlabel('Pseudo step')
        ax.grid(which='major', color='gray')
        if load == 'CL':
            ax.set_ylim(-0.2, -0.1)
        elif load == 'CD':
            ax.set_ylim(0.25, 0.45)


def plotResiduals(data, plotName):
    x = data['pseudo_step']
    for ax, res in zip(axes, residuals):
        ax.semilogy(x, data[res], label=plotName)
        ax.set_ylabel(res)
        ax.legend()
        ax.grid(which='major', color='gray')
        ax.set_xlabel('Pseudo step')
        ax.set_yticks(10.0**np.arange(-14, -3))
        ax.set_ylim([1e-13, 1e-3])
        ax.set_xlim([0, 10000])


def main():
    # set output directory
    dir_path = os.path.join(os.getcwd(), 'figures')
    os.makedirs(dir_path, exist_ok=True)

    # initialize figures & axes
    for load in loads:
        fig, ax = plt.subplots(figsize=(8, 6))
        figures.append(fig)
        axes.append(ax)

    # calculate and plot loads convergence histories
    for caseName in caseNameList:
        csvPath = os.path.join(os.getcwd(), caseName, 'surface_forces_v2.csv')
        data = pd.read_csv(csvPath, skipinitialspace=True)
        computeCLCD(data)
        plotLoads(data, caseName)

    # save loads figures
    for i, load in enumerate(loads):
        figures[i].savefig(os.path.join(dir_path, load + '.png'), dpi=500)

    for ax in axes:
        ax.cla()

    # plot residual convergence histories
    for res in residuals:
        fig, ax = plt.subplots(figsize=(8, 6))
        figures.append(fig)
        axes.append(ax)
    for caseName in caseNameList:
        csvPath = os.path.join(os.getcwd(), caseName, 'nonlinear_residual_v2.csv')
        data = pd.read_csv(csvPath, skipinitialspace=True)
        plotResiduals(data, caseName)
    for i, res in enumerate(residuals):
        figures[i].savefig(os.path.join(dir_path, res + '.png'), dpi=500)


if __name__ == '__main__':
    main()
