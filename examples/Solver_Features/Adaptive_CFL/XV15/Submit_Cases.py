import flow360 as fl
from Files import XV15

print("Obtaining mesh and solver files")

XV15.get_files()

print("Files accessed")

caseNameList=[]

# submit mesh
volume_mesh = fl.VolumeMesh.from_file(XV15.mesh_filename, name="XV15_Mesh")
volume_mesh = volume_mesh.submit()

#submit 1st order case
params = fl.Flow360Params(XV15.case_json)
case = fl.Case.create("XV15_1st_order_ramp", params, volume_mesh.id)
caseNameList.append(case.name)
case = case.submit()

#update solver and time-stepping parameters
params.navier_stokes_solver.order_of_accuracy=2
params.turbulence_model_solver.order_of_accuracy=2

params.time_stepping.max_pseudo_steps = 35
params.time_stepping.time_step_size = 29.08882086657216

params.time_stepping.CFL.final = 1e7
params.time_stepping.CFL.ramp_steps = 33


#submit 2nd order ramp case (forked from first order)
case_fork_1 = case.fork()
case_fork_1.name = "XV15_2nd_order_ramp_forked"
caseNameList.append(case_fork_1.name)
case_fork_1.params = params
print(params)
case_fork_1 = case_fork_1.submit()

#change CFL type to adaptive
params.time_stepping.CFL.type = "adaptive"

#submit 2nd order adaptive case (forked from first order)
case_fork_2 = case.fork()
case_fork_2.name = "XV15_2nd_order_adaptive_forked"
caseNameList.append(case_fork_2.name)
case_fork_2.params = params
print(params)
case_fork_2 = case_fork_2.submit()


#submit adaptive CFL case 
case = fl.Case.create("XV15_2nd_order_adaptive", params, volume_mesh.id)
caseNameList.append(case.name)
case = case.submit()


# dump case names for use in download and post-processing scripts

with open('caseNameList.dat', 'w') as f:
        for line in caseNameList:
            f.write(f"{line}\n")
