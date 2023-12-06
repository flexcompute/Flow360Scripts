"""Case submission from mesh ID's present on the Flexcompute servers"""

import flow360 as fl

case_name_list = []

MESH_ID = "a823b33f-7523-4aa4-9881-99964917cc47"

# submit case

params = fl.Flow360Params("Flow360.json")
case = fl.Case.create("XV15_Quick_Start", params, MESH_ID)
case = case.submit()

case_name_list.append(case.name)

# dump case name for use in download and post-processing scripts

with open("case_name_list.dat", "w", encoding="utf-8") as f:
    for line in case_name_list:
        f.write(f"{line}\n")
