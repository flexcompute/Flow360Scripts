import os, csv
import numpy as np
import flow360 as fl
import pandas as pd
from flow360 import MyCases
import matplotlib.pyplot as plt
from collections import defaultdict



def plotSectionalForces(data, plotName):
    axes[0].plot(data['Y'], data['wing_CFx_per_span'], label=plotName)
    axes[1].plot(data['Y'], data['wing_CFz_per_span'], label=plotName)
    axes[0].set_ylabel('CFx per span');
    axes[1].set_ylabel('CFz per span');
    for ax in axes:
            ax.legend()
            ax.set_xlabel('Y');
            ax.grid(which='major', color='gray')



#read in caseNameList

with open('caseNameList.dat', 'r') as file:
        caseNameList = file.read().splitlines()

my_cases = MyCases()

naming = ["ONERAM6"]
figures = []
axes = []


def main():

    for i in range(0, len(caseNameList)):
        caseFolder = os.path.join(os.getcwd(), caseNameList[i])
        os.makedirs(caseFolder, exist_ok = True)
        #Find the latest case with the name corresponding to the name in caseNameList
        for case in my_cases:
            if case.name == caseNameList[i]:
                break
        forces = f"results/postprocess/forceDistribution.csv"
        #print(case.results)
        case._download_file(forces, to_folder=caseFolder)

    for i in [0,1]:
        fig, ax = plt.subplots(figsize=(8,6))
        figures.append(fig)
        axes.append(ax)
    dir_path= os.path.join(os.getcwd(),f'figures')
    if not os.path.isdir(dir_path): # if directory already exists:
        os.makedirs(dir_path) # make that dir

    for j, resolution in enumerate(caseNameList):
        csvPath = os.path.join(os.getcwd(),f'{resolution}','forceDistribution.csv')
        data = pd.read_csv(csvPath, skipinitialspace=True)
        plotSectionalForces(data, naming[j])

    figures[0].savefig(f'figures/CFx_per_span.png', dpi=500);
    figures[1].savefig(f'figures/CFz_per_span.png', dpi=500);




if __name__ == '__main__':
    main()

