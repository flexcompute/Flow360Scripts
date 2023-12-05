The following cases are for a demonstration of the debug divergence pipeline and are intended to diverge. 

To run the demo case follow these steps:

1. Run `python submit_cases_from_downloads.py` -> this script will download both wall resolved and wall model meshes, and upload them to the Flexcompute servers. The cases will also be submitted. Alternatively the script `submit_cases_from_id.py` can also be used to run the cases from meshes already uploaded to Flexcompute servers.

2. Run `python download_data.py` -> this script will download the csv files containing the min/max locations of the pressure, density, velocity magnitude and turbulent variables.

3. Run `python print_divergence_locations.py` -> this script will print the minimum pressure, minimum density, maxiumum velocity magnitude and minimum nuHat at the last iteration.

4. Investigate the mesh at the location, where one of the variables went non-physical (e.g. negative pressure or density)

The debug divergence pipeline can also be used on the WebUI:

1. Go to min/max tab and position cursor on last pseudo-step in plot. Read which variable diverged from plot or from table below.

2. Go to case visualization tab.

3. Turn-off all boundaries and slices

4. Switch on non-slip walls.

5. Switch on slices of interest for the diverged variable.

6. Investigated multiple slices and views (flat vs crinkle vs wireframe with contour on/off)

7. Examine the mesh for quality issues such as large jumps in area/volume ratio's
