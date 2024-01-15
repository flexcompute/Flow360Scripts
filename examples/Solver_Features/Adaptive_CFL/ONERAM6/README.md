The following example demonstrates the use of adaptive CFL for the ONERAM6 wing

To run the demo case follow these steps:

1. Run `python submit_cases_from_downloads.py` -> this script will download the ONERAM6 mesh, and upload it to the Flexcompute servers. The cases will also be submitted for both adaptive and ramp CFL at two angles of attack. Alternatively the script `submit_cases_from_id.py` can also be used to run the cases from meshes already uploaded to Flexcompute servers.

2. Run `python download_data.py` -> this script will download the csv files containing the loads and residual histories at two angles of attack

3. Run `python convergence_plots_3p06.py` and `python convergence_plots_10.py` -> these scripts will cross-plot the load and residual convergence histories for the ramp and adaptive CFL cases at two angles of attack.
