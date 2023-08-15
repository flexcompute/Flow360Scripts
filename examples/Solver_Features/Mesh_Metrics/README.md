To run the demo case follow these steps:

1. Run Submit_Mesh.py -> this script will upload the mesh to the Flexcompute servers

2. Note that the mesh metrics take a short amount of time to be calculated once the mesh is uploaded. To check whether the mesh metrics have been calculated, try downloading the meshMetrics.json file using Download_MeshMetrics.py

3. Run Submit_Case.py -> this script will upload the case with a poor surface mesh, which will trigger mesh metrics validation warnings.

Files.py contains reference to the location of the meshes and JSON files. The default option is to use a mesh from Flexcompute storage servers and the Flow360.json file located in the "localFiles directory".
To run with a mesh stored in the "localFiles" directory, Run SubmitMesh.py or Submit_Cases.py --localFiles 1

