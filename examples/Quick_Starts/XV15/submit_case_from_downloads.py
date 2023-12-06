"""Case submission through mesh download and upload onto Flexcompute servers"""

import os.path
from urllib.request import urlretrieve

import flow360 as fl

case_name_list = []

# download meshes to the current directory

URL = "https://simcloud-public-1.s3.amazonaws.com/xv15/XV15_Hover_ascent_coarse.cgns"
MESH_FILENAME = "XV15_Hover_ascent_coarse.cgns"

if not os.path.isfile(MESH_FILENAME):
    urlretrieve(URL, MESH_FILENAME)

volume_mesh = fl.VolumeMesh.from_file(MESH_FILENAME, name="XV15_Mesh")
volume_mesh = volume_mesh.submit()

# submit case
params = fl.Flow360Params("Flow360.json")
case = fl.Case.create("XV15_Quick_Start", params, volume_mesh.id)
case = case.submit()

case_name_list.append(case.name)

# dump case name for use in download and post-processing scripts

with open("case_name_list.dat", "w", encoding="utf-8") as f:
    for line in case_name_list:
        f.write(f"{line}\n")
