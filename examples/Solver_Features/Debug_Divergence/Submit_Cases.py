import flow360 as fl
from Files import CRM_PoorSurface, CRM_AD

print("Obtaining mesh and solver files")

CRM_PoorSurface.get_files()
CRM_AD.get_files()

print("Files accessed")

caseNameList=[]

# submit mesh with poor surface
volume_mesh = fl.VolumeMesh.from_file(CRM_PoorSurface.mesh_filename, name="CRM_Poor_Surface_Mesh")
volume_mesh = volume_mesh.submit()

#submit case with poor surface
params = fl.Flow360Params(CRM_PoorSurface.case_json)
case = fl.Case.create("CRM_Poor_Surface", params, volume_mesh.id)
caseNameList.append(case.name)
case = case.submit()

# submit mesh with actuator disk
volume_mesh = fl.VolumeMesh.from_file(CRM_AD.mesh_filename, name="CRM_AD_Mesh")
volume_mesh = volume_mesh.submit()

#submit case with actuator disk
params = fl.Flow360Params(CRM_AD.case_json)
case = fl.Case.create("CRM_AD", params, volume_mesh.id)
caseNameList.append(case.name)
case = case.submit()

# dump case names for use in download and post-processing scripts

with open('caseNameList.dat', 'w') as f:
        for line in caseNameList:
            f.write(f"{line}\n")
