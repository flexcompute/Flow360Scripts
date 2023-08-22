import os
import flow360 as fl
from Files import XV15_1st, XV15_2nd

print("Obtaining mesh and solver files")

XV15_1st.get_files()
XV15_2nd.get_files()

print("Files accessed")

caseNameList=[]

# submit mesh

volume_mesh = fl.VolumeMesh.from_file(XV15_1st.mesh_filename, name="XV15_Mesh")
volume_mesh = volume_mesh.submit()

#submit case 1st order

params = fl.Flow360Params(XV15_1st.case_json)
case = fl.Case.create("XV15_1st_order", params, volume_mesh.id)
case = case.submit()

#submit case 2nd order
print(params)
case_fork_1 = case.fork(params=params)
case_fork_1.name = "XV15_2nd_order"
params2 = fl.Flow360Params(XV15_2nd.case_json)
case_fork_1.params = params2
caseNameList.append(case_fork_1.name)
case_fork_1 = case_fork_1.submit()

# dump case name for use in download and post-processing scripts

with open('caseNameList.dat', 'w') as f:
        for line in caseNameList:
            f.write(f"{line}\n")
