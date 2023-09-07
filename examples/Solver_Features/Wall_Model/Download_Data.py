import os
import flow360 as fl
from flow360 import MyCases

# read in caseNameList
with open('caseNameList.dat', 'r') as file:
    caseNameList = file.read().splitlines()

# get case list from Flow360
my_cases = MyCases(limit=None)

for caseName in caseNameList:
    caseFolder = os.path.join(os.getcwd(), caseName)
    os.makedirs(caseFolder, exist_ok=True)
    # find the latest case with name corresponding to caseNameList
    for case in my_cases:
        if case.name == caseName:
            break
    print(case.name)
    # download the files
    case.results.download(nonlinear_residuals=True, surface_forces=True, total_forces=True, destination=caseFolder)
