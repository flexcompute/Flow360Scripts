import os
import flow360 as fl
from Files import S809

print("Obtaining mesh and solver files")

S809.get_files()

print("Files accessed")

caseNameList=[]

params = fl.SurfaceMeshingParams(S809.surface_json)
surface_mesh = fl.SurfaceMesh.create(
    S809.geometry, params=params, name="NREL_S809_Surface"
)
surface_mesh = surface_mesh.submit()

params = fl.VolumeMeshingParams(S809.volume_json)
volume_mesh = surface_mesh.create_volume_mesh("NREL_S809_Volume", params=params)
volume_mesh = volume_mesh.submit()

params = fl.Flow360Params(S809.case_json)

#submit case
case = fl.Case.create("NREL_S809_Automated_Meshing", params, volume_mesh.id)
caseNameList.append(case.name)
case = case.submit()
# submit mesh

volume_mesh2 = fl.VolumeMesh.from_file(S809.mesh_filename, name="S809_Structured_Mesh")
volume_mesh2 = volume_mesh2.submit()



#submit case
case = fl.Case.create("NREL_S809_Structured", params, volume_mesh2.id)
caseNameList.append(case.name)
case = case.submit()

# dump case name for use in download and post-processing scripts

with open('caseNameList.dat', 'w') as f:
        for line in caseNameList:
            f.write(f"{line}\n")
