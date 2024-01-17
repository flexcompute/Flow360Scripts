"""Case submission from mesh ID's present on the Flexcompute servers"""

import flow360 as fl

case_name_list = []

MESH_ID = "cfd9dbc1-367e-4737-bdb0-ae6b2622dfaf"

# submit case

params = fl.Flow360Params("Flow360.json")
case = fl.Case.create("XV15_Quick_Start", params, MESH_ID)
case = case.submit()

case_name_list.append(case.name)

# dump case name for use in download and post-processing scripts

with open("case_name_list.dat", "w", encoding="utf-8") as f:
    for line in case_name_list:
        f.write(f"{line}\n")
