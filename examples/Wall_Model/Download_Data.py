import os
import flow360 as fl
from flow360.component.case import CaseDownloadable
from flow360 import MyCases

files = ["nonlinear_residual_v2.csv", "surface_forces_v2.csv", "total_forces_v2.csv"]

downloadable =["NONLINEAR_RESIDUALS", "SURFACE_FORCES", "TOTAL_FORCES"]

#read in caseNameList

with open('caseNameList.dat', 'r') as file:
        caseNameList = file.read().splitlines()

my_cases = MyCases()

for i in range(0, len(caseNameList)):
        caseFolder = os.path.join(os.getcwd(), caseNameList[i])
        os.makedirs(caseFolder, exist_ok = True)
        #Find the latest case with the name corresponding to the name in caseNameList
        for case in my_cases:
            if case.name == caseNameList[i]:
                break
        #Download the files 
        for j in range(0, len(files)):
            dst = os.path.join(caseFolder, files[j])
            case.results.download_file(getattr(CaseDownloadable,downloadable[j]), to_file=dst)
        #case.results.download_surface()
        #case.results.download_volumetric()
