The following example demonstrates the use of automated meshing using the ONERA M6 wing.

To run the demo case follow these steps:

1. Run 'python3 submit_cases.py` -> this script will upload the geometry file to the Flexcompute servers, generate the surface and volume mesh and then submit the CFD case.

2. Run `python download_data.py` -> this script will download the csv files containing the loads and residual histories.

3. Run `python convergence_plots.py` -> this script will plot the load and residual convergence histories.

4. Run `python download_plot_sectional_forces.py` -> this script will download and plot the sectional loads.

5. Run `download_vis_figures.py` -> this script will download Cp, Cf and streamline visualizations to the folder vis_figures.
