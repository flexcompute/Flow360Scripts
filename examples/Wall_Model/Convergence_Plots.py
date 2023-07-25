import matplotlib.pyplot as plt
from collections import defaultdict
import os, csv
import numpy as np


def getDataDictFromCsv(csvFilePath):
    with open(csvFilePath) as csvFile:
        csvReader = csv.DictReader(csvFile)
        data = defaultdict(list)
        for row in csvReader:
            for key, value in row.items():
                if len(key)>0 and (not key.isspace()):
                    data[key.strip()].append(float(value))
    return data

def computeCLCD(data):
     CL0 = np.add(data['Windsor_CL'], data['Windsor_rear_CL'])
     data['CL'] = np.add(data['Windsor_supports_CL'], CL0)
     CD0 = np.add(data['Windsor_CD'], data['Windsor_rear_CD'])
     data['CD'] = np.add(data['Windsor_supports_CD'], CD0)

     

def plotLoads(data, caseName, plotName):
    axes[0].plot(data['pseudo_step'], data['CL'], label=plotName)
    axes[1].plot(data['pseudo_step'], data['CD'], label=plotName)
    axes[0].set_ylabel('CL');
    axes[1].set_ylabel('CD');
    axes[0].set_ylim(-0.2, -0.1);
    axes[1].set_ylim(0.25, 0.45);

    for i in range(0,2):
            axes[i].legend()
            axes[i].set_xlabel('Pseudo step');
            axes[i].grid(which='major', color='gray')

def plotResiduals(res, caseName, plotName):
    x = res['pseudo_step']
    key = ['0_cont', '1_momx', '2_momy', '3_momz', '4_energ', '5_nuHat']
    labels = ['Cont Residual', 'Momx Residual', 'Momy Residual', 'Momz Residual', 'Energy Residual', 'nuHat Residual']
    for i in range(0,6):
        axes[i].semilogy(x, res[key[i]], label=plotName)
        axes[i].set_ylabel(labels[i])

    for i in range(0,6):
        axes[i].legend()
        axes[i].grid(which='major', color='gray')
        axes[i].set_xlabel('Pseudo step');
        axes[i].set_yticks(10.0**np.arange(-14,-3));
        axes[i].set_ylim([1e-13,1e-3])
        axes[i].set_xlim([0,10000])
    return 0




with open('caseNameList.dat', 'r') as file:
        caseNameList = file.read().splitlines()

naming = ["Wall Resolved", "Wall Modeled"]

def main():

    #Plot loads convergence histories
        global figures, axes
        figures = []
        axes = []
        for i in range(0,2):
            fig, ax = plt.subplots(figsize=(8,6))
            figures.append(fig)
            axes.append(ax)
            dir_path= os.path.join(os.getcwd(),f'figures')
        if not os.path.isdir(dir_path): # if directory already exists:
            os.makedirs(dir_path) # make that dir

        j=0
        for resolution in caseNameList:
            csvPath = os.path.join(os.getcwd(),f'{resolution}','surface_forces_v2.csv')
            data = getDataDictFromCsv(csvPath)
            computeCLCD(data)
            plotLoads(data, resolution, naming[j])
            j=j+1

        figures[0].savefig(f'figures/CL.png', dpi=500);
        figures[1].savefig(f'figures/CD.png', dpi=500);

        for i in range(0,2):
            axes[i].cla();
        
        #Plot residual convergence histories
        for i in range(0,6):
          fig, ax = plt.subplots(figsize=(8,6))
          figures.append(fig)
          axes.append(ax)
          j=0
        for resolution in caseNameList:
            csvPath = os.path.join(os.getcwd(),f'{resolution}','nonlinear_residual_v2.csv')
            res = getDataDictFromCsv(csvPath)
            plotResiduals(res, resolution, naming[j])
            j=j+1
        figures[0].savefig(f'figures/Cont.png', dpi=500);
        figures[1].savefig(f'figures/Momx.png', dpi=500);
        figures[2].savefig(f'figures/Momy.png', dpi=500);
        figures[3].savefig(f'figures/Momz.png', dpi=500);
        figures[4].savefig(f'figures/Energy.png', dpi=500);
        figures[5].savefig(f'figures/nuHat.png', dpi=500);



if __name__ == '__main__':
    main()

