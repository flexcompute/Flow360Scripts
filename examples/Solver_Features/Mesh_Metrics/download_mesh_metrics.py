"""Downloads the mesh metrics to verify that they have been calculated after mesh upload"""

import flow360 as fl

with open("mesh_name_list.dat", "r", encoding="utf-8") as file:
    mesh_name_list = file.read().splitlines()

mesh = None

my_meshes = fl.MyVolumeMeshes(limit=None)
for mesh_name in mesh_name_list:
    for mesh in my_meshes:
        if mesh.name == mesh_name:
            break

mesh.download_file("metadata/meshMetrics.json", to_folder="./")
