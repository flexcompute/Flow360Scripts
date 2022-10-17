import numpy as np
from collections import defaultdict
from math import pi, sqrt
import sys, os, re
from typing import Tuple, Optional, List, Dict
from .utils import _getCaseConfig, _normalize, _readResultsCsvFile,\
        _removePrefix, _calculateLiftDrag, versionNoNewerThan

from flow360client import case
from flow360client.authentication import refreshToken

BET_SEC_LOADING_PATTERN = '^Blade[0-9]+_R[0-9]+_'

class RefQuantity():
    def __init__(self, caseConfig):
        MachRef = None
        if 'MachRef' in caseConfig['freestream']:
            MachRef = caseConfig['freestream']['MachRef']
        else:
            MachRef = caseConfig['freestream']['Mach']
        assert abs(MachRef) > 1.e-15
        alpha = 0
        beta = 0
        if 'alphaAngle' in caseConfig['freestream']:
            alpha = caseConfig['freestream']['alphaAngle']
        elif 'alphaAngleDegrees' in caseConfig['freestream']:
            alpha = caseConfig['freestream']['alphaAngleDegrees']
        if 'betaAngle' in caseConfig['freestream']:
            beta = caseConfig['freestream']['betaAngle']
        elif 'betaAngleDegrees' in caseConfig['freestream']:
            beta = caseConfig['freestream']['betaAngleDegrees']

        self.refArea = caseConfig['geometry']['refArea']
        self.momentLength = np.array(caseConfig['geometry']['momentLength'])
        self.momentCenter = np.array(caseConfig['geometry']['momentCenter'])
        self.MachRef = MachRef
        self.alphaDeg = alpha
        self.betaDeg = beta

def _isBETSecLoading(keyNoDisk) -> bool:
    ret = re.findall(BET_SEC_LOADING_PATTERN, keyNoDisk)
    if len(ret) > 0:
        return True
    return False

def _parseBETSecLoadingKey(keyNoDisk) -> Tuple[int, int, str]:
    firstUnderscore = keyNoDisk.find('_')
    secondUnderscore = keyNoDisk.find('_', firstUnderscore+1)
    bladeIndex = int(keyNoDisk[5:firstUnderscore])
    radialIndex = int(keyNoDisk[firstUnderscore+2:secondUnderscore])
    field = keyNoDisk[secondUnderscore+1:]
    return bladeIndex, radialIndex, field

def _getFormattedBETForces(caseId) -> List[Dict]:
    caseConfig = _getCaseConfig(caseId)
    betForceRaw = None
    steps = None
    if 'BETDisks' in caseConfig and len(caseConfig['BETDisks']) > 0:
        steps, betForceRaw = _readResultsCsvFile(caseId, 'bet_forces_v2.csv')
        assert steps != None
        assert betForceRaw != None
    else:
        return []
    betForceAllDisks = list()
    nBETDisks = len(caseConfig['BETDisks'])
    for diskIndex in range(nBETDisks):
        forceCurr = dict()
        forceCurr.update(steps)
        rawKeys = betForceRaw.keys()
        secLoading = defaultdict(dict)
        for keyRaw, dataRaw in betForceRaw.items():
            keyWithoutDisk = _removePrefix(keyRaw, f'Disk{diskIndex}_')
            if _isBETSecLoading(keyWithoutDisk):
                bladeIndex, radialIndex, field = _parseBETSecLoadingKey(keyWithoutDisk)
                secLoading[f'Blade{bladeIndex}_R{radialIndex}'].update({field:dataRaw.tolist()})
            else:
                forceCurr[keyWithoutDisk] = dataRaw
        forceCurr['SectionalLoading'] = secLoading
        betForceAllDisks.append(forceCurr)
    return betForceAllDisks

@refreshToken
@versionNoNewerThan('release-22.3.3.0')
def GetBETForces(caseId, convertToList = True) -> List[Dict]:
    caseConfig = _getCaseConfig(caseId)
    ref = RefQuantity(caseConfig)
    betForces = _getFormattedBETForces(caseId)
    for diskIndex, betForce in enumerate(betForces):
        betConfig = caseConfig['BETDisks'][diskIndex]
        betCenter = np.array(betConfig['centerOfRotation'])
        nrow = betForce['Force_x'].size
        force = np.stack((betForce['Force_x'], betForce['Force_y'], betForce['Force_z']), axis=1)
        assert force.shape == (nrow, 3)
        momentDiskCenter = np.stack((betForce['Moment_x'], betForce['Moment_y'], betForce['Moment_z']), axis=1)
        globalCenterToDiskCenter = betCenter - ref.momentCenter
        momentGlobalCenter = np.cross(globalCenterToDiskCenter, force) + momentDiskCenter
        qA = 0.5*ref.MachRef**2*ref.refArea
        CForce = force/qA
        CMomentDiskCenter = momentDiskCenter/(qA*ref.momentLength)
        CMomentGlobalCenter = momentGlobalCenter/(qA*ref.momentLength)
        CL, CD = _calculateLiftDrag(CForce.transpose(), ref.alphaDeg, ref.betaDeg)
        betForce['CL'] = CL
        betForce['CD'] = CD
        betForce['CFx'] = CForce.transpose()[0]
        betForce['CFy'] = CForce.transpose()[1]
        betForce['CFz'] = CForce.transpose()[2]
        betForce['CMxDiskCenter'] = CMomentDiskCenter.transpose()[0]
        betForce['CMyDiskCenter'] = CMomentDiskCenter.transpose()[1]
        betForce['CMzDiskCenter'] = CMomentDiskCenter.transpose()[2]
        betForce['CMxGlobalCenter'] = CMomentGlobalCenter.transpose()[0]
        betForce['CMyGlobalCenter'] = CMomentGlobalCenter.transpose()[1]
        betForce['CMzGlobalCenter'] = CMomentGlobalCenter.transpose()[2]
        # CT, CQ
        betConfig = caseConfig['BETDisks'][diskIndex]
        axisOfRotation = _normalize(np.array(betConfig['axisOfRotation']))
        diskRadius = betConfig['radius']
        diskArea = np.pi*diskRadius**2
        diskOmega = betConfig['omega']
        thrust = np.dot(force, axisOfRotation)
        torque = np.dot(momentDiskCenter, axisOfRotation)
        betForce['Thrust'] = thrust
        betForce['Torque'] = torque
        CT = thrust/((diskOmega*diskRadius)**2 * diskArea)
        CQ = torque/((diskOmega*diskRadius)**2 * diskArea * diskRadius)
        betForce['CT'] = CT
        betForce['CQ'] = CQ
        if convertToList:
            for k,v in betForce.items():
                if isinstance(v, np.ndarray):
                    betForce[k] = v.tolist()
    return betForces

def _getFormattedActuatorDiskOutputs(caseId) -> List[Dict]:
    caseConfig = _getCaseConfig(caseId)
    steps = None
    adOutputRaw = None
    if 'actuatorDisks' in caseConfig and len(caseConfig['actuatorDisks'])>0:
        steps, adOutputRaw = _readResultsCsvFile(caseId, 'actuatorDisk_output_v2.csv')
        assert steps != None
        assert adOutputRaw != None
    else:
        return []
    adOutputAllDisks = list()
    nAD = len(caseConfig['actuatorDisks'])
    for diskIndex in range(nAD):
        outputCurr = dict()
        outputCurr.update(steps)
        for keyRaw, dataRaw in adOutputRaw.items():
            keyWithoutDisk = _removePrefix(keyRaw, f'Disk{diskIndex}_')
            outputCurr[keyWithoutDisk] = dataRaw
        adOutputAllDisks.append(outputCurr)
    return adOutputAllDisks

@refreshToken
@versionNoNewerThan('release-22.3.3.0')
def GetActuatorDiskForces(caseId, convertToList=True) -> List[Dict]:
    caseConfig = _getCaseConfig(caseId)
    ref = RefQuantity(caseConfig)
    adForces = _getFormattedActuatorDiskOutputs(caseId)
    for diskIndex, adForce in enumerate(adForces):
        adConfig = caseConfig['actuatorDisks'][diskIndex]
        axisThrust = np.array(_normalize(adConfig['axisThrust']))
        nrow = adForce['Force'].size
        force = np.repeat(adForce['Force'],3).reshape(nrow,3)*axisThrust
        momentDiskCenter = np.repeat(adForce['Moment'],3).reshape(nrow,3)*axisThrust
        assert force.shape == (nrow, 3)
        assert momentDiskCenter.shape == (nrow, 3)
        adCenter = np.array(adConfig['center'])
        globalCenterToDiskCenter = adCenter - ref.momentCenter
        momentGlobalCenter = np.cross(globalCenterToDiskCenter, force) + momentDiskCenter
        qA = 0.5*ref.MachRef**2*ref.refArea
        CForce = force/qA
        CMomentDiskCenter = momentDiskCenter/(qA*ref.momentLength)
        CMomentGlobalCenter = momentGlobalCenter/(qA*ref.momentLength)

        CL, CD = _calculateLiftDrag(CForce.transpose(), ref.alphaDeg, ref.betaDeg)
        adForce['CL'] = CL
        adForce['CD'] = CD
        adForce['CFx'] = CForce.transpose()[0]
        adForce['CFy'] = CForce.transpose()[1]
        adForce['CFz'] = CForce.transpose()[2]
        adForce['CMxDiskCenter'] = CMomentDiskCenter.transpose()[0]
        adForce['CMyDiskCenter'] = CMomentDiskCenter.transpose()[1]
        adForce['CMzDiskCenter'] = CMomentDiskCenter.transpose()[2]
        adForce['CMxGlobalCenter'] = CMomentGlobalCenter.transpose()[0]
        adForce['CMyGlobalCenter'] = CMomentGlobalCenter.transpose()[1]
        adForce['CMzGlobalCenter'] = CMomentGlobalCenter.transpose()[2]
        adForce['Thrust'] = np.array(adForce['Force'])
        adForce['Torque'] = np.array(adForce['Moment'])
        adForce['Power'] = np.array(adForce['Power'])
        del adForce['Force']
        del adForce['Moment']
        if convertToList:
            for k,v in adForce.items():
                adForce[k] = v.tolist()
    return adForces

def _appendForceCoeffInPlace(baseDict: Dict, additionalDict: Dict):
    baseDict['CL']  += additionalDict['CL']
    baseDict['CD']  += additionalDict['CD']
    baseDict['CFx'] += additionalDict['CFx']
    baseDict['CFy'] += additionalDict['CFy']
    baseDict['CFz'] += additionalDict['CFz']
    baseDict['CMxGlobalCenter'] += additionalDict['CMxGlobalCenter']
    baseDict['CMyGlobalCenter'] += additionalDict['CMyGlobalCenter']
    baseDict['CMzGlobalCenter'] += additionalDict['CMzGlobalCenter']

@refreshToken
@versionNoNewerThan('release-22.3.3.0')
def GetTotalForceCoefficients(caseId) -> Dict[str, List]:
    caseConfig = _getCaseConfig(caseId)
    ref = RefQuantity(caseConfig)

    CFWalls = case.GetCaseTotalForces(caseId)

    CFBetDisks = GetBETForces(caseId, convertToList=False)

    CFActuatorDisks = GetActuatorDiskForces(caseId, convertToList=False)

    totalForceCoeff = dict()
    totalForceCoeff['physical_step'] = np.array(CFWalls['physical_step'])
    totalForceCoeff['pseudo_step']   = np.array(CFWalls['pseudo_step'])
    totalForceCoeff['CL']  = np.array(CFWalls['CL'])
    totalForceCoeff['CD']  = np.array(CFWalls['CD'])
    totalForceCoeff['CFx'] = np.array(CFWalls['CFx'])
    totalForceCoeff['CFy'] = np.array(CFWalls['CFy'])
    totalForceCoeff['CFz'] = np.array(CFWalls['CFz'])
    totalForceCoeff['CMxGlobalCenter'] = np.array(CFWalls['CMx'])
    totalForceCoeff['CMyGlobalCenter'] = np.array(CFWalls['CMy'])
    totalForceCoeff['CMzGlobalCenter'] = np.array(CFWalls['CMz'])

    for CFBetDisk in CFBetDisks:
        _appendForceCoeffInPlace(totalForceCoeff, CFBetDisk)
    for CFActuatorDisk in CFActuatorDisks:
        _appendForceCoeffInPlace(totalForceCoeff, CFActuatorDisk)

    for k,v in totalForceCoeff.items():
        totalForceCoeff[k] = v.tolist()

    return totalForceCoeff
