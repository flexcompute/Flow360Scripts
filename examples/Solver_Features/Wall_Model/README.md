The following example compares wall-resolved and wall-modeled simulations for the Windsor body.

To run the demo case follow these steps:

1. Run `python submit_cases_from_downloads.py` -> this script will download both wall resolved and wall model meshes, and upload them to the Flexcompute servers. The cases will also be submitted. Alternatively the script `submit_cases_from_id.py` can also be used to run the cases from meshes already uploaded to Flexcompute servers.

2. Run `python download_data.py` -> this script will download the csv files containing the loads and residual histories.

3. Run `python convergence_plots.py` -> this script will cross-plot the load and residual convergence histories for the wall-resolved and wall-modeled cases.




