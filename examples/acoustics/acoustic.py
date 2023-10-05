
import os
import argparse

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import matplotlib.ticker as ticker

def read_acoustic_file(a_csv):
    pressure_data = pd.read_csv(a_csv,skipinitialspace=True)
    times = pressure_data['time']
    steps = pressure_data['physical_step']
    p = pressure_data.iloc[:,2:-1]
    return [np.array(times),np.array(steps),np.array(p)]

def filter_zero_data(time,steps,pressure,observerId):
    # dictionary of acoustic data for filtering
    acoustic_data_indices = {}
    acoustic_data = {}
    # number of observers and their length
    num_observers = pressure.shape[-1]
    length_observers = pressure.shape[0]
    # default when observerId is not given
    observerId_start = 0
    observerId_end = num_observers
    # list of indices of first and last non-zero elements for observers
    first_elements = []
    last_elements = []
    # all input as data
    data = np.column_stack((steps,time,pressure))
    
    # when observerId is given
    if observerId is not None:
        # when id is within range
        if observerId >= 0 and observerId <= num_observers-1:
            observerId_start = observerId
            observerId_end = observerId+1
            num_observers = 1
        # when id is not within range
        else:
            print("Observer Id doesn't exist")
            exit()
    
    # loop over observers to find where they are not zero
    for i in range(observerId_start,observerId_end,1):
        p_observer = data[:,i+2]
        acoustic_data_indices[i] = np.where(p_observer!=0)[0]

    # lists of indices of elements at the beginning or/and ending where they are not zero
    for i in range(observerId_start,observerId_end,1):
        if len(acoustic_data_indices[i]) != 0:
            first_elements.append(acoustic_data_indices[i][0])
            last_elements.append(acoustic_data_indices[i][-1])
        # when all data for an observer are zero
        else:
            first_elements.append(0)
            last_elements.append(length_observers)
    
    # max index where still there is a zero element for all observers
    start_index = max(first_elements)
    # min index where still there is a zero element for all observers
    end_index = min(last_elements)+1

    # physical time and step where all observers all non zero
    acoustic_data['time'] = time[start_index:end_index]
    acoustic_data['physical_step'] = steps[start_index:end_index]

    # non-zero acoustic data for all observers with the same physical time
    for i in range(observerId_start,observerId_end,1):
        p_observer = data[:,i+2]
        acoustic_data[i] = p_observer[start_index:end_index]
    return [observerId_start,observerId_end,num_observers,acoustic_data]

# based on signal amplitude
def cal_decibel_amplitude(p):
    p_ref = 2e-5
    return 20 * np.log10(p/p_ref)

# based on signal power
def cal_decibel_power(p):
    p_ref = 2e-5
    return 10 * np.log10(p / p_ref**2)
#end

def plot_response(name,freq,resp,key):
    fig, ax = plt.subplots()
    # optional axis limit
    # ax.axis([100, 18000, 0, 70])
    plt.plot(freq,resp,'crimson',linewidth=0.8,marker='o',markersize=0.8)
    plt.xscale('log')
    for axis in [ax.xaxis, ax.yaxis]:
        formatter = ticker.ScalarFormatter()
        formatter.set_scientific(False)
        axis.set_major_formatter(formatter)
    ax.yaxis.set_minor_formatter(formatter)
    ax.xaxis.set_minor_formatter(formatter)
    
    # optional log minor ticker
    ax.xaxis.set_minor_locator(ticker.LogLocator(base=10.0, subs=(0.2, 0.4, 0.6, 0.8), numticks=5))

    plot_title = f'Noise Spectrum - Observer {key}' if key != 'avg' else f'Noise Spectrum - Averaged'
    plt.title(plot_title, fontsize=10)
    plt.xlabel('Frequency [Hz]', fontsize=10)
    plt.ylabel('SPL [dB]', fontsize=10)
    plt.grid(which='major')
    plt.grid(which='minor', ls='--',color='k',linewidth=0.5)
    ax.tick_params(axis='x',which='major',labelsize=8,pad=10)
    ax.tick_params(axis='y',which='major',labelsize=8)
    ax.tick_params(axis='both',which='minor',labelsize=5)
    
    # figure resolution
    plt.rcParams['figure.dpi'] = 500
    plt.rcParams['savefig.dpi'] = 500
    plt.savefig(f'{name}_narrow-band_spectra_{key}.png', bbox_inches='tight')
    plt.close()

def get_spectrum(a_sound,rho,a_csv,o_name,obsrId):
    # reads acoustic csv file
    tt,stp,pdata = read_acoustic_file(a_csv)
    # filters zeros from acoustic data
    startId,endId,num_observers,acoustic_data = filter_zero_data(tt,stp,pdata,obsrId)
    
    # output file basename
    out_file = os.path.splitext(os.path.basename(o_name))[0]
    # output oaspl file in dat format
    oaspl_file = os.path.join(os.curdir,out_file+'_OASPL'+'.dat')
    print(f"variables=i,{'oaspl_'+out_file}",file=open(oaspl_file, 'w'))
    
    # initialized avg spectrum
    avg_response = 0
    # loop over observers
    for i in range(startId,endId,1):
        # get physical time from acoustic data
        tt = acoustic_data['time']
        # get acoustic pressures for an observer
        pp = acoustic_data[i]
        # convert to dimensional pressure
        pp = pp * rho * (a_sound**2)
        # get the mean pressure for the observer
        p0 = np.mean(pp)
        # get the RMS for the pressure fluctuations
        p_rms = np.sqrt(np.mean((pp - p0)**2))
        # get the overall sound pressure based on pressure fluctuations
        spl = cal_decibel_amplitude(p_rms)
        # print oaspl
        print('Observer {} | OASPL: {:.5f} dB'.format(i,spl))
        # print oaspl in the file
        print("{}, {:.5f}".format(i,spl),file=open(oaspl_file, 'a'))

        # get the mean time step size for pressure fluctuations
        mean_step_size = (tt[1:] - tt[:-1]).mean()
        # define the windowing function
        window = np.hanning(len(pp))
        # windowing checks
        # window /= window.mean()
        # window = np.ones(len(pp)) #no window

        # sums for normalization purpose - equation 19 and 20
        s1 = sum(window)
        s2 = sum(window**2)
        # sampling frequency - section 7
        fs = 1/(mean_step_size/a_sound)
        # effective noise bandwidth - equation 22
        enbw = 2 * fs * (s2 / s1**(5/2))
        # define the signal
        h =(pp - p0)*window
        # fft over the signal
        X = np.fft.fft(h)
        # get number of samples
        N = len(X)
        n_oneside = N//2
        # find the dimensional frequencies from the fft
        freq = np.fft.fftfreq(N,d=mean_step_size/a_sound)
        freq_oneside = freq[:n_oneside]
        
        # power spectrum - equation 23
        psX = (2 * np.abs(X[:n_oneside])**2) / s1**2
        # power spectrum density - equation 24
        psdX = psX / enbw
        # linear spectrum density - equation 25
        lsdX = np.sqrt(psdX)
        # linear spectrum - equation 26
        lsX = np.sqrt(psX)

        # calculate the sound pressure level
        # response = cal_decibel_amplitude(lsX)
        response = cal_decibel_power(psdX)
        
        # collect the spectrum for averaging between observers
        avg_response += np.abs(response)
        
        # plot the response
        plot_response(out_file,freq_oneside,response,i)
    
    # averaging the spectrum across all observers - which is useful in some cases 
    avg_response = avg_response/num_observers
    # plot the average spectrum
    plot_response(out_file,freq_oneside,avg_response,'avg')
#end

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i','--input',help='Specify the input aeroacoustic CSV file. For example: <caseId>_aeroacoustics_v3.csv',type=str,required=True)
    parser.add_argument('-n','--observerId',help='Observer Id number for acoustic pos-processing.',type=int,required=False)
    parser.add_argument('-o','--output',help='Specify the output file name for calculated OASPL.',type=str,required=True)
    args = parser.parse_args()
    scriptDir = os.getcwd()

    # speed of sound and density in SI for dimensional values
    a_speed = 340.3
    density = 1.225

    # getUnsteadyAerodynamicLoads(args.caseId)
    get_spectrum(a_speed,density,args.input,args.output,args.observerId)
#end

if __name__ == '__main__':
    main()