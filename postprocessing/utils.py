import numpy as np
from math import pi, sqrt
import sys, csv, os, tempfile, json
from typing import Tuple, Optional, List, Dict
from collections import defaultdict
import functools

from .version import Flow360Version
from flow360client import case

csv.register_dialect("flow360", delimiter=",", skipinitialspace=True)

def _removePrefix(inputStr, prefix) -> str:
    if inputStr.startswith(prefix):
        return inputStr[len(prefix):]
    else:
        raise RuntimeError(f'{inputStr} does not start with {prefix}')
    return None

def _normalize(vector: np.ndarray) -> np.ndarray:
    return vector/np.linalg.norm(vector)

def _getCaseConfig(caseId) -> Dict:
    caseConfig = None
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpfile = os.path.join(tmpdir, 'flow360.json')
        case.DownloadFile(caseId, 'flow360.json', tmpfile)
        with open(tmpfile) as fh:
            caseConfig = json.load(fh)
    assert caseConfig != None
    return caseConfig

def _readCsvHeader(csvFilePath) -> List[str]:
    header = []
    with open(csvFilePath) as fh:
        header = fh.readline().strip().split(',')
        header = [field.strip() for field in header if len(field.strip()) > 0]
    return header

def _readCsvFile(csvFilePath) -> Dict[str, np.ndarray]:
    fields = _readCsvHeader(csvFilePath)
    nFields = len(fields)
    dataStr = np.loadtxt(csvFilePath, skiprows=1, delimiter=',', dtype=str)
    data = np.ndarray.astype(dataStr.transpose()[0:nFields], dtype=np.float64)
    outputDict = dict()
    for fieldIndex, field in enumerate(fields):
        outputDict[field] = data[fieldIndex]
    return outputDict

def _readResultsCsvFile(caseId, srcName) -> \
        Tuple[Dict[str, np.ndarray], Dict[str, np.ndarray]]:
    result = None
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpCsvFile = os.path.join(tmpdir, 'tmp_results.csv')
        case.DownloadResultsFile(caseId, srcName, tmpCsvFile)
        result = _readCsvFile(tmpCsvFile)
    steps = {'physical_step': result['physical_step'],
             'pseudo_step': result['pseudo_step']}
    del result['physical_step']
    del result['pseudo_step']
    return steps, result

def _calculateLiftDrag(force, alphaDeg, betaDeg):
    assert force.shape[0] == 3
    sina = np.sin(alphaDeg*np.pi/180.)
    cosa = np.cos(alphaDeg*np.pi/180.)
    sinb = np.sin(betaDeg*np.pi/180.)
    cosb = np.cos(betaDeg*np.pi/180.)
    lift = force[2]*cosa - force[0]*sina
    drag = force[0]*cosb*cosa - force[1]*sinb + force[2]*cosb*sina
    return lift, drag

def versionNoNewerThan(newestVersion):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(caseId, **kwargs):
            caseInfo = case.GetCaseInfo(caseId)
            caseSolverVersion = caseInfo['solverVersion']
            if Flow360Version(caseSolverVersion) > Flow360Version(newestVersion):
                raise ValueError(f'The function {func.__name__} does not support version {caseSolverVersion} used by the specified case. The newest version it supports is {newestVersion}')
            value = func(caseId, **kwargs)
            return value
        return wrapper
    return decorator


