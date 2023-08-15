To run the demo case follow these steps:

1. Run Submit_Cases.py -> this script will obtain the mesh and submit ramp and adaptive CFL cases for the XV15 rotor.

2. Run Download_Data.py -> this script will download the csv files containing the loads and residual histories.

3. Run Convergence_Plots.py -> this script will cross-plot the residual convergence histories for the ramp and adaptive CFL cases forked from the 1st order solution and a clean 2nd order adpative CFL simulation.

Files.py contains reference to the location of the meshes and JSON files. The default option is to use a mesh from Flexcompute storage servers and the Flow360.json file located in the "localFiles directory".
To run with a mesh stored in the "localFiles" directory, Run Submit_Cases.py --localFiles 1


