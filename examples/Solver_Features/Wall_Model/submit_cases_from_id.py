"""Case submission from mesh ID's present on the Flexcompute servers"""

import flow360 as fl

case_name_list = []

MESH_ID_WALL_RESOLVED = "2f71bda6-b218-4fb2-9a2b-d79a4d3c5384"
MESH_ID_WALL_MODEL = "4ff4782e-9ad1-4bed-ab2d-419a07cc512b"


# submit wall-resolved case using json file
params = fl.Flow360Params("Flow360.json")
case = fl.Case.create("Windsor_Wall_Resolved", params, MESH_ID_WALL_RESOLVED)
case_name_list.append(case.name)
case = case.submit()

# change noSlipWall to wallFunction in params
Boundaries = params.boundaries
params.boundaries = Boundaries.copy(
    update={
        "1": fl.WallFunction(name="Flow.CFDWT.FloorUnder"),
        "4": fl.WallFunction(name="Flow.CFDWT.Floor"),
        "8": fl.WallFunction(name="Windsor"),
        "9": fl.WallFunction(name="Windsor_rear"),
        "10": fl.WallFunction(name="Windsor_supports"),
    }
)

# submit wall-modeled case using updated parameters
case2 = fl.Case.create("Windsor_Wall_Modeled", params, MESH_ID_WALL_MODEL)
case_name_list.append(case2.name)
case2 = case2.submit()

# dump case names for use in download and post-processing scripts
with open("case_name_list.dat", "w", encoding="utf-8") as f:
    for line in case_name_list:
        f.write(f"{line}\n")
