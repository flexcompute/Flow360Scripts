import os
import flow360 as fl
from flow360 import MyCases


#read in caseNameList

with open('caseNameList.dat', 'r') as file:
        caseNameList = file.read().splitlines()

my_cases = MyCases(limit=None)

for i in range(0, len(caseNameList)):
        caseFolder = os.path.join(os.getcwd(), caseNameList[i])
        os.makedirs(caseFolder, exist_ok = True)
        #Find the latest case with the name corresponding to the name in caseNameList
        for case in my_cases:
            if case.name == caseNameList[i]:
                break
        print(case.name)
        #Download the files 
        case.results.download(nonlinear_residuals=True, surface_forces=True, total_forces=True, destination=caseFolder)
