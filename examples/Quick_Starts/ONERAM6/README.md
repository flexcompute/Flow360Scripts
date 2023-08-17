To run the demo case follow these steps:

1. Run Submit_Cases.py -> this script will obtain the mesh, and upload it to the Flexcompute servers. The case will also be submitted.

2. Run Download_Data.py -> this script will download the csv files containing the loads and residual histories.

3. Run Convergence_Plots.py -> this script will plot the load and residual convergence histories.

4. Run Download_Plot_Sectional_Forces.py -> this script will download and plot the sectional loads.

5. Download_Vis_Figures.py -> this script will download Cp, Cf and streamline visualizations.

Files.py contains reference to the location of the meshes and JSON files. The default option is to use a mesh from Flexcompute storage servers and the Flow360.json file located in the "localFiles directory".
To run with a mesh stored in the "localFiles" directory, Run Submit_Cases.py --localFiles 1


