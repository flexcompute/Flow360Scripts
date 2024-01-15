"""Case submission from mesh name stored in mesh_name_list.dat"""

import flow360 as fl

with open("mesh_name_list.dat", "r", encoding="utf=8") as file:
    mesh_name_list = file.read().splitlines()

mesh = None
my_meshes = fl.MyVolumeMeshes(limit=None)
for mesh_name in mesh_name_list:
    for mesh in my_meshes:
        if mesh.name == mesh_name:
            break

    # submit case with poor surface
    params = fl.Flow360Params("Flow360_PoorSurface.json")
    case = fl.Case.create("CRM_Poor_Surface", params, mesh.id)
    case = case.submit()
