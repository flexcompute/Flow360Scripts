import matplotlib.pyplot as plt
from collections import defaultdict
import os, csv
import numpy as np
import pandas as pd


     

def plotLoads(data, plotName):
    axes[0].plot(data['pseudo_step'], data['CL'], label=plotName)
    axes[1].plot(data['pseudo_step'], data['CD'], label=plotName)
    axes[0].set_ylabel('CL');
    axes[1].set_ylabel('CD');
#    axes[0].set_ylim(0.25, 0.3);
#    axes[1].set_ylim(0.0, 0.05);

    for ax in axes:
            ax.legend()
            ax.set_xlabel('Pseudo step');
            ax.grid(which='major', color='gray')

def plotResiduals(res, plotName):
    x = res['pseudo_step']
    keys = ['0_cont', '1_momx', '2_momy', '3_momz', '4_energ', '5_nuHat']
    labels = ['Cont Residual', 'Momx Residual', 'Momy Residual', 'Momz Residual', 'Energy Residual', 'nuHat Residual']
    for ax, key, label in  zip(axes, keys, labels):
        for j, key in enumerate(keys):
            if plotName =="Ramp":
                ax.semilogy(x, res[key], label = plotName + ' ' + labels[j])
            else: 
                ax.semilogy(x, res[key], "--", label = plotName + ' ' + labels[j])
        ax.set_ylabel('Residuals')
        ax.legend()
        ax.set_title("ONERAM6 10.0 deg")
        ax.grid(which='major', color='gray')
        ax.set_xlabel('Pseudo step');
        ax.set_yticks(10.0**np.arange(-14,-3));
        ax.set_ylim([1e-10,1e-3])
        ax.set_xlim([0,8000])

with open('caseNameList.dat', 'r') as file:
        caseNameList = file.read().splitlines()

naming = ["Ramp", "Adaptive", "Ramp", "Adaptive"]
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
            if "10" in resolution:
                csvPath = os.path.join(os.getcwd(),f'{resolution}','total_forces_v2.csv')
                data = pd.read_csv(csvPath, skipinitialspace=True)
                plotLoads(data, naming[j])
                

        figures[0].savefig(f'figures/CL_AoA10.png', dpi=500);
        figures[1].savefig(f'figures/CD_AoA10.png', dpi=500);

        for i in range(0,2):
            axes[i].cla();
        
        #Plot residual convergence histories
        fig, ax = plt.subplots(figsize=(8,6))
        figures.append(fig)
        axes.append(ax)
        for j, resolution in enumerate(caseNameList):
            if "10" in resolution:
                if "ADAPTIVE" in resolution:
                    figures[0].gca().set_prop_cycle(None)
                csvPath = os.path.join(os.getcwd(),f'{resolution}','nonlinear_residual_v2.csv')
                res = pd.read_csv(csvPath, skipinitialspace=True)
                plotResiduals(res, naming[j])
        
        figures[0].savefig(f'figures/Residuals_AoA10.png', dpi=500);



if __name__ == '__main__':
    main()

