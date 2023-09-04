import flow360 as fl
from Files import CRM_PoorSurface

print("Obtaining mesh and solver files")

CRM_PoorSurface.get_files()

print("Files accessed")

with open('meshNameList.dat', 'r') as file:
        meshNameList = file.read().splitlines()


my_meshes= fl.MyVolumeMeshes(limit=None)
for i in range(0, len(meshNameList)):
    for mesh in my_meshes:
        if mesh.name == meshNameList[i]:
            break
print(mesh.name)
mesh.download_file("metadata/meshMetrics.json", to_folder="./")
