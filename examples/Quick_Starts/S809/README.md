The following example demonstrates the automated meshing workflow for the S809 airfoil and compares the results with the pre-meshed structured grid. 

To run the demo case follow these steps:

1. Run `python submit_cases_from_downloads.py` -> this script will download the structured S809 mesh, and upload it to the Flexcompute servers. The cases will also be submitted for both automated mesh and structured mesh. Alternatively the script `submit_cases_from_id.py` can also be used to run the structured mesh case from a meshe already uploaded to Flexcompute servers.

2. Run `python download_data.py` -> this script will download the csv files containing the loads and residual histories.

3. Run `python convergence_plots.py` to cross-plot the loads and residual convergence histories for the automated mesh and structured mesh cases.
