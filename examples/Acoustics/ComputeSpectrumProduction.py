# This script is used for post-processing of aeroacoustic pressure data
# based on the PSU-WOPWOP 3.4.3 User Guide
# 


# Inputs:
# The required input is set at the top of the main function in this script. Optional arguments can be modified directly in the acoustics_output function call.
# The only required input is the input file containing the pressure data at the observer location, typically of the form {caseID}_total_acoustics_v3.csv.
# 
# Valid arguments to the optional inputs include:
# weighting: "A" "None"
# window: "Hann" "None"
# output: any string for the output file name
# observer_id: -1 corresponds to post-processing all observer ID's or an integer corresponding to a single observer ID present in the input file.

# Outputs:
# A csv file containing the OASPL for each observerID 
# A plot of observerID vs OASPL
# PNG files with the spectral plots for each observerID

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os

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

def read_csv_file(filePath):
    df = pd.read_csv(filePath, skipinitialspace=True)
    df = df.iloc[:,:-1]
    data = df.to_dict(orient='list')
    return data

def apply_windowing_function(acoustics_data, i_observer, window):
    pressure = np.asarray(acoustics_data[f'observer_{i_observer}_pressure'])
    indices  = np.nonzero(pressure)
    non_zero_pressure = pressure[indices]
    N = len(non_zero_pressure) # number of time points in the time history

    # window correction. 0= Rectangular window, 1= Hann Window
    if(window=="Hann"):
        window_function = np.hanning(N)
        fc = np.sqrt(N/sum(window_function**2))
    else:
        window_function = 1.0
        fc = 1.0
    # The windows that are actually applied to the time history are 
    # the window functions multiplied by their respective scaling factor
    windowed_pressure = window_function * fc * non_zero_pressure
    return windowed_pressure

def compute_spectrum(windowed_pressure, time_step_size, i_observer, weighting, output):
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
    
    if weighting=="A": 
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
            print('OASPLdBA = 0.0')

    else:
    
        mean_square_pressure = 0.5 * np.abs(Pc)**2
        SPL   = 10 * np.log10(mean_square_pressure/reference_sound_pressure**2)
        OASPL = 10 * np.log10(sum(mean_square_pressure)/reference_sound_pressure**2)
        if np.isnan(OASPL)==0:
            print(f'OASPLdB = {OASPL}')
        else:
            print("WARNING: Invalid result obtained, skipping obeserver " +str(i_observer))
    return frequency, SPL, OASPL

def plot_spectrum(frequency, SPL , i_observer, weighting, window):
    plt.figure(figsize=(8, 6))
    if (weighting == "None" and window == "Hann"):
        plot_title = "Noise Spectrum - Non-weighted, Hann Window - Observer "+str(i_observer)
    elif (weighting =="None" and window == "None"):
        plot_title = "Noise Spectrum - Non-weighted, No Window - Observer "+str(i_observer)
    elif (weighting == "A" and window == "None"):
        plot_title = "Noise Spectrum - A-weighted, No Window - Observer "+str(i_observer)
    elif (weighting == "A" and window == "Hann"):
        plot_title = "Noise Spectrum - A-weighted, Hann Window - Observer "+str(i_observer)
  
    plt.title(plot_title)

    if weighting=="A":
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

def plot_OASPL(observer_id_all, OASPL_all, weighting, window):
    plt.figure(figsize=(8, 6))
    if (weighting == "None" and window == "Hann"):
        plot_title = "OASPL - Non-weighted, Hann Window"
    elif (weighting =="None" and window == "None"):
        plot_title = "OASPL - Non-weighted, No Window"
    elif (weighting == "A" and window == "None"):
        plot_title = "OASPL - A-weighted, No Window"
    elif (weighting == "A" and window == "Hann"):
        plot_title = "OASPL, A-weighted, Hann Window"

    plt.title(plot_title)

    if weighting=="A":
        plt.scatter(observer_id_all, OASPL_all, label='dBA')
        plt.ylabel('OASPL [dBA]', fontsize=10)

    else:
        plt.scatter(observer_id_all, OASPL_all, label='dB')
        plt.ylabel('OASPL [dB]', fontsize=10)

    plt.xlabel('Observer ID', fontsize=10)
    plt.grid(which='major')
    plt.grid(which='minor', ls='--',color='k',linewidth=0.5)
    plt.legend()
    plt.savefig(f'figures/OASPL.png',dpi=500)
    plt.close()

def acoustics_output(input, output, window, weighting, observer_id):
    OASPL_all = []
    observer_id_all = []
    os.makedirs('figures',exist_ok=True)

    acoustics_data = read_csv_file(input)

    if (observer_id== -1):
        print("Computing aeroacoustic output for all observers")
        n_observer = len(acoustics_data)-2
        observer_id = list(range(0,n_observer))

    else:
        print("Computing aeroacoustic output for observer ID "+ str(observer_id))
        n_observer = 1
        if (observer_id >= len(acoustics_data)-2):
            print("Observer ID not present in the aeroacoustics output")
            exit()
        observer_id =list(range(observer_id, observer_id+1))


    if  window == "Hann":
        print("Hann Window")
    elif window == "None":
        print("Rectangular Window")
    else:
        print("Invalid windowing option selected")



    if weighting == "A":
        print("A-weighted output")
        f = open(output, "w")
        f.write("observer_id, dBA \n")

    elif weighting == "None":
        f = open(output, "w")
        print("Non-weighted output")
        f.write("observer_id, dB \n")
    else:
         print("Invalid weighting option selected")

    
    for i_observer in observer_id:
        print(f'Observer ID = {i_observer}')
        #Assuming constant time step size for now
        time_step_size = acoustics_data[f"time"][1]-acoustics_data[f"time"][0]
        #Apply windowing function (even if no windowing is specified, script still goes through this function with a rectangular window applied).
        windowed_pressure = apply_windowing_function(acoustics_data, i_observer, window)
        #Compute spectrum and OASPL values
        frequency, SPL, OASPL = compute_spectrum(windowed_pressure, time_step_size, i_observer, weighting, output)
        if np.isnan(OASPL)==0:
            observer_id_all = np.append(observer_id_all, i_observer)
            OASPL_all = np.append(OASPL_all, OASPL)
        
        #Output CSV file containing OASPL values
        if np.isnan(OASPL)==0:
            f.write("{}, {:.5f} \n".format(i_observer,OASPL))
        else:
            OASPL = 0
            f.write("{}, {:.5f} \n".format(i_observer,OASPL))


        #Plot spectral response
        if (np.isnan(SPL).any())==0:
            plot_spectrum(frequency, SPL, i_observer, weighting, window)
    plot_OASPL(observer_id_all, OASPL_all, weighting, window)

def main():
    input = "09caab3a-dc97-4f40-9727-0fe94818cdf1_total_acoustics_v3.csv"    
    acoustics_output(input, output="OASPL.csv", window="Hann", weighting="A", observer_id = -1)

if __name__ == '__main__':
    main()

