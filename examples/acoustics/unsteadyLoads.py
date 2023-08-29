
import os, tempfile
import argparse

import numpy as np
import pandas as pd
import json
from matplotlib import pyplot as plt
import matplotlib.ticker as ticker

import flow360client

def separator(n=20):
    return "-"*n

# read json cofig file
def read_json_input(json_in):
    with open(json_in,'r') as jconfig:
        configdata = jconfig.read()
    config = json.loads(configdata)
    return config
#end

def get_case_config_parameters(caseId):
    if caseId is not None:
        return flow360client.case.GetCaseInfo(caseId)['runtimeParams']
    else:
        return None
#end

def get_total_forces_per_physical_steps(caseId,input,starting_step):
    if caseId is not None:
        total_forces_data = flow360client.case.GetCaseTotalForces(caseId)
    else:
        total_forces_data = pd.read_csv(input,skipinitialspace=True)

    steps = total_forces_data['physical_step']
    cl = total_forces_data['CL']
    cd = total_forces_data['CD']
    cfz = total_forces_data['CFz']
    cm = total_forces_data['CMz']
    
    # finds the starting line after the starting step
    for i in range(len(steps)):
        if steps[i] == starting_step:
            initialLine = i+1

    # crates array for coefficient after the starting step
    steps = np.array(steps[initialLine:None])
    cl = np.array(cl[initialLine:None])
    cd = np.array(cd[initialLine:None])
    cfz = np.array(cfz[initialLine:None])
    cm = np.array(cm[initialLine:None])
    
    current_row_step = steps[0]
    last_row_step = steps[-1]
    print('Starting physical step: {}'.format(current_row_step))
    print('Ending physical step: {}'.format(last_row_step))

    i = 0
    steps_inst=[]
    cl_inst = []
    cd_inst = []
    cfz_inst = []
    cm_inst = []
    
    # taking last values at end of each physical step
    while current_row_step != last_row_step:
        if current_row_step != steps[i+1]:
            steps_inst.append(steps[i])
            cl_inst.append(cl[i])
            cd_inst.append(cd[i])
            cfz_inst.append(cfz[i])
            cm_inst.append(cm[i])
        i+=1
        current_row_step= int(steps[i])
    
    # adding the last values at end of the last physical step
    steps_inst.append(steps[-1])
    cl_inst.append(cl[-1])
    cd_inst.append(cd[-1])
    cfz_inst.append(cfz[-1])
    cm_inst.append(cm[-1])

    # list of array to return
    return_list = []
    for val in [steps_inst,cl_inst,cd_inst,cfz_inst,cm_inst]:
        return_list.append(np.array(val))
    
    # returning coefficients converged at each physical step
    return return_list

def get_reference_parameters(case_config,ref_input):
    if case_config is not None:
        ref_config = case_config
        print('Reference values are taken based on the provided caseId.')
    elif ref_input is not None:
        ref_config = read_json_input(ref_input)
        print(f'Reference values are taken based on the provided input file: {ref_input}.')
    else:
        print('No reference input values are provided. Please enter reference values to continue.')
        print(separator(50))
        ref_config = {'geometry': {'refArea': 0, 'momentLength': []}, 'freestream': {'MachRef': 0, 'alphaAngle': 0, 'betaAngle': 0}, 'slidingInterfaces': [{'omega': 0}], 'timeStepping': {'timeStepSize': 0}}
        ref_config['geometry']['refArea'] = float(input("Enter reference area: "))
        moment_length_list = [int(item) for item in input("Enter three numbers for moment reference length as ref_mx ref_my ref_mz: ").split()]
        ref_config['geometry']['momentLength'] = moment_length_list
        ref_config['freestream']['MachRef'] = float(input("Enter reference Mach number: "))
        ref_config['freestream']['alphaAngle'] = float(input("Enter free-stream alpha angle in degrees: "))
        ref_config['freestream']['betaAngle'] = float(input("Enter free-stream beta angle in degrees: "))
        ref_config['slidingInterfaces'][0]['omega'] = float(input("Enter reference non-dimensional rotational speed in rad/sec: "))
        ref_config['timeStepping']['timeStepSize'] = float(input("Enter non-dimensional step size used: "))
    print(separator(50))

    ref_area = ref_config['geometry']['refArea']
    moment_length = np.array(ref_config['geometry']['momentLength'])
    mach_ref = ref_config['freestream']['MachRef']
    assert abs(mach_ref) > 1.e-15
    alpha = ref_config['freestream']['alphaAngle']
    beta = ref_config['freestream']['betaAngle']
    omega = ref_config['slidingInterfaces'][0]['omega']
    time_step = ref_config['timeStepping']['timeStepSize']
    return [ref_area,moment_length,mach_ref,alpha,beta,omega,time_step]
#end

def report_ref_values(refs):
    print(f'refArea: {refs[0]}')
    print(f'momentLength: {refs[1]}')
    print(f'MachRef: {refs[2]}')
    print(f'alphaAngle: {refs[3]}')
    print(f'betaAngle: {refs[4]}')
    print(f'omega: {refs[5]}')
    print(f'timeStepSize: {refs[6]}')
#end

def plot_torque_thrust_coefficients(rev,CQ,CQ_sigma,CT,CT_sigma,output):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    lns1 = ax.plot(rev,CQ, '-b', label='$C_{Q}$', linewidth=0.6)
    ax.fill_between(rev,(CQ + CQ_sigma),(CQ - CQ_sigma),color='gray',alpha=0.15)
    ax.fill_between(rev,(CQ + 2 * CQ_sigma),(CQ - 2 * CQ_sigma),color='crimson',alpha=0.15)
    ax2=ax.twinx()
    lns2 = ax2.plot(rev,CT, '-r', label='$C_{T}$', linewidth=0.6)
    ax2.fill_between(rev,(CT + CT_sigma),(CT - CT_sigma),color='gray',alpha=0.2)
    ax2.fill_between(rev,(CT + 2 * CT_sigma),(CT - 2 * CT_sigma),color='green',alpha=0.15)
    lns = lns1+lns2
    labs = [l.get_label() for l in lns]
    ax.legend(lns, labs, loc =0, frameon=False)

    plt.title("Torque and Thrust Coefficients", fontsize=12)
    ax.set_xlabel('Revolutions', fontsize=10)
    ax.set_ylabel('$C_{Q}$', fontsize=10)
    ax2.set_ylabel('$C_{T}$', fontsize=10)
    ax2.set_yticks(np.arange(0.0075,0.0125,0.001))
    plt.savefig(f'{output}_ctcq_coef.png', bbox_inches='tight', dpi=600)
    plt.close()
#end

def plot_torque_thrust(rev,moment,moment_sigma,thrust,thrust_sigma,output):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    lns1 = ax.plot(rev,moment, '-b', label='$Torque$', linewidth=0.6)
    ax.fill_between(rev,(moment + moment_sigma),(moment - moment_sigma),color='gray',alpha=0.15)
    ax.fill_between(rev,(moment + 2 * moment_sigma),(moment - 2 * moment_sigma),color='crimson',alpha=0.15)
    ax2=ax.twinx()
    lns2 = ax2.plot(rev,thrust, '-r', label='$Thrust$', linewidth=0.6)
    ax2.fill_between(rev,(thrust + thrust_sigma),(thrust - thrust_sigma),color='gray',alpha=0.15)
    ax2.fill_between(rev,(thrust + 2 * thrust_sigma),(thrust - 2 * thrust_sigma),color='green',alpha=0.15)
    lns = lns1+lns2
    labs = [l.get_label() for l in lns]
    ax.legend(lns, labs, loc =0, frameon=False)

    plt.title("Torque and Thrust", fontsize=12)
    ax.set_xlabel('Revolutions', fontsize=10)
    ax.set_ylabel('Torque (N.m)', fontsize=10)
    ax2.set_ylabel('Thrust (N)', fontsize=10)
    ax2.set_yticks(np.arange(2,4.5,0.5))
    plt.savefig(f'{output}_torque_thrust.png', bbox_inches='tight', dpi=600)
    plt.close()
#end

def plot_Cfz_moment_coeffcients(rev,CFz,CFz_sigma,CM,CM_sigma,output):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    lns1 = ax.plot(rev,CM, '-b', label='$C_{M}$', linewidth=0.6)
    ax.fill_between(rev,(CM + CM_sigma),(CM - CM_sigma),color='gray',alpha=0.15)
    ax.fill_between(rev,(CM + 2 * CM_sigma),(CM - 2 * CM_sigma),color='crimson',alpha=0.15)
    ax2=ax.twinx()
    lns2 = ax2.plot(rev,CFz, '-r', label='$C_{Fz}$', linewidth=0.6)
    ax2.fill_between(rev,(CFz + CFz_sigma),(CFz - CFz_sigma),color='gray',alpha=0.15)
    ax2.fill_between(rev,(CFz + 2 * CFz_sigma),(CFz - 2 * CFz_sigma),color='green',alpha=0.15)
    lns = lns1+lns2
    labs = [l.get_label() for l in lns]
    ax.legend(lns, labs, loc =0, frameon=False)

    plt.title("Force Coefficients", fontsize=12)
    ax.set_xlabel('Revolutions', fontsize=10)
    ax.set_ylabel('$C_{M}$', fontsize=10)
    ax2.set_ylabel('$C_{Fz}$', fontsize=10)
    ax2.set_yticks(np.arange(0.02,0.03,0.001))
    plt.savefig(f'{output}_cfzcm_coef.png', bbox_inches='tight', dpi=600)
    plt.close()
#end

def get_forces_per_intervals(values,num_intervals):
    min = 0
    max = len(values[0])
    interval_size = int(np.round((max - min) / num_intervals))

    interval_vars = {}
    interval_id = 0
    for start in range(min,max,interval_size):
        end = start + interval_size
        var_tmp = []
        i = 0
        for var in values:
            var_tmp.append(var[start:end])
            i+=1
        interval_vars[f'{interval_id}'] = var_tmp
        interval_id+=1
    return interval_vars
#end

def cal_confidence_bound(data,n_interval):

    # separate data into number of intervals
    data_per_chunk = get_forces_per_intervals(data,n_interval)
    num_forces = len( list( data_per_chunk.values() )[0] )

    # dict holding averaged values per interval for all data
    data_averaged_per_chunk = {}
    # loop over number of intervals
    for i in range(n_interval):
        # get the chunk of data in i interval
        chunk_vars = data_per_chunk[ f'{i}' ]
        # temporary list for averaged values in this chunk
        averaged_list = []
        # loop over data 
        for data in chunk_vars:
            # calculate the averaged value
            averaged_value = np.mean(data)
            # append it to list
            averaged_list.append(averaged_value)
        # assign the averaged list to a dict
        data_averaged_per_chunk[ f'chunk_{i}' ] = averaged_list
    
    # convert the averaged dict for all forces at each interval to an array
    data_averaged = np.array(list( data_averaged_per_chunk.values() ))
    # calculate population mean for averaged values in all chunks
    data_averaged_mean = []
    for iforce in range(num_forces):
        data_averaged_mean.append(np.mean( data_averaged[:,iforce] ))
    
    # calculate standard deviation of averaged forces across all chunks
    sigma_forces = []
    for iforce in range(num_forces):
        sigma_forces.append(np.sqrt( np.mean( ( data_averaged[:,iforce]-data_averaged_mean[iforce] )**2 ) ))
    
    confidence_bound = sigma_forces / np.sqrt(n_interval)
    return [ sigma_forces ,confidence_bound ]


def get_unsteady_loads(a_sound,rho,L_grid,input,output,ref_input,start=0,pervious_rev=0):
    
    # check if the input is a file or caseId
    isExist = os.path.exists(input)
    if isExist:
        caseId = None
        print('For Input File: {}'.format(input))
    else:
        caseId = input
        print('For Input CaseId: {}'.format(caseId))
    print(separator(70))

    # fetching case parameters
    case_config = get_case_config_parameters(caseId)
    # fetching reference parameters
    ref = get_reference_parameters(case_config,ref_input)
    # reporting back the reference values
    report_ref_values(ref)

    # assigning reference parameters including:
    # non dimensional omega in rad/s
    omega = ref[5]
    # dimensional rpm for check
    rpm = omega * (60 / (2*np.pi)) * (a_sound / L_grid)
    # reference area
    area_ref = ref[0]
    # radius based on reference area
    radius = np.sqrt(area_ref / np.pi)
    # reference mach no
    mach_ref = ref[2]
    # reference moment in z direction
    moment_z_ref = ref[1][2]
    # reference velocity based on mach ref
    velocity_ref = mach_ref * a_sound
    # number of physical steps per one revolution
    steps_per_revolution = np.floor((2 * np.pi / omega) / ref[6])
    # filter forces at the end of each physical step
    vars = get_total_forces_per_physical_steps(caseId,input,start)
    print(separator(50))

    # revolution progress
    rev = [((i-start)/steps_per_revolution)+pervious_rev for i in vars[0]]

    # coefficients
    CL,CD,CFz,CM = vars[1:]

    # average of coefficients
    averaged_CL = np.mean(CL)
    averaged_CD = np.mean(CD)
    averaged_CFz = np.mean(CFz)
    averaged_CM = np.mean(CM)

    # rms values based on root mean square of instantaneous values
    RMScl = np.sqrt(np.mean(CL**2))
    RMScd = np.sqrt(np.mean(CD**2))
    RMScfz = np.sqrt(np.mean(CFz**2))
    RMScm = np.sqrt(np.mean(CM**2))

    # +/- values
    varCL = np.mean([abs(averaged_CL - np.min(CL)), np.max(CL) - averaged_CL])
    varCD = np.mean([abs(averaged_CD - np.min(CD)), np.max(CD) - averaged_CD])
    varCFz = np.mean([abs(averaged_CFz - np.min(CFz)), np.max(CFz) - averaged_CFz])
    varCM = np.mean([abs(averaged_CM - np.min(CM)), np.max(CM) - averaged_CM])

    # lift force based on RMScl
    lift_force = 0.5 * RMScl * rho * (velocity_ref**2) * area_ref
    # instantaneous lift
    lift_inst = 0.5 * CL * rho * (velocity_ref**2) * area_ref
    # drag force
    drag_force = 0.5 * RMScd * rho * (velocity_ref**2) * area_ref
    # instantaneous drag
    drag_inst = 0.5 * CD * rho * (velocity_ref**2) * area_ref
    # force based cfz
    skinFricZ_force = 0.5 * RMScfz * rho * (velocity_ref**2) * area_ref
    # instantaneous drag
    skinFricZ_inst = 0.5 * CFz * rho * (velocity_ref**2) * area_ref
    # moment z
    moment_z = 0.5 * RMScm * rho * (velocity_ref**2) * area_ref * moment_z_ref
    # instantaneous moment
    moment_z_inst = 0.5 * CM * rho * (velocity_ref**2) * area_ref * moment_z_ref

    # thrust is in z direction
    thrust_force = skinFricZ_force
    # instantaneous thrust
    thrust_inst = skinFricZ_inst
    
    # non-dimensional thrust
    non_dim_thrust = thrust_inst / (rho * (a_sound**2) * (L_grid**2))
    # non-dimensional moment
    non_dim_moment = moment_z_inst / (rho * (a_sound**2) * (L_grid**3))
    # instantaneous thrust coefficient
    CT = non_dim_thrust / (rho * area_ref * ((omega*radius)**2))
    # instantaneous torque coefficient
    CQ = non_dim_moment / (rho * ((omega * radius)**2) * area_ref * radius)
    
    # rms of thrust and torque coefficients
    RMSct = np.sqrt(np.mean(CT**2))
    RMScq = np.sqrt(np.mean(CQ**2))
    # averaged value of thrust and torque
    averaged_CT = np.mean(CT)
    averaged_CQ = np.mean(CQ)
    # +/- values for thrust and torque coefficients
    varCT = np.mean([abs(averaged_CT - np.min(CT)), np.max(CT) - averaged_CT])
    varCQ = np.mean([abs(averaged_CQ - np.min(CQ)), np.max(CQ) - averaged_CQ])

    # calculate standard deviation, one-sigma and two-sigma confidence bounds
    num_intervals = 5
    data = [CL,CD,CFz,CM,CT,CQ]
    dev,one_sigma_confidence = cal_confidence_bound(data, num_intervals)
    two_sigma_confidence = 2 * one_sigma_confidence

    CL_one_sigma_bound = one_sigma_confidence[0]
    CD_one_sigma_bound = one_sigma_confidence[1]
    CFz_one_sigma_bound = one_sigma_confidence[2]
    CM_one_sigma_bound = one_sigma_confidence[3]
    CT_one_sigma_bound = one_sigma_confidence[4]
    CQ_one_sigma_bound = one_sigma_confidence[5]

    CL_two_sigma_bound = two_sigma_confidence[0]
    CD_two_sigma_bound = two_sigma_confidence[1]
    CFz_two_sigma_bound = two_sigma_confidence[2]
    CM_two_sigma_bound = two_sigma_confidence[3]
    CT_two_sigma_bound = two_sigma_confidence[4]
    CQ_two_sigma_bound = two_sigma_confidence[5]

    thrust_deviation = 0.5 * dev[2] * rho * (velocity_ref**2) * area_ref
    thrust_one_sigma_bound = 0.5 * CFz_one_sigma_bound * rho * (velocity_ref**2) * area_ref
    torque_deviation = 0.5 * dev[3] * rho * (velocity_ref**2) * area_ref * moment_z_ref
    torque_one_sigma_bound = 0.5 * CM_one_sigma_bound * rho * (velocity_ref**2) * area_ref * moment_z_ref

    # report
    print("CL = %.6f" % (averaged_CL) + " +/- %.6f" % (varCL))
    print("RMS CL = %.6f" % (RMScl))
    print("Standard Deviation CL = %.6f" % (dev[0]))
    print("One-Sigma Bound CL = %.6f" % (CL_one_sigma_bound))
    print("Two-Sigma Bound CL = %.6f" % (CL_two_sigma_bound))
    print(separator(40))
    
    print("CD = %.6f" % (averaged_CD) + " +/- %.6f" % (varCD))
    print("RMS CD = %.6f" % (RMScd))
    print("Standard Deviation CD = %.6f" % (dev[1]))
    print("One-Sigma Bound CD = %.6f" % (CD_one_sigma_bound))
    print("Two-Sigma Bound CD = %.6f" % (CD_two_sigma_bound))
    print(separator(40))

    print("CFz = %.6f" % (averaged_CFz) + " +/- %.6f" % (varCFz))
    print("RMS CFz = %.6f" % (RMScfz))
    print("Standard Deviation CFz = %.6f" % (dev[2]))
    print("One-Sigma Bound CFz = %.6f" % (CFz_one_sigma_bound))
    print("Two-Sigma Bound CFz = %.6f" % (CFz_two_sigma_bound))
    print(separator(40))

    print("CM = %.6f" % (averaged_CM) + " +/- %.6f" % (varCM))
    print("RMS CM = %.6f" % (RMScm))
    print("Standard Deviation CM = %.6f" % (dev[3]))
    print("One-Sigma Bound CM = %.6f" % (CM_one_sigma_bound))
    print("Two-Sigma Bound CM = %.6f" % (CM_two_sigma_bound))
    print(separator(40))

    print("CT = %.6f" % (averaged_CT) + " +/- %.6f" % (varCT))
    print("RMS CT = %.6f" % (RMSct))
    print("Standard Deviation CT = %.6f" % (dev[4]))
    print("One-Sigma Bound CT = %.6f" % (CT_one_sigma_bound))
    print("Two-Sigma Bound CT = %.6f" % (CT_two_sigma_bound))
    print(separator(40))

    print("CQ = %.6f" % (averaged_CQ) + " +/- %.6f" % (varCQ))
    print("RMS CQ = %.6f" % (RMScq))
    print("Standard Deviation CQ = %.6f" % (dev[5]))
    print("One-Sigma Bound CQ = %.6f" % (CQ_one_sigma_bound))
    print("Two-Sigma Bound CQ = %.6f" % (CQ_two_sigma_bound))
    print(separator(40))

    # figure of merit
    fom = (abs(averaged_CT)**( 3 / 2))/(np.sqrt(2) * abs(averaged_CQ))

    print("Thrust (N) = %.4f" % (thrust_force))
    print("Standard Deviation Thrust = %.6f" % (thrust_deviation))
    print("One-Sigma Bound Thrust = %.6f" % (thrust_one_sigma_bound))
    print("Torque (N.m) = %.4f" % (moment_z))
    print("Standard Deviation Torque = %.6f" % (torque_deviation))
    print("One-Sigma Bound Torque = %.6f" % (torque_one_sigma_bound))
    print(separator(40))
    print("FoM = %.4f" % (fom))

    # output file basename
    out_file_name = os.path.splitext(os.path.basename(output))[0]
    # output file in dat format
    force_file = os.path.join(os.curdir,out_file_name+'_thrust_torque'+'.dat')
    print("variables=cl,cd,cfz,cmz,ct,cq,fom,thrust,torque",file=open(force_file, 'w'))
    print("{0},  {1},  {2},  {3},  {4},  {5},  {6},  {7}".format(RMScl, RMScd, RMScfz, RMScm, RMSct, RMScq, fom, thrust_force, moment_z),file=open(force_file, 'a'))

    plot_torque_thrust_coefficients(rev, CQ, CQ_one_sigma_bound, CT, CT_one_sigma_bound, out_file_name)
    plot_Cfz_moment_coeffcients(rev, CFz, CFz_one_sigma_bound, CM, CM_one_sigma_bound, out_file_name)
    plot_torque_thrust(rev, moment_z_inst, torque_one_sigma_bound, thrust_inst, thrust_one_sigma_bound, out_file_name)
#end

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i','--input',help='Specify the input total forces CSV file or alternatively specify the caseId. For example: <caseId>_total_forces_v2.csv or <caseId>.',type=str,required=True)
    parser.add_argument('-s','--start',help='Starting physical step for post-processing total forces.',type=int,required=False)
    parser.add_argument('-r','--reference',help='Reference values for post-processing total forces.',required=False)
    parser.add_argument('-o','--output',help='Specify the output file name for post-processed forces.',type=str,required=True)
    args = parser.parse_args()
    scriptDir = os.getcwd()

    # speed of sound and density in SI unit for dimensional values
    a_speed = 340.3
    density = 1.225
    L_grid = 1
    # number of past revolutions
    past_revolutions = 10
    starting_physical_step = args.start
    reference_values = args.reference

    get_unsteady_loads(a_speed,density,L_grid,args.input,args.output,reference_values,starting_physical_step,past_revolutions)


if __name__ == '__main__':
    main()