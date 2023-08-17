import os
import flow360 as fl
from Files import ONERAM6

print("Obtaining mesh and solver files")

ONERAM6.get_files()

print("Files accessed")

caseNameList=[]

# submit mesh
volume_mesh = fl.VolumeMesh.from_file(ONERAM6.mesh_filename, name="ONERAM6_Mesh")
volume_mesh = volume_mesh.submit()


params = fl.Flow360Params(ONERAM6.case_json)

#submit case
case = fl.Case.create("ONERAM6_Quickstart", params, volume_mesh.id)
caseNameList.append(case.name)
case = case.submit()

# dump case name for use in download and post-processing scripts

with open('caseNameList.dat', 'w') as f:
        for line in caseNameList:
            f.write(f"{line}\n")
