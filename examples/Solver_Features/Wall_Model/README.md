To run the demo case follow these steps:

1. Run `python Submit_Cases.py` -> this script will download[^1] both wall resolved and wall model meshes, and upload them to the Flexcompute servers. The cases will also be submitted.

2. Run `python Download_Data.py` -> this script will download the csv files containing the loads and residual histories.

3. Run `python Convergence_Plots.py` -> this script will cross-plot the load and residual convergence histories for the wall-resolved and wall-modeled cases.

[^1] Files.py contains reference to the location of the meshes and JSON files. The default option is to use a mesh from Flexcompute storage servers and the Flow360.json file located in the "localFiles directory".
To run with a mesh stored in the "localFiles" directory, Run Submit_Cases.py --localFiles 1



