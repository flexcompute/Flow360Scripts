Usage:

Use the acoustic.py to calculate and plot the noise spectrums, OASPL, and averaged noise spectrum for observers:

python acoustic.py -i example1_aeroacoustics_v3.csv -o my_simulation

Use the acoustic.py with -n to specify a particular observer to calculate and plot the noise spectrum and OASPL.

python acoustic.py -i example1_aeroacoustics_v3.csv -n <observer_id> -o my_simulation

Use the unsteadyLoads.py to calculate and plot unsteady aerodynamic loads starting from a physical step for example 3000 and get a report on forces:

python unsteadyLoads.py -caseId <xxxxxxx> -start <starting_physical_step> -o my_simulation