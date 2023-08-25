usage:

Use the acoustic.py to calculate and plot noise spectrums, oaspl, and averaged noise spectrums for observers:

python acoustic.py -csv example_aeroacoustics_v3.csv -o my_simulation

Use the unsteadyLoads.py to calculate and plot unsteady aerodynamic loads starting from physical step 3000 and get a report on forces:

python unsteadyLoads.py -caseId <xxxxxxx> -start 3000 -o my_simulation