import matplotlib.pyplot as plt
from collections import defaultdict
import os, csv
import numpy as np
import pandas as pd


     

with open('caseNameList.dat', 'r') as file:
        caseNameList = file.read().splitlines()

for resolution in caseNameList:
    csvPath = os.path.join(os.getcwd(),f'{resolution}','minmax_state_v2.csv')
    data = pd.read_csv(csvPath, skipinitialspace=True)
    print(resolution)
    print("Minimum Density: " + str(data[f"min_rho"][len(data)-1])+" at location (x="+ str(data[f"min_rho_x"][len(data)-1])+ ", y=" + str(data[f"min_rho_y"][len(data)-1])+", z="+ str(data[f"min_rho_z"][len(data)-1]) +")" )
    print("Minimum Pressure: " + str(data[f"min_p"][len(data)-1])+" at location (x="+ str(data[f"min_p_x"][len(data)-1])+ ", y=" + str(data[f"min_p_y"][len(data)-1])+", z="+ str(data[f"min_p_z"][len(data)-1]) +")" )
    print("Maximum Velocity Magnitude: " + str(data[f"max_umag"][len(data)-1])+" at location (x="+ str(data[f"max_umag_x"][len(data)-1])+ ", y=" + str(data[f"max_umag_y"][len(data)-1])+", z="+ str(data[f"max_umag_z"][len(data)-1]) +")" )
    print("Minimum nuHat Magnitude: " + str(data[f"min_nuHat"][len(data)-1])+" at location (x="+ str(data[f"min_nuHat_x"][len(data)-1])+ ", y=" + str(data[f"min_nuHat_y"][len(data)-1])+", z="+ str(data[f"min_nuHat_z"][len(data)-1]) +")" )




                


