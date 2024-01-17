"""Case submission using automated meshing and structured pre-generated mesh case submission from mesh download"""

import os.path
from urllib.request import urlretrieve

import flow360 as fl

# inputs for structured mesh download
URL = "https://simcloud-public-1.s3.amazonaws.com/s809/s809structured.cgns"
MESH_FILENAME = "s809structured.cgns"

case_name_list = []

params = fl.SurfaceMeshingParams("s809SurfaceMesh.json")
surface_mesh = fl.SurfaceMesh.create(
    "s809.csm", params=params, name="NREL_S809_Surface"
)
surface_mesh = surface_mesh.submit()

params = fl.VolumeMeshingParams("s809VolumeMesh.json")
volume_mesh = surface_mesh.create_volume_mesh("NREL_S809_Volume", params=params)
volume_mesh = volume_mesh.submit()

params = fl.Flow360Params("s809Case.json")

# submit case
case = fl.Case.create("NREL_S809_Automated_Meshing", params, volume_mesh.id)
case_name_list.append(case.name)
case = case.submit()

if not os.path.isfile(MESH_FILENAME):
    urlretrieve(URL, MESH_FILENAME)

# submit mesh
volume_mesh2 = fl.VolumeMesh.from_file(MESH_FILENAME, name="S809_Structured_Mesh")
volume_mesh2 = volume_mesh2.submit()

# submit case
case2 = fl.Case.create("NREL_S809_Structured", params, volume_mesh2.id)
case_name_list.append(case2.name)
case2 = case2.submit()

# dump case name for use in download and post-processing scripts

with open("case_name_list.dat", "w", encoding="utf-8") as f:
    for line in case_name_list:
        f.write(f"{line}\n")
