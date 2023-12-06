"""Case submission through mesh download and upload onto Flexcompute servers"""

import os.path
from urllib.request import urlretrieve

import flow360 as fl

case_name_list = []

# download mesh to the current directory
URL = "https://simcloud-public-1.s3.amazonaws.com/om6/wing_tetra.1.lb8.ugrid"
MESH_FILENAME = "wing_tetra.1.lb8.ugrid"

if not os.path.isfile(MESH_FILENAME):
    urlretrieve(URL, MESH_FILENAME)


# submit mesh
volume_mesh = fl.VolumeMesh.from_file(MESH_FILENAME, name="ONERAM6_Mesh")
volume_mesh = volume_mesh.submit()

params = fl.Flow360Params("Flow360.json")

# submit case
case = fl.Case.create("ONERAM6_Quickstart", params, volume_mesh.id)
case_name_list.append(case.name)
case = case.submit()

# dump case name for use in download and post-processing scripts

with open("case_name_list.dat", "w", encoding="utf-8") as f:
    for line in case_name_list:
        f.write(f"{line}\n")
