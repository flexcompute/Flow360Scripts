The following example, launches the XV-15 Quick-start case.

To run the demo case follow these steps:

1. Run `python submit_cases_from_downloads.py` -> this script will download the XV15 mesh, and upload it to the Flexcompute servers. The case will also be submitted. Alternatively the script `submit_cases_from_id.py` can also be used to run the case from a mesh already uploaded to Flexcompute servers.

2. Run `python download_data.py` -> this script will download the csv files containing the loads and residual histories.

3. Run `python convergence_plots.py` -> this script will plot the load and residual convergence histories.

4. Run `python download_plot_sectional_forces.py` -> this script will download and plot the sectional loads.

5. Run `download_vis_figures.py` -> this script will download Cp, Cf and streamline visualizations to the vis_figures folder.
