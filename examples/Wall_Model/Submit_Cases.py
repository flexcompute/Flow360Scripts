import flow360 as fl
from Files import WallResolved, WallModel

print("Downloading mesh and solver files")

WallResolved.get_files()
WallModel.get_files()

print("Files downloaded")

caseNameList=[]

# submit wall resolved mesh
volume_mesh = fl.VolumeMesh.from_file(WallResolved.mesh_filename, name="Windsor_Wall_Resolved_Mesh")
volume_mesh = volume_mesh.submit()


# submit wall model mesh
volume_mesh2 = fl.VolumeMesh.from_file(WallModel.mesh_filename, name="Windsor_Wall_Modeled_Mesh")
volume_mesh2 = volume_mesh2.submit()

 # submit wall-resolved case using json file
params = fl.Flow360Params(WallResolved.case_json)
case = fl.Case.create("Windsor_Wall_Resolved", params, volume_mesh.id)
caseNameList.append(case.name)
case = case.submit()

# Change noSlipWall to wallFunction in params

Boundaries = params.boundaries
params.boundaries = Boundaries.copy(update={ "1": fl.WallFunction(name="Flow.CFDWT.FloorUnder"),  "4": fl.WallFunction(name="Flow.CFDWT.Floor"),  "8": fl.WallFunction(name="Windsor"), "9": fl.WallFunction(name="Windsor_rear"), "10": fl.WallFunction(name="Windsor_supports")})

# submit wall-modeled case using updated parameters

case = fl.Case.create("Windsor_Wall_Modeled", params, volume_mesh2.id)
caseNameList.append(case.name)
case = case.submit()

# dump case names for use in download and post-processing scripts

with open('caseNameList.dat', 'w') as f:
        for line in caseNameList:
            f.write(f"{line}\n")

