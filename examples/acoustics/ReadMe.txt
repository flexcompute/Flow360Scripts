Usage:

Use the acoustic.py to calculate and plot the noise spectrums, OASPL, and averaged noise spectrum for observers:

python acoustic.py -i example1_aeroacoustics_v3.csv -o my_simulation

Use the acoustic.py with -n to specify a particular observer to calculate and plot the noise spectrum and OASPL.

python acoustic.py -i example1_aeroacoustics_v3.csv -n <observer_id> -o my_simulation

-------------------------------------------------------------------------------------------------------------------

Use the unsteadyLoads.py to calculate and plot unsteady aerodynamic loads starting from a physical step for example 3000 and get a report on forces:

option 1 with caseId:

python unsteadyLoads.py -caseId <xxxxxxx> -start <starting_physical_step> -o my_simulation

option 2 with <caseId>_total_forces_v2.csv file and a json input including reference values:

python unsteadyLoads.py -i <caseId>_total_forces_v2.csv -s 3000 -r reference_flow360.json -o my_simulation

option 3 with <caseId>_total_forces_v2.csv file and without a json input for reference values:

python unsteadyLoads.py -i <caseId>_total_forces_v2.csv -s 3000 -o my_simulation