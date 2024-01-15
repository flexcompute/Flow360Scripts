"""Case submission through mesh download and upload onto Flexcompute servers"""

import os.path
from urllib.request import urlretrieve

import flow360 as fl

case_name_list = []

# download meshes to the current directory

URL = "PLACEHOLDER"
MESH_FILENAME = "mesh.lb8.ugrid"

if not os.path.isfile(MESH_FILENAME):
    urlretrieve(URL, MESH_FILENAME)


# submit mesh
volume_mesh = fl.VolumeMesh.from_file(MESH_FILENAME, name="ONERAM6_Mesh")
volume_mesh = volume_mesh.submit()

params = fl.Flow360Params("Flow360.json")

# submit ramp CFL case at alpha = 3.06
case = fl.Case.create("ONERAM6_3p06_RAMP", params, volume_mesh.id)
case_name_list.append(case.name)
case = case.submit()

# change CFL type to adaptive
params.time_stepping.CFL.type = "adaptive"

# submit adaptive CFL case at alpha = 3.06
case2 = fl.Case.create("ONERAM6_3p06_ADAPTIVE", params, volume_mesh.id)
case_name_list.append(case2.name)
case2 = case2.submit()

# change CFL type to ramp, modify time stepping settings and increase alpha to 10
params.time_stepping.CFL.type = "ramp"
params.time_stepping.max_pseudo_steps = 8000
params.time_stepping.CFL.initial = 1
params.time_stepping.CFL.final = 20
params.time_stepping.CFL.ramp_steps = 200
params.freestream.alpha = 10

# submit ramp CFL case at alpha = 10
case3 = fl.Case.create("ONERAM6_10_RAMP", params, volume_mesh.id)
case_name_list.append(case3.name)
case3 = case3.submit()


# change CFL type to adaptive
params.time_stepping.CFL.type = "adaptive"

# submit adaptive CFL case at alpha = 10
case4 = fl.Case.create("ONERAM6_10_ADAPTIVE", params, volume_mesh.id)
case_name_list.append(case4.name)
case4 = case4.submit()

# dump case names for use in download and post-processing scripts

with open("case_name_list.dat", "w", encoding="utf-8") as f:
    for line in case_name_list:
        f.write(f"{line}\n")
