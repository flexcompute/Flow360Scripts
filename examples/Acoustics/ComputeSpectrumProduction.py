# This script is used for post-processing of aeroacoustic pressure data
# based on the PSU-WOPWOP 3.4.3 User Guide
# 

# The only required argument is the input file
# input -> name of the input file containing the pressure data at each observedID. Typically this will be of the form caseID_total_acoustics_v3.csv
#
# Additional optional arguments can be specified:
# window -> 0 indicates no windowing applied, 1 (default) indicates Hann window.
# a_weight -> 0 indicates no weighting applied, 1 (default) inidicates A-weighted resutls
# observer_Id (specified observer) -> only processes a single observer specified by the user
# output -> output file for OASPL values. The default is OASPL.csv

# Outputs:
# A csv file containing the OASPL for each observerID
# PNG files with the spectral plots for each observerID

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os
import argparse


#Input corresponding environmental conditions
grid_unit = 1 # m
speed_of_sound = 340 # m/s, freestream
rho = 1.225 # kg/m^3, freestream
reference_sound_pressure = 20e-6 # Pa

#Constants used for A-weighting
K1 = 2.243e16
K3 = 1.562
f1 = 20.599
f2 = 107.653
f3 = 737.862
f4 = 12194.220

def readCsvFile(filePath):
    df = pd.read_csv(filePath, skipinitialspace=True)
    del df[df.columns[-1]]
    data = df.to_dict(orient='list')
    return data

def apply_windowing_function(acoustics_data, i_observer, window):
    pressure = np.asarray(acoustics_data[f'observer_{i_observer}_pressure'])
    indices  = np.nonzero(pressure)
    non_zero_pressure = pressure[indices]
    N = len(non_zero_pressure) # number of time points in the time history

    # window correction. 0= Rectangular window, 1= Hann Window
    if(window==1):
        window_function = np.hanning(N)
        Fc = np.sqrt(N/sum(window_function**2))
    else:
        window_function = 1.0
        Fc = 1.0
    # The windows that are actually applied to the time history are 
    # the window functions multiplied by their respective scaling factor
    windowed_pressure = window_function * Fc * non_zero_pressure
    return windowed_pressure

def compute_spectrum(windowed_pressure, time_step_size, i_observer, a_weight, output):
    N = len(windowed_pressure)
    physical_pressure     = windowed_pressure * rho * speed_of_sound**2 # Pa
    physical_time_step_size = time_step_size * grid_unit / speed_of_sound # s
    frequency_step_size = 1.0/(N*physical_time_step_size)
    M = int(np.floor(N/2)+1)
    nyquist_frequency = np.floor(N/2)*frequency_step_size
    frequency = np.linspace(0,nyquist_frequency,M)
    spectrum  = np.fft.rfft(physical_pressure)
    
    Pc = np.zeros(M, dtype=complex)
    Pc[0]   = spectrum[0] * 1/N;
    Pc[1:M] = spectrum[1:M] * 2/N;
    mean_square_pressure = 0.5 * np.abs(Pc)**2
    
    if a_weight==1: 
        weighted_mean_square_pressure = np.zeros(M)
        for m in range(0,M):
            f_m  = frequency[m]
            wCm = K1 * f_m**4 / ((f_m**2+f1**2)**2 * (f_m**2+f4**2)**2)
            wAm = wCm * K3 * f_m**4 / ((f_m**2+f2**2) * (f_m**2+f3**2))
            weighted_mean_square_pressure[m] = 0.5 * wAm * np.abs(Pc[m])**2
        SPL   = 10 * np.log10(weighted_mean_square_pressure/reference_sound_pressure**2)
        OASPL = 10 * np.log10(sum(weighted_mean_square_pressure)/reference_sound_pressure**2)
        if np.isnan(OASPL)==0:
            print(f'OASPLdBA = {OASPL}')
        else:
            print("WARNING: Invalid result obtained, skipping observer "+ str(i_observer))

    else:
    
        mean_Square_pressure = 0.5 * np.abs(Pc)**2
        SPL   = 10 * np.log10(mean_square_pressure/reference_sound_pressure**2)
        OASPL = 10 * np.log10(sum(mean_square_pressure)/reference_sound_pressure**2)
        if np.isnan(OASPL)==0:
            print(f'OASPLdB = {OASPL}')
        else:
            print("WARNING: Invalid result obtained, skipping obeserver " +str(i_observer))
    return frequency, SPL, OASPL

def plot_spectrum(frequency, SPL , i_observer, a_weight, window):
    # plotting
    plt.figure(figsize=(8, 6))
    if (a_weight ==0 and window == 1):
        plot_title = "Noise Spectrum - Non-weighted, Hann Window - Observer "+str(i_observer)
    elif (a_weight ==1 and window == 1):
        plot_title = "Noise Spectrum - A-weighted, Hann Window - Observer "+str(i_observer)
    elif (a_weight ==1 and window == 0):
        plot_title = "Noise Spectrum - A-weighted, No Window - Observer "+str(i_observer)
    elif (a_weight ==1 and window == 1):
        plot_title = "Noise Spectrum - A-weighted, No Window - Observer "+str(i_observer)
  
    plt.title(plot_title)

    if a_weight==1:
        plt.plot(frequency, SPL, '-', label='dBA')
        plt.ylabel('SPL [dBA]', fontsize=10)

    else:
        plt.plot(frequency, SPL, '-', label='dB')
        plt.ylabel('SPL [dB]', fontsize=10)

    plt.xscale('log')
    plt.xlabel('Frequency [Hz]', fontsize=10)
    plt.grid(which='major')
    plt.grid(which='minor', ls='--',color='k',linewidth=0.5)
    plt.legend()
    plt.savefig(f'figures/spectrum_observer_{i_observer}',dpi=500)
    plt.close()
    return 0








def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('-i','--input',help='Specify the input aeroacoustic CSV file. For example: <caseId>_total_acoustics_v3.csv',type=str,required=True)
    parser.add_argument('-n','--observer_Id',help='Observer Id number for acoustic pos-processing.',type=int,required=False)
    parser.add_argument('-o','--output',help='Specify the output file name for calculated OASPL. Default is OASPL.csv',type=str,required=False)
    parser.add_argument('-w','--window',help='Specify whether windowing should be applied to the spectral output 0=NONE, 1=HANN WINDOW',type=int,required=False)    
    parser.add_argument('-a','--a_weight',help='Specify whether A-weighting should be applied to the signal. 0=No weighting applied, 1=A-weighted signal.',type=int,required=False)
    args = parser.parse_args()


    os.makedirs('figures',exist_ok=True)

    acoustics_data = readCsvFile(args.input)
    

    if args.observer_Id is None:
        print("Computing aeroacoustic output for all observers")
        n_observer = len(acoustics_data)-2
        observer_Id = list(range(0,n_observer))

    else:
        print("Computing aeroacoustic output for observer ID "+ str(args.observer_Id))
        n_observer = 1
        observer_Id =list(range(args.observer_Id, args.observer_Id+1))
    
    #Hann window by default
    if args.window is None:
        args.window=1

    if  args.window == 1:
        print("Hann Window")
    elif args.window==0:
        print("Rectangular Window")
    
    if args.output is None:
        oaspl_file = os.path.join("OASPL.csv")
    else:
        oaspl_file = os.path.join(args.output)

    #A-weighted results by default

    if args.a_weight is None:
        args.a_weight=1

    if args.a_weight == 1:
        print("A-weighted output")
        print(f"observer_Id, dBA",file=open(oaspl_file, 'w'))

    elif args.a_weight==0:
        print("Non-weighted output")
        print(f"observer_Id, dB",file=open(oaspl_file, 'w'))


    for i_observer in observer_Id:
        print(f'Observer ID = {i_observer}')
        #Assuming constant time step size for now
        time_step_size = acoustics_data[f"time"][1]-acoustics_data[f"time"][0]
        #Apply windowing function (even if no windowing is specified, script still goes through this function with a rectangular window applied).
        windowed_pressure = apply_windowing_function(acoustics_data, i_observer, args.window)
        #Compute spectrum and OASPL values
        frequency, SPL, OASPL = compute_spectrum(windowed_pressure, time_step_size, i_observer, args.a_weight, args.output)
        #Output CSV file containing OASPL values
        if np.isnan(OASPL)==0:
            print("{}, {:.5f}".format(i_observer,OASPL),file=open(oaspl_file, 'a'))
        #Plot spectral response
        if (np.isnan(SPL).any())==0:
            plot_spectrum(frequency, SPL, i_observer, args.a_weight, args.window)
    return 0

if __name__ == '__main__':
    main()

