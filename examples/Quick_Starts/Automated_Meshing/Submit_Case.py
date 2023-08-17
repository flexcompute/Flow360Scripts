import os
import flow360 as fl
from Files import ONERAM6

print("Obtaining mesh and solver files")

ONERAM6.get_files()

print("Files accessed")

caseNameList=[]

params = fl.SurfaceMeshingParams(ONERAM6.surface_json)
surface_mesh = fl.SurfaceMesh.create(
    ONERAM6.geometry, params=params, name="ONERAM6_Automated_Meshing_Surface"
)
surface_mesh = surface_mesh.submit()


params = fl.VolumeMeshingParams(ONERAM6.volume_json)
volume_mesh = surface_mesh.create_volume_mesh("ONERAM6_Automated_Meshing_Volume", params=params)
volume_mesh = volume_mesh.submit()

params = fl.Flow360Params(ONERAM6.case_json)

#submit case
case = fl.Case.create("ONERAM6_Automated_Meshing", params, volume_mesh.id)
caseNameList.append(case.name)
case = case.submit()

# dump case name for use in download and post-processing scripts

with open('caseNameList.dat', 'w') as f:
        for line in caseNameList:
            f.write(f"{line}\n")
