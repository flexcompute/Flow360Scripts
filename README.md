To run the demo case follow these steps:

1. Run Submit_Cases.py -> this script will download both wall resolved and wall model meshes, and upload them to the Flexcompute servers. The cases will also be submitted.

2. Run Download_Data.py -> this script will download the csv files containing the loads and residual histories.

3. Run Convergence_Plots.py -> this script will cross-plot the load and residual convergence histories for the wall-resolved and wall-modeled cases.

Files.py contains reference to the location of the meshes and JSON files. 

- The Flow360.json file is contained in the "Files" directory.
- The meshes are obtained by default from files stored on Flexcompute storage servers, or by setting an optional flag --localFiles to 1, locally stored files can be used from the "Files" directory.


