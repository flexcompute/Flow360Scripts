"""This script is used for post-processing of aeroacoustic pressure data
based on the PSU-WOPWOP 3.4.3 User Guide

Inputs:
The inputs are set at the top of the script.
The following inputs can be set:

INPUT: Name of the input file (typically of the form "{caseID}_total_acoustics_v3.csv"
WEIGHTING: Options for Non-weighted and A-weighted outputs. Valid inputs: "A" None
WINDOW: Options for a windowed or non-windowed signal. Valid inputs: "Hann" None
OUTPUT: Name of the output file
OBSERVER_ID: -1 corresponds to post-processing all observer ID's
or an integer corresponding to a single observer ID present in the input file.

Outputs:
A csv file containing the OASPL for each observerID
A plot of observerID vs OASPL
PNG files with the spectral plots for each observerID
"""

import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# User inputs
INPUT_FILE = "09caab3a-dc97-4f40-9727-0fe94818cdf1_total_acoustics_v3.csv"
OUTPUT_FILE = "OASPL.csv"
WINDOW = "Hann"
WEIGHTING = "A"
OBSERVER_ID = -1

# Input corresponding environmental conditions
GRID_UNIT = 1  # m
SPEED_OF_SOUND = 340  # m/s, freestream
RHO = 1.225  # kg/m^3, freestream
REFERENCE_SOUND_PRESSURE = 20e-6  # Pa

# Constants used for A-weighting
K1 = 2.243e16
K3 = 1.562
F1 = 20.599
F2 = 107.653
F3 = 737.862
F4 = 12194.220


def read_csv_file(file_path):
    """Read in the acoustics data input file and return a dict"""

    df = pd.read_csv(file_path, skipinitialspace=True)
    df = df.iloc[:, :-1]
    data = df.to_dict(orient="list")
    return data


def apply_windowing_function(acoustics_data, i_observer, window):
    """ "Apply the prescribed windowing function to observer data"""

    pressure = np.asarray(acoustics_data[f"observer_{i_observer}_pressure"])
    indices = np.nonzero(pressure)
    non_zero_pressure = pressure[indices]
    n = len(non_zero_pressure)  # number of time points in the time history

    # window correction."None"= No window, "Hann"= Hann Window
    if window == "Hann":
        window_function = np.hanning(n)
        fc = np.sqrt(n / sum(window_function**2))
    else:
        window_function = 1.0
        fc = 1.0
    # The windows that are actually applied to the time history are
    # the window functions multiplied by their respective scaling factor
    windowed_pressure = window_function * fc * non_zero_pressure
    return windowed_pressure


def compute_a_weight(f_m):
    """Compute the A weight"""

    w_cm = K1 * f_m**4 / ((f_m**2 + F1**2) ** 2 * (f_m**2 + F4**2) ** 2)
    w_am = w_cm * K3 * f_m**4 / ((f_m**2 + F2**2) * (f_m**2 + F3**2))
    return w_am


def compute_spectrum(windowed_pressure, time_step_size, weighting):
    """Compute the FFT of the pressure signal and then the OASPL and SPL spectrum"""
    # Number of discrete points in the time domain
    n = len(windowed_pressure)
    # Calculate dimensional quantities from Flow360 nondimensional data
    physical_pressure = windowed_pressure * RHO * SPEED_OF_SOUND**2  # Pa
    physical_time_step_size = time_step_size * GRID_UNIT / SPEED_OF_SOUND  # s
    # Compute the frequency step size
    frequency_step_size = 1.0 / (n * physical_time_step_size)
    # Compute the number of frequency bins
    m = int(np.floor(n / 2) + 1)
    # Compute the Nyquist frequency
    nyquist_frequency = np.floor(n / 2) * frequency_step_size
    # Compute the frequency array based on the minimum and maximum frequencies required to recreate the signal
    frequency = np.linspace(0, nyquist_frequency, m)
    # Compute the Fast Fourier Transform
    spectrum = np.fft.rfft(physical_pressure)

    # Calculate the complex pressure at each frequency bin
    p_c = np.zeros(m, dtype=complex)
    p_c[0] = spectrum[0] * 1 / n
    p_c[1:m] = spectrum[1:m] * 2 / n

    # If A-weighitng is selected, compute the weighted mean square pressure and then the SPL and OASPL values.
    if weighting == "A":
        weighted_mean_square_pressure = np.zeros(m)
        for k in range(0, m):
            f_m = frequency[k]
            w_am = compute_a_weight(f_m)
            weighted_mean_square_pressure[k] = 0.5 * w_am * np.abs(p_c[k]) ** 2
        spl = 10 * np.log10(
            weighted_mean_square_pressure / REFERENCE_SOUND_PRESSURE**2
        )
        oaspl = 10 * np.log10(
            sum(weighted_mean_square_pressure) / REFERENCE_SOUND_PRESSURE**2
        )
        if np.isnan(oaspl) == 0:
            print(f"OASPL [dBA] = {oaspl}")
        else:
            print("OASPL [dBA] = 0.0")
    # If no weighting is selected, compute the mean square pressure and then the SPL and OASPL values.
    else:
        mean_square_pressure = 0.5 * np.abs(p_c) ** 2
        spl = 10 * np.log10(mean_square_pressure / REFERENCE_SOUND_PRESSURE**2)
        oaspl = 10 * np.log10(sum(mean_square_pressure) / REFERENCE_SOUND_PRESSURE**2)
        if np.isnan(oaspl) == 0:
            print(f"OASPL [dB] = {oaspl}")
        else:
            print("OASPL [dB] = 0.0")

    return frequency, spl, oaspl


def plot_spectrum(frequency, spl, i_observer, weighting, window):
    """Plot the SPL spectra"""

    plt.figure(figsize=(8, 6))
    if weighting is None and window == "Hann":
        plot_title = "Noise Spectrum - Non-weighted, Hann Window - Observer " + str(
            i_observer
        )
    elif weighting is None and window is None:
        plot_title = "Noise Spectrum - Non-weighted, No Window - Observer " + str(
            i_observer
        )
    elif weighting == "A" and window is None:
        plot_title = "Noise Spectrum - A-weighted, No Window - Observer " + str(
            i_observer
        )
    elif weighting == "A" and window == "Hann":
        plot_title = "Noise Spectrum - A-weighted, Hann Window - Observer " + str(
            i_observer
        )

    plt.title(plot_title)

    if weighting == "A":
        plt.plot(frequency, spl, "-", label="dBA")
        plt.ylabel("SPL [dBA]", fontsize=10)

    else:
        plt.plot(frequency, spl, "-", label="dB")
        plt.ylabel("SPL [dB]", fontsize=10)

    plt.xscale("log")
    plt.xlabel("Frequency [Hz]", fontsize=10)
    plt.grid(which="major")
    plt.grid(which="minor", ls="--", color="gray", linewidth=0.5)
    plt.legend()
    plt.savefig(f"figures/spectrum_observer_{i_observer}", dpi=500)
    plt.close()


def plot_oaspl(observer_id_all, oaspl_all, weighting, window):
    """Plot the OASPL vs Observer ID"""

    plt.figure(figsize=(8, 6))
    if weighting is None and window == "Hann":
        plot_title = "OASPL - Non-weighted, Hann Window"
    elif weighting is None and window is None:
        plot_title = "OASPL - Non-weighted, No Window"
    elif weighting == "A" and window is None:
        plot_title = "OASPL - A-weighted, No Window"
    elif weighting == "A" and window == "Hann":
        plot_title = "OASPL, A-weighted, Hann Window"

    plt.title(plot_title)

    if weighting == "A":
        plt.scatter(observer_id_all, oaspl_all, label="dBA")
        plt.ylabel("OASPL [dBA]", fontsize=10)

    else:
        plt.scatter(observer_id_all, oaspl_all, label="dB")
        plt.ylabel("OASPL [dB]", fontsize=10)

    plt.xlabel("Observer ID", fontsize=10)
    plt.grid(which="major")
    plt.grid(which="minor", ls="--", color="k", linewidth=0.5)
    plt.legend()
    plt.savefig("figures/OASPL.png", dpi=500)
    plt.close()


def print_input_choices(observer_id, window, weighting, acoustics_data):
    """Print the input choices to the screen"""

    if observer_id == -1:
        print("Computing aeroacoustic output for all observers")
    else:
        print("Computing aeroacoustic output for observer ID " + str(observer_id))
        if observer_id >= len(acoustics_data) - 2:
            print("Observer ID not present in the aeroacoustics output")
            raise RuntimeError

    if window == "Hann":
        print("Hann Window")
    elif window is None:
        print("No Window")
    else:
        print("Invalid windowing option selected")
        raise RuntimeError

    if weighting == "A":
        print("A-weighted output")
    elif weighting is None:
        print("Non-weighted output")
    else:
        print("Invalid weighting option selected")
        raise RuntimeError


def acoustics_output(input_file, output, window, weighting, observer_id):
    """Drive the acoustics output"""

    oaspl_all = []
    observer_id_all = []
    os.makedirs("figures", exist_ok=True)

    acoustics_data = read_csv_file(input_file)
    print_input_choices(observer_id, window, weighting, acoustics_data)

    if observer_id == -1:
        n_observer = len(acoustics_data) - 2
        observer_list = list(range(0, n_observer))
    else:
        observer_list = list(range(observer_id, observer_id + 1))

    if weighting == "A":
        with open(output, "w", encoding="utf-8") as f:
            f.write("observer_id, dBA \n")
    elif weighting is None:
        with open(output, "w", encoding="utf-8") as f:
            f.write("observer_id, dB \n")

    for i_observer in observer_list:
        print(f"Observer ID = {i_observer}")
        # Assuming constant time step size for now
        time_step_size = acoustics_data["time"][1] - acoustics_data["time"][0]
        # Apply windowing function (even if no windowing is specified, then rectangular window applied)
        windowed_pressure = apply_windowing_function(acoustics_data, i_observer, window)
        # Compute spectrum and OASPL values
        frequency, spl, oaspl = compute_spectrum(
            windowed_pressure, time_step_size, weighting
        )
        if np.isnan(oaspl) == 0:
            observer_id_all = np.append(observer_id_all, i_observer)
            oaspl_all = np.append(oaspl_all, oaspl)

        # Output CSV file containing OASPL values
        if np.isnan(oaspl) == 0:
            with open(output, "a", encoding="utf-8") as f:
                f.write(f"{i_observer}, {oaspl:.5f} \n")
        else:
            oaspl = 0
            with open(output, "a", encoding="utf-8") as f:
                f.write(f"{i_observer}, {oaspl:.5f} \n")

        # Plot spectral response
        if (np.isnan(spl).any()) == 0:
            plot_spectrum(frequency, spl, i_observer, weighting, window)
    plot_oaspl(observer_id_all, oaspl_all, weighting, window)


acoustics_output(INPUT_FILE, OUTPUT_FILE, WINDOW, WEIGHTING, OBSERVER_ID)
