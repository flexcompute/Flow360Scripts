import matplotlib.pyplot as plt
from collections import defaultdict
import os, csv
import numpy as np
import pandas as pd


with open('caseNameList.dat', 'r') as file:
    caseNameList = file.read().splitlines()

naming = ["Wall Resolved", "Wall Modeled"]
figures = []
axes = []


def computeCLCD(data):
    CL0 = np.add(data['Windsor_CL'], data['Windsor_rear_CL'])
    data['CL'] = np.add(data['Windsor_supports_CL'], CL0)
    CD0 = np.add(data['Windsor_CD'], data['Windsor_rear_CD'])
    data['CD'] = np.add(data['Windsor_supports_CD'], CD0)
     

def plotLoads(data, plotName):
    x = data['pseudo_step']
    keys = ['CL', 'CD']
    for ax, key in zip(axes, keys):
        ax.plot(x, data[key], label=plotName)
        ax.set_ylabel(key)
        ax.legend()
        ax.set_xlabel('Pseudo step')
        ax.grid(which='major', color='gray')
        if key == 'CL':
            ax.set_ylim(-0.2, -0.1)
        elif key == 'CD':
            ax.set_ylim(0.25, 0.45)


def plotResiduals(res, plotName):
    x = res['pseudo_step']
    keys = ['0_cont', '1_momx', '2_momy', '3_momz', '4_energ', '5_nuHat']
    labels = ['Cont Residual', 'Momx Residual', 'Momy Residual', 'Momz Residual', 'Energy Residual', 'nuHat Residual']
    for ax, key, label in zip(axes, keys, labels):
        ax.semilogy(x, res[key], label=plotName)
        ax.set_ylabel(label)
        ax.legend()
        ax.grid(which='major', color='gray')
        ax.set_xlabel('Pseudo step')
        ax.set_yticks(10.0**np.arange(-14, -3))
        ax.set_ylim([1e-13, 1e-3])
        ax.set_xlim([0, 10000])


def main():
    # plot loads convergence histories
    for i in [0, 1]:
        fig, ax = plt.subplots(figsize=(8, 6))
        figures.append(fig)
        axes.append(ax)
    dir_path = os.path.join(os.getcwd(), f'figures')
    if not os.path.isdir(dir_path):
        os.makedirs(dir_path)

    for j, resolution in enumerate(caseNameList):
        csvPath = os.path.join(os.getcwd(), f'{resolution}', 'surface_forces_v2.csv')
        data = pd.read_csv(csvPath, skipinitialspace=True)
        computeCLCD(data)
        plotLoads(data, naming[j])

    figures[0].savefig(f'figures/CL.png', dpi=500)
    figures[1].savefig(f'figures/CD.png', dpi=500)

    for ax in axes:
        ax.cla()

    # plot residual convergence histories
    for i in range(0, 6):
        fig, ax = plt.subplots(figsize=(8, 6))
        figures.append(fig)
        axes.append(ax)
    for j, resolution in enumerate(caseNameList):
        csvPath = os.path.join(os.getcwd(), f'{resolution}', 'nonlinear_residual_v2.csv')
        res = pd.read_csv(csvPath, skipinitialspace=True)
        plotResiduals(res, naming[j])

    figures[0].savefig(f'figures/Cont.png', dpi=500)
    figures[1].savefig(f'figures/Momx.png', dpi=500)
    figures[2].savefig(f'figures/Momy.png', dpi=500)
    figures[3].savefig(f'figures/Momz.png', dpi=500)
    figures[4].savefig(f'figures/Energy.png', dpi=500)
    figures[5].savefig(f'figures/nuHat.png', dpi=500)


if __name__ == '__main__':
    main()

