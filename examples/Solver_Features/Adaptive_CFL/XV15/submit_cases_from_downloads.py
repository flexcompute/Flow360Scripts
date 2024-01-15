"""Case submission through mesh download and upload onto Flexcompute servers"""

import os.path
from urllib.request import urlretrieve

import flow360 as fl

case_name_list = []

# download meshes to the current directory

URL = "PLACEHOLDER"
MESH_FILENAME = "xv15_airplane_pitch26.cgns"

if not os.path.isfile(MESH_FILENAME):
    urlretrieve(URL, MESH_FILENAME)


# submit mesh
volume_mesh = fl.VolumeMesh.from_file(MESH_FILENAME, name="XV15_Mesh")
volume_mesh = volume_mesh.submit()

params = fl.Flow360Params("Flow360.json")

# submit 1st order case
case = fl.Case.create("XV15_1st_order_ramp", params, volume_mesh.id)
case_name_list.append(case.name)
case = case.submit()

# update solver and time-stepping parameters
params.navier_stokes_solver.order_of_accuracy = 2
params.turbulence_model_solver.order_of_accuracy = 2

params.time_stepping.max_pseudo_steps = 35
params.time_stepping.time_step_size = 29.08882086657216

params.time_stepping.CFL.final = 1e7
params.time_stepping.CFL.ramp_steps = 33


# submit 2nd order ramp case (forked from first order)
case_fork_1 = case.fork()
case_fork_1.name = "XV15_2nd_order_ramp"
case_name_list.append(case_fork_1.name)
case_fork_1.params = params
case_fork_1 = case_fork_1.submit()

# change CFL type to adaptive
params.time_stepping.CFL.type = "adaptive"


# submit adaptive CFL case
case2 = fl.Case.create("XV15_2nd_order_adaptive", params, volume_mesh.id)
case_name_list.append(case2.name)
case2 = case2.submit()


# dump case names for use in download and post-processing scripts

with open("case_name_list.dat", "w", encoding="utf-8") as f:
    for line in case_name_list:
        f.write(f"{line}\n")
