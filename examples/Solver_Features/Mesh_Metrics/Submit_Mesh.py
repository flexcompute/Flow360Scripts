import flow360 as fl
from Files import CRM_PoorSurface

print("Obtaining mesh and solver files")

CRM_PoorSurface.get_files()

print("Files accessed")

meshNameList=[]

# submit mesh with poor surface
volume_mesh = fl.VolumeMesh.from_file(CRM_PoorSurface.mesh_filename, name="CRM_Poor_Surface_Mesh")
volume_mesh = volume_mesh.submit()
meshNameList.append(volume_mesh.name)

with open('meshNameList.dat', 'w') as f:
        for line in meshNameList:
            f.write(f"{line}\n")
