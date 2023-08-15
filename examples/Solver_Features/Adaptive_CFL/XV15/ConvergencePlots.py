import matplotlib.pyplot as plt
from collections import defaultdict
import os, csv, json
import numpy as np
import pandas as pd

def addAccumPseudoStep(history):
    pseudoSteps = history['pseudo_step']
    accum = list()
    accum.append(0)
    for i in range(1,len(pseudoSteps)):
        if pseudoSteps[i] > pseudoSteps[i-1]:
            accum.append(accum[-1]+abs(pseudoSteps[i] - pseudoSteps[i-1]))
        else:
            accum.append(accum[-1]+1)
    history['accum_pseudo_step'] = accum


def plotResiduals(res, caseName, plotName):
    x = res['accum_pseudo_step']
    keys = ['0_cont', '1_momx', '2_momy', '3_momz', '4_energ', '5_nuHat']
    labels = ['Cont Residual', 'Momx Residual', 'Momy Residual', 'Momz Residual', 'Energy Residual', 'nuHat Residual']
    for ax, key, label in  zip(axes, keys, labels):
        for j, key in enumerate(keys):
            if plotName =="Ramp":
                ax.semilogy(x, res[key], label = plotName + ' ' + labels[j])
            else:
                ax.semilogy(x, res[key], "--", label = plotName + ' ' + labels[j])
        ax.legend(loc='upper right')
        ax.grid(which='major', color='gray')

        ax.set_title("XV15 Rotor - Residuals")
        ax.set_xlabel('Accumulated Pseudo step');
        ax.set_yticks(10.0**np.arange(-11,-3));
        ax.set_ylim([1e-9,1e-3])
        ax.set_xlim([3000,4000])
        ax.set_ylabel('Residuals')


caseNameList = ["XV15_2nd_order_ramp_forked", "XV15_2nd_order_adaptive_forked"]
naming= ["Ramp", "Adaptive"]
figures = []
axes = []

def main():
    fig, ax = plt.subplots(figsize=(8,6))
    figures.append(fig)
    axes.append(ax)
    dir_path= os.path.join(os.getcwd(),f'figures')
    if not os.path.isdir(dir_path): # if directory already exists:
        os.makedirs(dir_path) # make that dir

    for j, resolution in enumerate(caseNameList):
        csvPath = os.path.join(os.getcwd(),f'{resolution}','nonlinear_residual_v2.csv')
        res = pd.read_csv(csvPath, skipinitialspace=True)
        addAccumPseudoStep(res)
        plotResiduals(res, resolution, naming[j])
        figures[0].gca().set_prop_cycle(None)
        figures[0].savefig(f'figures/Residuals.png', dpi=500);
        axes[0].set_xlim([3450,3550])
        figures[0].savefig(f'figures/ResidualsZoomed.png', dpi=500);

    caseNameList2 = ["XV15_2nd_order_adaptive"]
    naming2= ["Adaptive"]
    for ax in axes:
        ax.cla();

    for j, resolution in enumerate(caseNameList2):
        csvPath = os.path.join(os.getcwd(),f'{resolution}','nonlinear_residual_v2.csv')
        res = pd.read_csv(csvPath, skipinitialspace=True)
        addAccumPseudoStep(res)
        plotResiduals(res, resolution, naming2[j])
        axes[0].set_xlim([0,4000])
        figures[0].savefig(f'figures/Residuals_Adaptive_from_scratch.png', dpi=500);

if __name__ == '__main__':
    main()

