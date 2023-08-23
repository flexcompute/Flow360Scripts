
import os
import argparse

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import matplotlib.ticker as ticker

import flow360client

def getCaseConfigParameters(caseId):
    return flow360client.case.GetCaseInfo(caseId)['runtimeParams']

def readAcousticCSVFile(acsv):
    # read acoustic csv when the file is available via python api
    # with tempfile.TemporaryDirectory() as tmpdir:
    #     tmpfile = os.path.join(tmpdir, 'aeroacoustics_v3.csv')
    #     flow360client.case.DownloadFile(caseId, 'aeroacoustics_v3.csv', tmpfile)
    pressure_data = pd.read_csv(acsv,skipinitialspace=True)
    times = pressure_data['physical_time']
    steps = pressure_data['physical_step']
    p = pressure_data.iloc[:,2:-1]
    return [np.array(times),np.array(steps),np.array(p)]

def filterZeroAcousticData(time,steps,pressure):
    numObservers = pressure.shape[-1]
    acoustic_data_indices = {}
    acoustic_data = {}
    # loop over observers to find where they are zero
    for i in range(numObservers):
        p_observer = pressure[:,i]
        acoustic_data_indices[i] = np.where(p_observer!=0)[0]
    first_elements = []
    last_elements = []
    # lists of elements with zeros at begin and end
    for i in range(numObservers):
        first_elements.append(acoustic_data_indices[i][0])
        last_elements.append(acoustic_data_indices[i][-1])
    # max index where still there is a zero element for all observers
    start_index = max(first_elements)
    # min index where still there is a zero element for all observers
    end_index = min(last_elements)

    # physical time and step where all observers all non zero
    acoustic_data['physical_time'] = time[start_index:end_index]
    acoustic_data['physical_step'] = steps[start_index:end_index]

    # non-zero acoustic data for all observers with the same physical time
    for i in range(numObservers):
        p_observer = pressure[:,i]
        acoustic_data[i] = p_observer[start_index:end_index]
    return acoustic_data

def cal_spl(signal_amp):
    p_ref=2e-5
    return 10*np.log10(signal_amp/p_ref)

def plot_response(name,freq,resp,key):
    fig, ax = plt.subplots()
    # optional axis limit
    ax.axis([100, 18000, 0, 70])
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

    plotTitle = f'Noise Spectrum - Observer {key}' if key != 'avg' else f'Noise Spectrum - Averaged'
    plt.title(plotTitle, fontsize=10)
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

def getSpectrum(aSound,rho,acsv,oName):
    # reference sound pressure in air
    p_ref = 2e-5

    # reads acoustic csv file
    tt,stp,pdata = readAcousticCSVFile(acsv)
    # filters zeros from acoustic data
    acoustic_data = filterZeroAcousticData(tt,stp,pdata)
    # number of observers based on acoustic data
    numObservers = len(acoustic_data)-2

    # output file basename
    outFileName = os.path.splitext(os.path.basename(oName))[0]
    # output oaspl file in dat format
    oasplFile = os.path.join(os.curdir,outFileName+'_OASPL'+'.dat')
    print(f"variables=i,{'oaspl_'+outFileName}",file=open(oasplFile, 'w'))
    
    # initialized avg spectrum
    avg_response = 0
    # loop over observers
    for i in range(numObservers):
        # get physical time from acoustic data
        tt = acoustic_data['physical_time']
        # get acoustic pressures for an observer
        pp = acoustic_data[i]
        # convert to dimensional pressure
        pp = pp * rho * (aSound**2)
        # get the mean pressure for the observer
        p0 = np.mean(pp)
        # get the RMS for the pressure fluctuations
        p_rms = np.sqrt(np.mean((pp - p0)**2))
        # get the overall sound pressure based on pressure fluctuations
        spl = 20 * np.log10(p_rms/p_ref)
        # print oaspl
        print('Observer {} | OASPL: {:.5f} dB'.format(i,spl))
        # print oaspl in the file
        print("{}, {:.5f}".format(i,spl),file=open(oasplFile, 'a'))

        # get the mean time step size for pressure fluctuations
        meanStepSize = (tt[1:] - tt[:-1]).mean()
        # define the windowing function
        window = np.hanning(len(pp))
        # windowing checks
        # window /= window.mean()
        # window = 1 #no window

        # define the signal
        h =(pp - p0)*window
        # fft over the signal
        X = np.fft.fft(h)
        # get number of samples
        N = len(X)
        n_oneside = N//2
        # find the dimensional frequencies from the fft
        freq = np.fft.fftfreq(N,d=meanStepSize/aSound)
        freq_oneside = freq[:n_oneside]
        
        # calculate the sound pressure level
        response = cal_spl(np.abs(X[:n_oneside]))
        
        # collect the spectrum for averaging between observers
        avg_response += np.abs(response[:n_oneside])
        
        # plot the response
        plot_response(outFileName,freq_oneside,response[:n_oneside],i)
    
    # averaging the spectrum across all observers - which is useful in some cases 
    avg_response = avg_response/numObservers
    # plot the average spectrum
    plot_response(outFileName,freq_oneside,avg_response,'avg')
#end

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-csv',type=str,required=True)
    parser.add_argument('-o',type=str,required=True)
    args = parser.parse_args()
    scriptDir = os.getcwd()

    # speed of sound and density in SI for dimensional values
    a_speed = 340.3
    density = 1.225

    # getUnsteadyAerodynamicLoads(args.caseId)
    getSpectrum(a_speed,density,args.csv,args.o)


if __name__ == '__main__':
    main()