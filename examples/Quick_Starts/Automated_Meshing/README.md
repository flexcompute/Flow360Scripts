To run the demo case follow these steps:

1. Run Submit_Cases.py -> this script will obtain the mesh, and upload it to the Flexcompute servers. The case will also be submitted.

2. Run Download_Data.py -> this script will download the csv files containing the loads and residual histories.

3. Run Convergence_Plots.py -> this script will plot the load and residual convergence histories.

Files.py contains reference to the location of the meshes and JSON files. The default option is to use files from Flexcompute storage servers. To run with  files stored in the "localFiles" directory, Run Submit_Cases.py --localFiles 1


