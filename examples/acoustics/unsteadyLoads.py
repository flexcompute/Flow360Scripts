
import os, tempfile
import argparse

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import matplotlib.ticker as ticker

import flow360client

def separator(n=20):
    return "-"*n

def getCaseConfigParameters(caseId):
    return flow360client.case.GetCaseInfo(caseId)['runtimeParams']

def getTotalForcesPerPhysicalSteps(caseId,startingStep):
    total_forces_data = flow360client.case.GetCaseTotalForces(caseId)
    steps = total_forces_data['physical_step']
    cl = total_forces_data['CL']
    cd = total_forces_data['CD']
    cfz = total_forces_data['CFz']
    cm = total_forces_data['CMz']
    
    # finds the starting line after the starting step
    for i in range(len(steps)):
        if steps[i] == startingStep:
            initialLine = i+1

    # crates array for coefficient after the starting step
    steps = np.array(steps[initialLine:None])
    cl = np.array(cl[initialLine:None])
    cd = np.array(cd[initialLine:None])
    cfz = np.array(cfz[initialLine:None])
    cm = np.array(cm[initialLine:None])
    
    currentRowStep = steps[0]
    lastRowStep = steps[-1]
    print('Starting physical step: {}'.format(currentRowStep))
    print('Ending physical step: {}'.format(lastRowStep))

    i = 0
    steps_inst=[]
    cl_inst = []
    cd_inst = []
    cfz_inst = []
    cm_inst = []
    
    # taking last values at end of each physical step
    while currentRowStep != lastRowStep:
        if currentRowStep != steps[i+1]:
            steps_inst.append(steps[i])
            cl_inst.append(cl[i])
            cd_inst.append(cd[i])
            cfz_inst.append(cfz[i])
            cm_inst.append(cm[i])
        i+=1
        currentRowStep= int(steps[i])
    
    # adding the last values at end of the last physical step
    steps_inst.append(steps[-1])
    cl_inst.append(cl[-1])
    cd_inst.append(cd[-1])
    cfz_inst.append(cfz[-1])
    cm_inst.append(cm[-1])

    # returning coefficients converged at each physical step
    return [np.array(steps_inst),np.array(cl_inst),np.array(cd_inst),np.array(cfz_inst),np.array(cm_inst)]

def getRefParameters(caseConfig):
    refArea = caseConfig['geometry']['refArea']
    momentLength = np.array(caseConfig['geometry']['momentLength'])

    MachRef = caseConfig['freestream']['MachRef']
    assert abs(MachRef) > 1.e-15
    alpha = caseConfig['freestream']['alphaAngle']
    beta = caseConfig['freestream']['betaAngle']
    omega = caseConfig['slidingInterfaces'][0]['omega']
    timeStep = caseConfig['timeStepping']['timeStepSize']
    return [refArea,momentLength,MachRef,alpha,beta,omega,timeStep]

def plot_torque_thrust_coefficients(rev,CQ,CT,oName):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    lns1 = ax.plot(rev,CQ, '-b', label='$C_{Q}$', linewidth=0.6)
    ax2=ax.twinx()
    lns2 = ax2.plot(rev,CT, '-r', label='$C_{T}$', linewidth=0.6)
    lns = lns1+lns2
    labs = [l.get_label() for l in lns]
    ax.legend(lns, labs, loc =0, frameon=False)

    plt.title("Torque and Thrust Coefficients", fontsize=12)
    ax.set_xlabel('Revolutions', fontsize=10)
    ax.set_ylabel('$C_{Q}$', fontsize=10)
    ax2.set_ylabel('$C_{T}$', fontsize=10)
    ax2.set_yticks(np.arange(0.0075,0.0125,0.001))
    plt.savefig(f'{oName}_ctcq_coef.png', bbox_inches='tight', dpi=600)
    plt.close()
#end

def plot_torque_thrust(rev,moment,thrust,oName):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    lns1 = ax.plot(rev,moment, '-b', label='$Torque$', linewidth=0.6)
    ax2=ax.twinx()
    lns2 = ax2.plot(rev,thrust, '-r', label='$Thrust$', linewidth=0.6)
    lns = lns1+lns2
    labs = [l.get_label() for l in lns]
    ax.legend(lns, labs, loc =0, frameon=False)

    plt.title("Torque and Thrust", fontsize=12)
    ax.set_xlabel('Revolutions', fontsize=10)
    ax.set_ylabel('Torque (N.m)', fontsize=10)
    ax2.set_ylabel('Thrust (N)', fontsize=10)
    ax2.set_yticks(np.arange(2,4.5,0.5))
    plt.savefig(f'{oName}_torque_thrust.png', bbox_inches='tight', dpi=600)
    plt.close()
#end

def plot_Cfz_moment_coeffcients(rev,CFz,CM,oName):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    lns1 = ax.plot(rev,CM, '-b', label='$C_{M}$', linewidth=0.6)
    ax2=ax.twinx()
    lns2 = ax2.plot(rev,CFz, '-r', label='$C_{Fz}$', linewidth=0.6)
    lns = lns1+lns2
    labs = [l.get_label() for l in lns]
    ax.legend(lns, labs, loc =0, frameon=False)

    plt.title("Force Coefficients", fontsize=12)
    ax.set_xlabel('Revolutions', fontsize=10)
    ax.set_ylabel('$C_{M}$', fontsize=10)
    ax2.set_ylabel('$C_{Fz}$', fontsize=10)
    ax2.set_yticks(np.arange(0.02,0.03,0.001))
    plt.savefig(f'{oName}_cfzcm_coef.png', bbox_inches='tight', dpi=600)
    plt.close()
#end

def getUnsteadyLoads(aSound,rho,Lgrid,caseId,oName,start = 0, pRev = 0):
    print('For CaseID: {}'.format(caseId))
    print(separator(50))

    # fetching case parameters
    caseConfig = getCaseConfigParameters(caseId)
    # fetching reference parameters
    ref = getRefParameters(caseConfig)
    # assigning reference parameters including:
    # non dimensional omega in rad/s
    omega = ref[5]
    # dimensional rpm for check
    rpm = omega*(60/(2*np.pi))*(aSound/Lgrid)
    # reference area
    area_ref = ref[0]
    # radius based on reference area
    radius = np.sqrt(area_ref/np.pi)
    # reference mach no
    mach_ref = ref[2]
    # reference moment in z direction
    moment_z_ref = ref[1][2]
    # reference velocity based on mach ref
    velocity_ref = mach_ref*aSound
    # number of physical steps per one revolution
    steps_per_revolution = np.floor((2*np.pi/omega)/ref[6])
    # 
    vars = getTotalForcesPerPhysicalSteps(caseId,start)
    print(separator(50))
    # revolution progress
    rev = [((i-start)/steps_per_revolution)+pRev for i in vars[0]]

    # coefficients
    CL,CD,CFz,CM = vars[1:]

    # average of coefficients
    averagedCL = np.mean(CL)
    averagedCD = np.mean(CD)
    averagedCFz = np.mean(CFz)
    averagedCM = np.mean(CM)

    # rms values based on root mean square of instantaneous values
    RMScl = np.sqrt(np.mean(CL**2))
    RMScd = np.sqrt(np.mean(CD**2))
    RMScfz = np.sqrt(np.mean(CFz**2))
    RMScm = np.sqrt(np.mean(CM**2))

    # +/- values
    varCL = np.mean([abs(averagedCL - np.min(CL)), np.max(CL) - averagedCL])
    varCD = np.mean([abs(averagedCD - np.min(CD)), np.max(CD) - averagedCD])
    varCFz = np.mean([abs(averagedCFz - np.min(CFz)), np.max(CFz) - averagedCFz])
    varCM = np.mean([abs(averagedCM - np.min(CM)), np.max(CM) - averagedCM])

    # non dimensional rotational speed in rad/s
    # lift force based on RMScl
    lift_force = 0.5 * RMScl * rho * (velocity_ref**2) * area_ref
    # instantaneous lift
    lift = 0.5 * CL * rho * (velocity_ref**2) * area_ref
    # drag force
    drag_force = 0.5 * RMScd * rho * (velocity_ref**2) * area_ref
    # instantaneous drag
    drag = 0.5 * CD * rho * (velocity_ref**2) * area_ref
    # force based cfz
    Z_force = 0.5 * RMScfz * rho * (velocity_ref**2) * area_ref
    # instantaneous drag
    zforce = 0.5 * CFz * rho * (velocity_ref**2) * area_ref
    # moment z
    moment_z = 0.5 * RMScm * rho * (velocity_ref**2) * area_ref * moment_z_ref
    # instantaneous moment
    moment = 0.5 * CM * rho * (velocity_ref**2) * area_ref * moment_z_ref

    # thrust is in z direction
    thrust_force = Z_force
    # instantaneous thrust
    thrust = lift
    
    # non-dimensional thrust
    non_dim_thrust = thrust / (rho * (aSound**2) * (Lgrid**2))
    # non-dimensional moment
    non_dim_moment = moment / (rho * (aSound**2) * (Lgrid**3))
    # instantaneous thrust coefficient
    CT = non_dim_thrust / (rho * area_ref * ((omega*radius)**2))
    # instantaneous torque coefficient
    CQ = non_dim_moment / (rho * ((omega * radius)**2) * area_ref * radius)
    
    # rms of thrust and torque coefficients
    RMSct = np.sqrt(np.mean(CT**2))
    RMScq = np.sqrt(np.mean(CQ**2))
    # averaged value of thrust and torque
    averagedCT = np.mean(CT)
    averagedCQ = np.mean(CQ)
    # +/- values for thrust and torque coefficients
    varCT = np.mean([abs(averagedCT - np.min(CT)), np.max(CT) - averagedCT])
    varCQ = np.mean([abs(averagedCQ - np.min(CQ)), np.max(CQ) - averagedCQ])

    # report
    print("CL = %.6f" % (averagedCL) + " +/- %.6f" % (varCL))
    print("RSM CL = %.6f" % (RMScl))
    print(separator(40))
    print("CD = %.6f" % (averagedCD) + " +/- %.6f" % (varCD))
    print("RSM CD = %.6f" % (RMScd))
    print(separator(40))
    print("CFz = %.6f" % (averagedCFz) + " +/- %.6f" % (varCFz))
    print("RSM CFz = %.6f" % (RMScfz))
    print(separator(40))
    print("CM = %.6f" % (averagedCM) + " +/- %.6f" % (varCM))
    print("RSM CM = %.6f" % (RMScm))
    print(separator(40))
    print("CT = %.6f" % (averagedCT) + " +/- %.6f" % (varCT))
    print("RSM CT = %.6f" % (RMSct))
    print(separator(40))
    print("CQ = %.6f" % (averagedCQ) + " +/- %.6f" % (varCQ))
    print("RSM CQ = %.6f" % (RMScq))
    print(separator(40))

    # figure of merit
    fom = (abs(averagedCT)**(3/2))/(np.sqrt(2)*abs(averagedCQ))

    print("Thrust (N) = %.4f" % (thrust_force))
    print("Torque (N.m) = %.4f" % (moment_z))
    print("FoM = %.4f" % (fom))

    # output file basename
    outFileName = os.path.splitext(os.path.basename(oName))[0]
    # output file in dat format
    forceFile = os.path.join(os.curdir,outFileName+'_thrust_torque'+'.dat')
    print("variables=cl,cd,cfz,cmz,ct,cq,fom,thrust,torque",file=open(forceFile, 'w'))
    print("{0},  {1},  {2},  {3},  {4},  {5},  {6},  {7}".format(RMScl,RMScd,RMScfz,RMScm,RMSct,RMScq,fom,thrust_force,moment_z),file=open(forceFile, 'a'))

    plot_torque_thrust_coefficients(rev,CQ,CT,outFileName)
    plot_torque_thrust(rev,moment,thrust,outFileName)
    plot_Cfz_moment_coeffcients(rev,CFz,CM,outFileName)
#end

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-caseId',type=str,required=True)
    parser.add_argument('-start',type=int,required=True)
    parser.add_argument('-o',type=str,required=True)
    args = parser.parse_args()
    scriptDir = os.getcwd()

    # speed of sound and density in SI for dimensional values
    a_speed = 340.3
    density = 1.225
    Lgrid = 1
    past_revolutions = 10
    starting_physicalStep = args.start

    getUnsteadyLoads(a_speed,density,Lgrid,args.caseId,args.o,starting_physicalStep,past_revolutions)


if __name__ == '__main__':
    main()