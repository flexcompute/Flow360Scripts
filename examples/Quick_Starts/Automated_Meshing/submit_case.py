"""Submit surface mesh from geometry file, volume mesh from surface mesh and case from volume mesh"""

import flow360 as fl

case_name_list = []

# submit surface mesh
params = fl.SurfaceMeshingParams("om6SurfaceMesh.json")
surface_mesh = fl.SurfaceMesh.create(
    "om6wing.csm", params=params, name="ONERAM6_Automated_Meshing_Surface"
)
surface_mesh = surface_mesh.submit()

# submit volume mesh
params = fl.VolumeMeshingParams("om6VolumeMesh.json")
volume_mesh = surface_mesh.create_volume_mesh(
    "ONERAM6_Automated_Meshing_Volume", params=params
)
volume_mesh = volume_mesh.submit()


params = fl.Flow360Params("om6Case.json")

# submit case
case = fl.Case.create("ONERAM6_Automated_Meshing", params, volume_mesh.id)
case_name_list.append(case.name)
case = case.submit()

# dump case name for use in download and post-processing scripts

with open("case_name_list.dat", "w", encoding="utf-8") as f:
    for line in case_name_list:
        f.write(f"{line}\n")
