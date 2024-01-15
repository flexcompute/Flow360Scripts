"""Case submission from mesh ID's present on the Flexcompute servers"""

import flow360 as fl

case_name_list = []

MESH_ID = "49d4b0aa-3a42-4879-8c9c-d977112e7665"
MESH_ID2 = "2c1fb0cb-36bc-47f9-a166-4a61507ebfc8"

# submit case with poor surface
params = fl.Flow360Params("Flow360_PoorSurface.json")
case = fl.Case.create("CRM_Poor_Surface", params, MESH_ID)
case_name_list.append(case.name)
case = case.submit()

# submit case with actuator disk
params2 = fl.Flow360Params("Flow360_AD.json")
case2 = fl.Case.create("CRM_AD", params2, MESH_ID2)
case_name_list.append(case2.name)
case2 = case2.submit()

# dump case names for use in download and post-processing scripts
with open("case_name_list.dat", "w", encoding="utf-8") as f:
    for line in case_name_list:
        f.write(f"{line}\n")
