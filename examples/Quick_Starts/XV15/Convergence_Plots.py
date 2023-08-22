import matplotlib.pyplot as plt
from collections import defaultdict
import os, csv
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


def plotLoads(data, plotName):
    axes[0].plot(data['accum_pseudo_step'], data['CFz'], label=plotName)
    axes[1].plot(data['accum_pseudo_step'], data['CMz'], label=plotName)
    axes[0].set_ylabel('CFz');
    axes[1].set_ylabel('CMz');
    #axes[0].set_ylim(0.255, 0.265);
    #axes[1].set_ylim(0.0203, 0.0212);

    for ax in axes:
            ax.legend()
            ax.set_xlabel('Pseudo step');
            ax.grid(which='major', color='gray')

def plotResiduals(res, plotName):
    x = res['accum_pseudo_step']
    keys = ['0_cont', '1_momx', '2_momy', '3_momz', '4_energ', '5_nuHat']
    labels = ['Cont Residual', 'Momx Residual', 'Momy Residual', 'Momz Residual', 'Energy Residual', 'nuHat Residual']
    for ax, key, label in  zip(axes, keys, labels):
        for j, key in enumerate(keys):
                ax.semilogy(x, res[key], label = plotName + ' ' + labels[j])
        ax.set_ylabel('Residuals')
        ax.legend()
        ax.set_title("XV-15 - Quickstart")
        ax.grid(which='major', color='gray')
        ax.set_xlabel('Pseudo step');
        ax.set_yticks(10.0**np.arange(-14,-3));
        ax.set_ylim([1e-9,1e-2])
        ax.set_xlim([0,7000])

with open('caseNameList.dat', 'r') as file:
        caseNameList = file.read().splitlines()

naming = ["XV15"]
figures = []
axes = []

def main():

    #Plot loads convergence histories
        for i in [0,1]:
            fig, ax = plt.subplots(figsize=(8,6))
            figures.append(fig)
            axes.append(ax)
        dir_path= os.path.join(os.getcwd(),f'figures')
        if not os.path.isdir(dir_path): # if directory already exists:
            os.makedirs(dir_path) # make that dir

        for j, resolution in enumerate(caseNameList):

                csvPath = os.path.join(os.getcwd(),f'{resolution}','total_forces_v2.csv')
                data = pd.read_csv(csvPath, skipinitialspace=True)
                addAccumPseudoStep(data)
                plotLoads(data, naming[j])
                

        figures[0].savefig(f'figures/CFz.png', dpi=500);
        figures[1].savefig(f'figures/CMz.png', dpi=500);

        for i in range(0,2):
            axes[i].cla();
        
        #Plot residual convergence histories
        fig, ax = plt.subplots(figsize=(8,6))
        figures.append(fig)
        axes.append(ax)
        for j, resolution in enumerate(caseNameList):
                csvPath = os.path.join(os.getcwd(),f'{resolution}', 'nonlinear_residual_v2.csv')
                res = pd.read_csv(csvPath, skipinitialspace=True)
                addAccumPseudoStep(res)
                plotResiduals(res, naming[j])
        
        figures[0].savefig(f'figures/Residuals.png', dpi=500);



if __name__ == '__main__':
    main()

