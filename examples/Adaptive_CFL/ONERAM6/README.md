To run the demo case follow these steps:

1. Run Submit_Cases.py -> this script will download the ONERAM6 mesh, and upload it to the Flexcompute servers. The ramp CFL and adaptive CFL cases will also be submitted for both angles of attack of 3.06 and 10 degrees.

2. Run Download_Data.py -> this script will download the csv files containing the loads and residual histories.

3. Run Convergence_Plots_3p06.py -> this script will cross-plot the load and residual convergence histories for the ramp and adaptive CFL cases at 3.06 degrees angle of attack.

4. Run Convergence_Plots_10.py -> this script will cross-plot the load and residual convergence histories for the ramp and adaptive CFL cases at 10 degrees angle of attack.


Files.py contains reference to the location of the meshes and JSON files


