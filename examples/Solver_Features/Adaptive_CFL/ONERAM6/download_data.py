"""Download the results for the ramp and adaptive CFL cases at both angles of attack"""

import os

from flow360 import MyCases

# read in case_name_list
with open("case_name_list.dat", "r", encoding="utf-8") as file:
    case_name_list = file.read().splitlines()

my_cases = MyCases(limit=None)

case = None

for case_name in case_name_list:
    case_folder = os.path.join(os.getcwd(), case_name)
    os.makedirs(case_folder, exist_ok=True)
    # find the latest case with the name corresponding to the name in case_name_list
    for case in my_cases:
        if case.name == case_name:
            break
    print(case.name)
    # download the files
    case.results.download(
        nonlinear_residuals=True,
        surface_forces=True,
        total_forces=True,
        destination=case_folder,
    )
