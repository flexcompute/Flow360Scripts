"""Case submission from mesh ID's present on the Flexcompute servers"""

import flow360 as fl

mesh_name_list = []

MESH_ID = "49d4b0aa-3a42-4879-8c9c-d977112e7665"

# submit case with poor surface
params = fl.Flow360Params("CRM_PoorSurface.json")
case = fl.Case.create("CRM_Poor_Surface", params, MESH_ID)
case = case.submit()

# write the volume mesh name to a file
volume_mesh = fl.VolumeMesh(MESH_ID)

mesh_name_list.append(volume_mesh.name)

with open("mesh_name_list.dat", "w", encoding="utf-8") as f:
    for line in mesh_name_list:
        f.write(f"{line}\n")
