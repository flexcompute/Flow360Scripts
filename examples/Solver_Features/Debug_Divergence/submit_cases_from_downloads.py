"""Case submission through mesh download and upload onto Flexcompute servers"""

import os.path
from urllib.request import urlretrieve

import flow360 as fl

case_name_list = []

# download meshes to the current directory

URL = "PLACEHOLDER"
MESH_FILENAME = "Unswept_CRM_Poor_Surface.cgns"

if not os.path.isfile(MESH_FILENAME):
    urlretrieve(URL, MESH_FILENAME)

URL2 = "PLACEHOLDER"
MESH_FILENAME2 = "Unswept_CRM_AD.cgns"

if not os.path.isfile(MESH_FILENAME2):
    urlretrieve(URL2, MESH_FILENAME2)

# submit mesh with poor surface
volume_mesh = fl.VolumeMesh.from_file(MESH_FILENAME, name="CRM_Poor_Surface_Mesh")
volume_mesh = volume_mesh.submit()

# submit mesh with actuator disk
volume_mesh2 = fl.VolumeMesh.from_file(MESH_FILENAME2, name="CRM_AD_Mesh")
volume_mesh2 = volume_mesh2.submit()

# submit case with poor surface
params = fl.Flow360Params("Flow360_PoorSurface.json")
case = fl.Case.create("CRM_Poor_Surface", params, volume_mesh.id)
case_name_list.append(case.name)
case = case.submit()

# submit case with actuator disk
params2 = fl.Flow360Params("Flow360_AD.json")
case2 = fl.Case.create("CRM_AD", params2, volume_mesh2.id)
case_name_list.append(case2.name)
case2 = case2.submit()

# dump case names for use in download and post-processing scripts

with open("case_name_list.dat", "w", encoding="utf-8") as f:
    for line in case_name_list:
        f.write(f"{line}\n")
