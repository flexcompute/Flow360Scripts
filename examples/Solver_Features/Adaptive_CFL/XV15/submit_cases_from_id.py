"""Case submission from mesh ID's present on the Flexcompute servers"""

import flow360 as fl

case_name_list = []

MESH_ID = "05f1b090-2e93-4032-b703-ca665c1f9700"

# submit 1st order case
params = fl.Flow360Params("Flow360.json")
case = fl.Case.create("XV15_1st_order_ramp", params, MESH_ID)
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
case2 = fl.Case.create("XV15_2nd_order_adaptive", params, MESH_ID)
case_name_list.append(case2.name)
case2 = case2.submit()

# dump case names for use in download and post-processing scripts

with open("case_name_list.dat", "w", encoding="utf-8") as f:
    for line in case_name_list:
        f.write(f"{line}\n")
