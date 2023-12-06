"""Case submission using automated meshing and structured pre-generated mesh case submission from mesh ID"""

import flow360 as fl

# mesh ID for structured mesh
MESH_ID = "0ab89ce3-33e0-4d4e-bd4a-7249da3cd9c3"

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


# submit case
case2 = fl.Case.create("NREL_S809_Structured", params, MESH_ID)
case_name_list.append(case2.name)
case2 = case2.submit()

# dump case name for use in download and post-processing scripts

with open("case_name_list.dat", "w", encoding="utf-8") as f:
    for line in case_name_list:
        f.write(f"{line}\n")
