To run the demo case follow these steps:

1. Run Submit_Cases.py -> this script will obtain the mesh and submit ramp and adaptive CFL cases for the ONERAM6 wing at  two angles of attack

2. Run Download_Data.py -> this script will download the csv files containing the loads and residual histories.

3. Run Convergence_Plots_3p06.py and Convergence_Plots_10.py -> these script will cross-plot the load and residual convergence histories for the ramp and adaptive CFL cases at two angles of attack.

Files.py contains reference to the location of the meshes and JSON files. The default option is to use a mesh from Flexcompute storage servers and the Flow360.json file located in the "localFiles directory".
To run with a mesh stored in the "localFiles" directory, Run Submit_Cases.py --localFiles 1


