"""Case submission through mesh download and upload onto Flexcompute servers"""

import os.path
from urllib.request import urlretrieve

import flow360 as fl

case_name_list = []

# download meshes to the current directory


URL = "https://simcloud-public-1.s3.amazonaws.com/caseStudies/wallModel/Meshes/Windsor_Wall_Resolved_1e-06.b8.ugrid"
MESH_FILENAME = "Windsor_Wall_Resolved_1e-06.b8.ugrid"

if not os.path.isfile(MESH_FILENAME):
    urlretrieve(URL, MESH_FILENAME)

URL2 = "https://simcloud-public-1.s3.amazonaws.com/caseStudies/wallModel/Meshes/Windsor_Wall_Model_5e-04.b8.ugrid"
MESH_FILENAME2 = "Windsor_Wall_Model_5e-04.b8.ugrid"

if not os.path.isfile(MESH_FILENAME2):
    urlretrieve(URL2, MESH_FILENAME2)


# upload the wall resolved mesh
volume_mesh = fl.VolumeMesh.from_file(MESH_FILENAME, name="Windsor_Wall_Resolved_Mesh")
volume_mesh = volume_mesh.submit()


# upload the wall model mesh
volume_mesh2 = fl.VolumeMesh.from_file(MESH_FILENAME2, name="Windsor_Wall_Modeled_Mesh")
volume_mesh2 = volume_mesh2.submit()

# submit wall-resolved case using json file
params = fl.Flow360Params("Flow360.json")
case = fl.Case.create("Windsor_Wall_Resolved", params, volume_mesh.id)
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

case2 = fl.Case.create("Windsor_Wall_Modeled", params, volume_mesh2.id)
case_name_list.append(case2.name)
case2 = case2.submit()

# dump case names for use in download and post-processing scripts

with open("case_name_list.dat", "w", encoding="utf-8") as f:
    for line in case_name_list:
        f.write(f"{line}\n")
