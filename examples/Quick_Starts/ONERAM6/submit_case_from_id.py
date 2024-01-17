"""Case submission from mesh ID's present on the Flexcompute servers"""

import flow360 as fl

case_name_list = []

MESH_ID = "33f46ac0-e4e6-468e-be86-2289817b6472"

params = fl.Flow360Params("Flow360.json")

# submit case
case = fl.Case.create("ONERAM6_Quickstart", params, MESH_ID)
case_name_list.append(case.name)
case = case.submit()

# dump case name for use in download and post-processing scripts

with open("case_name_list.dat", "w", encoding="utf-8") as f:
    for line in case_name_list:
        f.write(f"{line}\n")
