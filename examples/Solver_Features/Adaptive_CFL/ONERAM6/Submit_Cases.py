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

#submit ramp CFL case at alpha = 3.06
case = fl.Case.create("ONERAM6_3p06_RAMP", params, volume_mesh.id)
caseNameList.append(case.name)
case = case.submit()

#change CFL type to adaptive
params.time_stepping.CFL.type = "adaptive"

#submit adaptive CFL case at alpha = 3.06
case = fl.Case.create("ONERAM6_3p06_ADAPTIVE", params, volume_mesh.id)
caseNameList.append(case.name)
case = case.submit()

#change CFL type to ramp, modify time stepping settings and increase alpha to 10
params.time_stepping.CFL.type = "ramp"
params.time_stepping.max_pseudo_steps = 8000
params.time_stepping.CFL.initial = 1
params.time_stepping.CFL.final = 20
params.time_stepping.CFL.ramp_steps = 200
params.freestream.alpha = 10

#submit ramp CFL case at alpha = 10 
case = fl.Case.create("ONERAM6_10_RAMP", params, volume_mesh.id)
caseNameList.append(case.name)
case = case.submit()


#change CFL type to adaptive
params.time_stepping.CFL.type = "adaptive"

#submit adaptive CFL case at alpha = 10
case = fl.Case.create("ONERAM6_10_ADAPTIVE", params, volume_mesh.id)
caseNameList.append(case.name)
case = case.submit()

# dump case names for use in download and post-processing scripts

with open('caseNameList.dat', 'w') as f:
        for line in caseNameList:
            f.write(f"{line}\n")
