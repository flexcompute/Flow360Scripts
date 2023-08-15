import flow360 as fl
from Files import CRM_PoorSurface

print("Obtaining mesh and solver files")

CRM_PoorSurface.get_files()

print("Files accessed")

with open('meshNameList.dat', 'r') as file:
        meshNameList = file.read().splitlines()


my_meshes= fl.MyVolumeMeshes()
for i in range(0, len(meshNameList)):
    for mesh in my_meshes:
        if mesh.name == meshNameList[i]:
            break


#submit case with poor surface
    params = fl.Flow360Params(CRM_PoorSurface.case_json)
    case = fl.Case.create("CRM_Poor_Surface", params, mesh.id)
    case = case.submit()
