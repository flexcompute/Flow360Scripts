"""
This Module is meant to be imported into scripts that translate the required information into a Flow360 input JSON file
with BET disk(s).

Explain XROTOR, DFDC, C81, Xfoil.

EXAMPLE useage:

EXAMPLE codes

"""
# import sys
# import os

from math import *
from numpy import arange, array, clip, exp, log
import json


########################################################################################################################
def check_comment(comment_line, numelts):
    """
    This function is used when reading an XROTOR input file to make sure that what should be comments really are
    :param comment_line: string
    :param numelts: int
    """
    if not comment_line: # if the comment_line is empty.
        return

    # otherwise make sure that we are on a comment line
    if not comment_line[0] == '!' and not (len(comment_line) == numelts):
        raise ValueError(f'wrong format for line: {comment_line}')


########################################################################################################################
def check_num_values(values_list, numelts):
    """
    This function is used to make sure we have the expecteed number of inputs in a given line
    :param values: list
    :param numelts:  int
    :return:
    """
    # make sure that we have the expected number of values.
    if not (len(values_list) == numelts):
        print('wrong number of items for line:', values_list)
        raise ValueError(f'wrong number of items for line: {values_list}')

########################################################################################################################
def readDFDCFile(dfdcFileName):
    """
    This functions read in the dfdc filename provided.
    it does rudimentary checks to make sure the file is truly in the dfdc format.
    :param dfdcFileName: string
    :return: a dictionary with all the required values. That dictionary will be used to create BETdisks section of the
            Flow360 input JSON file.

    dfdcInputDict has the following format:
    Case run definition:
    rho :air density (dimensional: kg/m3)
    vso aka cinf : speed of sound ( dimensional: m/s)
        !   RMU         Fluid dynamic viscosity  (dimensioned)
        !   VSO         Fluid speed of sound     (dimensioned)
        !   VEL         Flight speed             (dimensioned)
    rmu: Fluid dynamic viscosity  (dimensional (kg/ms) standard air:1.789E-05)
    Alt: Altitude for fluid properties (km),  999.0 if not defined
    Vel: flight speed dimensional (m/s)
    xi0:Blade root radial coordinate value (dimensional (m))
    xiw: hub wake displacement radius (unused)
    nAeroSections aka naero: number of AERO sections the blade is defined by, NOT TO BE CONFUSED WITH nGeomStations (AKA II) WHICH DEFINE THE BLADE GEOMETRY
    dfdcInputDict stores all the blade sectional information as lists of nsection elements
    rRsection: r/R location of this blade section
    Aerodynamic definition of the blade section at xiaero
        a0deg: angle of zero lift in degrees
        dclda: Incompressible 2-d lift curve slope in radians
        clmax: Max cl after which we use the post stall dc/dalfa (aka dclda_stall)
        clmin: Min cl before which we use the negative alpha stall dc/dalfa (aka dclda_stall)

        dclda_stall: 2-d lift curve slope at stall
        dcl_stall: cl increment, onset to full stall
        cmconst: constant Incompressible 2-d pitching moment
        mcrit: critical Mach #
        cdmin: Minimum drag coefficient value
        cldmin: Lift at minimum drag coefficient value
        dcddcl2: Parabolic drag param d(Cd)/dcl^2
        reyref: reference Reynold's number
        reyexp: Reynold's number exponent Cd~Re^rexp

    nGeomStations: number of geometric stations where the blade geometry is defined at
    nBlades: number of blades on the propeller
    Each geometry station will have the following parameters:
      r/R: station r/R
      c/R: local chord divided by radius
      beta0deg: Twist relative to disk plane. ie symmetric 2D section at beta0Deg would create 0 thrust, more beta0deg means more local angle of attack for the blade
      Ubody: (unused) Nacelle perturbation axial  velocity


    """
    fid = open(dfdcFileName, 'r')

    # read in lines 5->8 which contains the run case information
    dfdcInputDict = {}
    for i in range (4): fid.readline()  # we have 4 blank lines

    comment_line = fid.readline().upper().split()
    check_comment(comment_line, 5)
    values = fid.readline().split()
    check_num_values(values, 4)

    dfdcInputDict['vel'] = float(values[1])
    dfdcInputDict['RPM'] = float(values[2])

    comment_line = fid.readline().upper().split()
    check_comment(comment_line, 5)
    values = fid.readline().split()
    check_num_values(values, 4)
    dfdcInputDict['rho'] = float(values[0])
    dfdcInputDict['vso'] = float(values[1])

    for i in range(7):
        fid.readline()  # skip next 8 lines.

    comment_line = fid.readline().upper().split()  # convert all to upper case
    check_comment(comment_line, 2)  # 2 because line should have 2 components
    values = fid.readline().split()
    check_num_values(values, 1)  # we should have 1 value.
    dfdcInputDict['nAeroSections'] = int(values[0])
    # define the lists with the right number of elements
    dfdcInputDict['rRstations'] = [0] * dfdcInputDict['nAeroSections']
    dfdcInputDict['a0deg'] = [0] * dfdcInputDict['nAeroSections']  # WARNING, ao is in deg
    dfdcInputDict['dclda'] = [0] * dfdcInputDict['nAeroSections']  # but dclda is in cl per radians
    dfdcInputDict['clmax'] = [0] * dfdcInputDict['nAeroSections']
    dfdcInputDict['clmin'] = [0] * dfdcInputDict['nAeroSections']
    dfdcInputDict['dcldastall'] = [0] * dfdcInputDict['nAeroSections']
    dfdcInputDict['dclstall'] = [0] * dfdcInputDict['nAeroSections']
    dfdcInputDict['mcrit'] = [0] * dfdcInputDict['nAeroSections']
    dfdcInputDict['cdmin'] = [0] * dfdcInputDict['nAeroSections']
    dfdcInputDict['clcdmin'] = [0] * dfdcInputDict['nAeroSections']
    dfdcInputDict['dcddcl2'] = [0] * dfdcInputDict['nAeroSections']

    comment_line = fid.readline().upper().split()  # convert all to upper case
    check_comment(comment_line, 2)  # 2 because line should have 2 components
    for i in range(dfdcInputDict['nAeroSections']):  # iterate over all the sections

        values = fid.readline().split()
        check_num_values(values, 1)  # we should have 1 value.
        dfdcInputDict['rRstations'][i] = float(values[0])  # aka xisection

        comment_line = fid.readline().upper().split()  # convert all to upper case
        check_comment(comment_line, 5)  # 5 because line should have 5 components
        values = fid.readline().split()
        check_num_values(values, 4)  # we should have 4 value.
        dfdcInputDict['a0deg'][i] = float(values[0])  # WARNING, ao is in deg
        dfdcInputDict['dclda'][i] = float(values[1])  # but dclda is in cl per radians
        dfdcInputDict['clmax'][i] = float(values[2])
        dfdcInputDict['clmin'][i] = float(values[3])

        comment_line = fid.readline().upper().split()  # convert all to upper case
        check_comment(comment_line, 5)  # 5 because line should have 5 components
        values = fid.readline().split()
        check_num_values(values, 4)  # we should have 4 value.
        dfdcInputDict['dcldastall'][i] = float(values[0])
        dfdcInputDict['dclstall'][i] = float(values[1])
        dfdcInputDict['mcrit'][i] = float(values[3])

        comment_line = fid.readline().upper().split()  # convert all to upper case
        check_comment(comment_line, 4)  # 4 because line should have 4 components
        values = fid.readline().split()
        check_num_values(values, 3)  # we should have 3 value.
        dfdcInputDict['cdmin'][i] = float(values[0])
        dfdcInputDict['clcdmin'][i] = float(values[1])
        dfdcInputDict['dcddcl2'][i] = float(values[2])

        for i in range(2):
            fid.readline()  # skip next 3 lines.

    for i in range(3):
        fid.readline()  # skip next 3 lines.

    # Now we are done with the various aero sections and we start looking at blade geometry definitions
    comment_line = fid.readline().upper().split()  # convert all to upper case
    check_comment(comment_line, 3)  # 3 because line should have 3 components
    values = fid.readline().split()
    check_num_values(values, 3)  # we should have 3 values.
    dfdcInputDict['rad'] = float(values[0])
    dfdcInputDict['nBlades'] = int(values[1])
    comment_line = fid.readline().upper().split()  # convert all to upper case
    check_comment(comment_line, 2)
    values = fid.readline().split()
    check_num_values(values, 1)
    dfdcInputDict['nGeomStations'] = int(values[0])
    # 2nd value on that  line is the number of blades
    dfdcInputDict['rRGeom'] = [0] * dfdcInputDict['nGeomStations']
    dfdcInputDict['cRGeom'] = [0] * dfdcInputDict['nGeomStations']
    dfdcInputDict['beta0Deg'] = [0] * dfdcInputDict['nGeomStations']
    comment_line = fid.readline().upper().split()  # convert all to upper case
    check_comment(comment_line, 4)  # 4 because line should have 4 components
    for i in range(dfdcInputDict['nGeomStations']):  # iterate over all the geometry stations
        values = fid.readline().split()
        check_num_values(values, 3)  # we should have 3 values.
        dfdcInputDict['rRGeom'][i] = float(values[0])  # not quite true b/c we need to multiply by radius but I need a place to store the r locations
        dfdcInputDict['cRGeom'][i] = float(values[1])  # not quite true b/c we need to multiply by radius but I need a place to store the chord dimensions
        dfdcInputDict['beta0Deg'][i] = float(values[2])  # twist values
    if dfdcInputDict['rRGeom'][0] != 0:  # As per discussion in
        # https://enreal.slack.com/archives/C01PFAJ76FL/p1643652853237749?thread_ts=1643413462.002919&cid=C01PFAJ76FL
        # i need to ensure that the blade coordinates go all the way to r/R=0 and have a 0 chord  90deg twist at r/R=0
        dfdcInputDict['rRGeom'].insert(0, 0.0)
        dfdcInputDict['cRGeom'].insert(0, 0.0)
        dfdcInputDict['beta0Deg'].insert(0, 90.0)
        dfdcInputDict['nGeomStations'] += 1  # we have added one station.


    # for i in range(dfdcInputDict['nGeomStations']):  # iterate over all the geometry stations to nondimensionalize by radius.
    #     dfdcInputDict['rRGeom'][i] = dfdcInputDict['rRGeom'][i] * dfdcInputDict['rad']  # aka r/R location
    #     dfdcInputDict['cRGeom'][i] = dfdcInputDict['cRGeom'][i] * dfdcInputDict['rad']  # aka r/R location

    # calculate Extra values and add them  to the dict
    dfdcInputDict['omegaDim'] = dfdcInputDict['RPM'] * pi / 30

    # Now we are done, we have all the data we need.
    return dfdcInputDict


########################################################################################################################

########################################################################################################################
def readXROTORFile(xrotorFileName):
    """
    This functions read in the Xrotor filename provided.
    it does rudimentary checks to make sure the file is truly in the Xrotor format.
    :param xrotorFileName: string
    :return: a dictionary with all the required values. That dictionary will be used to create BETdisks section of the
            Flow360 input JSON file.


    xrotor Input file has the following definitions:
    Case run definition:
    rho :air density (dimensional: kg/m3)
    vso aka cinf : speed of sound ( dimensional: m/s)
        !   RMU         Fluid dynamic viscosity  (dimensioned)
        !   VSO         Fluid speed of sound     (dimensioned)
        !   VEL         Flight speed             (dimensioned)
        !   RAD         Rotor tip radius         (dimensioned)
    rmu: Fluid dynamic viscosity  (dimensional (kg/ms) standard air:1.789E-05)
    Alt: Altitude for fluid properties (km),  999.0 if not defined
    Rad: rotor Tip radius dimensional (m)
    Vel: flight speed dimensional (m/s)
    Adv: Advance ratio (Vel/Vtip) where Vtip = propeller tip speed
    Rake: unused- Winglet/droop type tips. We assume a planar propeller.
    xi0:Blade root radial coordinate value (dimensional (m))
    xiw: hub wake displacement radius (unused)
    nAeroSections aka naero: number of AERO sections the blade is defined by, NOT TO BE CONFUSED WITH nGeomStations (AKA II) WHICH DEFINE THE BLADE GEOMETRY
    xrotorInputDict stores all the blade sectional information as lists of nsection elements
    rRsection: r/R location of this blade section
    Aerodynamic definition of the blade section at xiaero
        a0deg: angle of zero lift in degrees
        dclda: Incompressible 2-d lift curve slope in radians
        clmax: Max cl after which we use the post stall dc/dalfa (aka dclda_stall)
        clmin: Min cl before which we use the negative alpha stall dc/dalfa (aka dclda_stall)

        dclda_stall: 2-d lift curve slope at stall
        dcl_stall: cl increment, onset to full stall
        cmconst: constant Incompressible 2-d pitching moment
        mcrit: critical Mach #
        cdmin: Minimum drag coefficient value
        cldmin: Lift at minimum drag coefficient value
        dcddcl2: Parabolic drag param d(Cd)/dcl^2
        reyref: reference Reynold's number
        reyexp: Reynold's number exponent Cd~Re^rexp

    nGeomStations: number of geometric stations where the blade geometry is defined at
    nBlades: number of blades on the propeller
    Each geometry station will have the following parameters:
      r/R: station r/R
      c/R: local chord divided by radius
      beta0deg: Twist relative to disk plane. ie symmetric 2D section at beta0Deg would create 0 thrust, more beta0deg means more local angle of attack for the blade
      Ubody: (unused) Nacelle perturbation axial  velocity

    """

    try:
        fid = open(xrotorFileName, 'r')

        # Top line in the file should start with the XROTOR keywords.
        topLine=fid.readline()
        if topLine.find('DFDC') == 0:  # If we are actually doing a DFDC file instead of Xrotor
            fid.close()  # close the file b/c we will reopen it in readDFDCFile
            return readDFDCFile(xrotorFileName)

        elif topLine.find('XROTOR') == -1:
            raise ValueError(f'This input Xrotor file does not seem to be a valid Xrotor input file')

        # read in lines 2->8 which contains the run case information
        xrotorInputDict = {}
        fid.readline()
        comment_line = fid.readline().upper().split()
        check_comment(comment_line, 5)

        values = fid.readline().split()
        check_num_values(values, 4)

        xrotorInputDict['vso'] = float(values[1])

        comment_line = fid.readline().upper().split()
        check_comment(comment_line, 5)
        values = fid.readline().split()
        check_num_values(values, 4)
        xrotorInputDict['rad'] = float(values[0])
        xrotorInputDict['vel'] = float(values[1])
        xrotorInputDict['adv'] = float(values[2])

        fid.readline()
        fid.readline()
        comment_line = fid.readline().upper().split()
        check_comment(comment_line, 2)
        values = fid.readline().split()
        check_num_values(values, 1)

        nAeroSections = int(values[0])
        # Initialize the dictionary with all the information to re-create the polars at each defining aero section.
        xrotorInputDict['nAeroSections'] = nAeroSections
        xrotorInputDict['rRstations'] = [0] * nAeroSections
        xrotorInputDict['a0deg'] = [0] * nAeroSections
        xrotorInputDict['dclda'] = [0] * nAeroSections
        xrotorInputDict['clmax'] = [0] * nAeroSections
        xrotorInputDict['clmin'] = [0] * nAeroSections
        xrotorInputDict['dcldastall'] = [0] * nAeroSections
        xrotorInputDict['dclstall'] = [0] * nAeroSections
        xrotorInputDict['mcrit'] = [0] * nAeroSections
        xrotorInputDict['cdmin'] = [0] * nAeroSections
        xrotorInputDict['clcdmin'] = [0] * nAeroSections
        xrotorInputDict['dcddcl2'] = [0] * nAeroSections

        for i in range(nAeroSections):  # loop ever each aero section and populate the required variables.
            comment_line = fid.readline().upper().split()
            check_comment(comment_line, 2)
            values = fid.readline().split()
            check_num_values(values, 1)
            xrotorInputDict['rRstations'][i] = float(values[0])

            comment_line = fid.readline().upper().split()
            check_comment(comment_line, 5)
            values = fid.readline().split()
            check_num_values(values, 4)
            xrotorInputDict['a0deg'][i] = float(values[0])
            xrotorInputDict['dclda'][i] = float(values[1])
            xrotorInputDict['clmax'][i] = float(values[2])
            xrotorInputDict['clmin'][i] = float(values[3])

            comment_line = fid.readline().upper().split()
            check_comment(comment_line, 5)
            values = fid.readline().split()
            check_num_values(values, 4)
            xrotorInputDict['dcldastall'][i] = float(values[0])
            xrotorInputDict['dclstall'][i] = float(values[1])
            xrotorInputDict['mcrit'][i] = float(values[3])

            comment_line = fid.readline().upper().split()
            check_comment(comment_line, 4)
            values = fid.readline().split()
            check_num_values(values, 3)
            xrotorInputDict['cdmin'][i] = float(values[0])
            xrotorInputDict['clcdmin'][i] = float(values[1])
            xrotorInputDict['dcddcl2'][i] = float(values[2])

            comment_line = fid.readline().upper().split()
            check_comment(comment_line, 3)
            values = fid.readline().split()

        # skip the duct information
        fid.readline()
        fid.readline()

        # Now we are done with the various aero sections and we start
        # looking at blade geometry definitions
        comment_line = fid.readline().upper().split()
        check_comment(comment_line, 3)
        values = fid.readline().split()
        check_num_values(values, 2)

        nGeomStations = int(values[0])
        xrotorInputDict['nGeomStations'] = nGeomStations
        xrotorInputDict['nBlades'] = int(values[1])
        xrotorInputDict['rRGeom'] = [0] * nGeomStations
        xrotorInputDict['cRGeom'] = [0] * nGeomStations
        xrotorInputDict['beta0Deg'] = [0] * nGeomStations

        comment_line = fid.readline().upper().split()
        check_comment(comment_line, 5)

        # iterate over all the geometry stations
        for i in range(nGeomStations):

            values = fid.readline().split()
            check_num_values(values, 4)
            xrotorInputDict['rRGeom'][i] = float(values[0])
            xrotorInputDict['cRGeom'][i] = float(values[1])
            xrotorInputDict['beta0Deg'][i] = float(values[2])

    finally: # We are done reading
        fid.close()

    # Set the twist at the root to be 90 so that it is continuous on
    # either side of the origin. I.e Across blades' root. Also set
    # the chord to be 0 at the root
    if xrotorInputDict['rRGeom'][0] != 0:
        xrotorInputDict['rRGeom'].insert(0, 0.0)
        xrotorInputDict['cRGeom'].insert(0, 0.0)
        xrotorInputDict['beta0Deg'].insert(0, 90.0)
        xrotorInputDict['nGeomStations'] += 1

    # AdvanceRatio = Vinf/Vtip => Vinf/OmegaR
    xrotorInputDict['omegaDim'] = \
        xrotorInputDict['vel'] / (xrotorInputDict['adv'] * xrotorInputDict['rad'])
    xrotorInputDict['RPM'] = xrotorInputDict['omegaDim'] * 30 / pi

    return xrotorInputDict


########################################################################################################################
def generateTwists(xrotorDict, gridUnit):
    """
    Transform the Xrotor format blade twists distribution into the Flow360 standard.

    :param xrotorDict: dictionary of Xrotor data as read in by def readXROTORFile(xrotorFileName):
    :param gridUnit: float,  Grid unit length in the mesh.
    :return:  list of dictionaries containing the radius ( in grid units) and twist in degrees.
    """
    # generate the twists vector required from the BET input
    twistVec = []
    for i in range(xrotorDict['nGeomStations']):
        # dimensional radius we are at in grid unit
        r = xrotorDict['rRGeom'][i] * xrotorDict['rad'] / gridUnit
        twist = xrotorDict['beta0Deg'][i]
        twistVec.append({'radius': r, 'twist': twist})

    return twistVec


########################################################################################################################
def generateChords(xrotorDict, gridUnit):
    """
    Transform the Xrotor format blade chords distribution into the Flow360 standard.

    :param xrotorDict: dictionary of Xrotor data as read in by def readXROTORFile(xrotorFileName):
    :param gridUnit: float,  Grid unit length in the mesh.
    :return:  list of dictionaries containing the radius ( in grid units) and chords in grid units.
    """
    # generate the dimensional chord vector required from the BET input
    chordVec = []
    for i in range(xrotorDict['nGeomStations']):
        r = xrotorDict['rRGeom'][i] * xrotorDict['rad'] / gridUnit
        chord = xrotorDict['cRGeom'][i] * xrotorDict['rad'] / gridUnit
        chordVec.append({'radius': r, 'chord': chord})

    return chordVec


########################################################################################################################
def generateMachs():
    """
    The Flow360 BET input file expects a set of Mach numbers to interpolate
    between using the Mach number the blade sees.
    To that end we will generate 4 different tables at 4 different Mach #s
    equivalent to M^2=0, 1/3, 2/3, 0.9

    :return: list of floats
    """

    machVec = [0, sqrt(1 / 3), sqrt(2 / 3), sqrt(0.9)]
    return machVec


########################################################################################################################
def generateReys():
    """
    Flow360 has the functionality to interpolate across Reynolds numbers but we are not using that functionality
    just make it a constant 1
    :return:
    """
    return [1]


########################################################################################################################
def generateAlphas():
    """
    Generate the list of Alphas that the BET 2d section polar is for in 1 degree steps from -180 to 180
    :return: list of floats
    """
    # generate the list of Alphas that the 2d section polar is for:

    # option 1:
    # 10 deg steps from -180 ->-30 and from 30 to 180. 1 deg steps from -29 to 29
    # negAng = list(arange(-30, -5, 1).astype(float))
    # posAng = list(arange(-5, 10, 1).astype(float))
    # posAng2 = list(arange(10, 29, 1).astype(float))
    # return list(arange(-180, -30, 10).astype(float)) + negAng + posAng + posAng2 + list(arange(30, 190, 10).astype(float))  # json doesn't like the numpy default int64 type so I make it a float

    # option 2: return every degree
    return list(arange(-180, 181, 1).astype(float))


########################################################################################################################
def findClMinMaxAlphas(CLIFT, CLMIN, CLMAX):
    """
    Find the index in the CLIFT list where we are just below the CLMin
    value and the one where we are just above the CLmax value. Use the fact that CL should be continually increasing
    from -pi -> Pi radians.
    The goal of this function is to separate the linear CL regime (i.e. from CLmin to CLmax) and extract its indices
    We Traverse the list from the beginning until we hit CLMIN


    Attributes
    ----------

    CLIFT: list of floats
    CLMIN: float
    CLMAX: float
    return: 2 ints as indices
    """

    clMinIdx = 0  # initialize as the first index
    clMaxIdx = len(CLIFT)  # initialize as the last index
    for i in range(len(CLIFT)):
        if CLIFT[i] < CLMIN:
            clMinIdx = i
        if CLIFT[i] > CLMAX:
            clMaxIdx = i
            break
    return clMinIdx - 1, clMaxIdx + 1  # return the two indices right before and after the two found values.


########################################################################################################################
def blendFuncValue(blendWindow, alpha, alphaMinMax, alphaRange):
    """
    This functions is used to blend the flat plate CL and CD polar to the given Cl and CD polars.
    The returned blend value is 1 when we use the given CL and CD values and 0 when we use the Flat plate values.
    Within the blendWindow range of alphas it returns a COS^2 based smooth blend.

    Attributes
    ----------

        blendWindow: float size of the window we want to blend from the given 2D polar
        alpha: float alpha we are at in radians
        alphaMinMax: float,   alpha min  or alpha max for that 2D polar in radians. Outside of those values we use
    the Flat plate coefficients
        alphaRange: string, used to figure out whether we are doing before CLmin or beyond CLmax
        return: float (blend value for that alpha
    """

    if 'aboveCLmax' in alphaRange:
        # we are on the CLMAX side:
        if alpha < alphaMinMax:
            return 1
        if alpha > alphaMinMax + blendWindow:
            return 0
        return cos((alpha - alphaMinMax) / blendWindow * pi / 2) ** 2
    if 'belowCLmin' in alphaRange:
        # we are on the CLMIN side:
        if alpha > alphaMinMax:
            return 1
        if alpha < alphaMinMax - blendWindow:
            return 0
        return cos((alpha - alphaMinMax) / blendWindow * pi / 2) ** 2
    else:
        raise ValueError('alphaRange must be either aboveCLmax or belowCLmin, it is: %s'%alphaRange)


########################################################################################################################
def blend2flatPlate(CLIFT, CDRAG, alphas, alphaMinIdx, alphaMaxIdx):
    """
     Blend the Clift and Cdrag values outside of the normal working range of alphas to the flat plate CL and CD values.
    :param CLIFT: float
    :param CDRAG: float
    :param alphas: list of floats
    :param alphaMinIdx: int, index within the above list of alphas
    :param alphaMaxIdx: int, index within the above list of alphas

    :return: 2 Floats representing the blended CL and CD at that alpha
    """

    blendWindow = 0.5  # 0.5 radians
    alphaMin = alphas[alphaMinIdx] * pi / 180
    alphaMax = alphas[alphaMaxIdx] * pi / 180

    for i in range(alphaMinIdx):  # from -pi to alphaMin in the CLIFT array
        a = alphas[i] * pi / 180  # alpha in radians

        blendVal = blendFuncValue(blendWindow, a, alphaMin, 'belowCLmin')  # we are on the alphaCLmin side going up in CL
        # this follows the flat plate lift and drag equations times the blend val coefficient
        CLIFT[i] = CLIFT[i] * blendVal + (1 - blendVal) * cos(a) * 2 * pi * sin(a) / sqrt(1 + (2 * pi * sin(a)) ** 2)
        CDRAG[i] = CDRAG[i] * blendVal + (1 - blendVal) * sin(a) * (2 * pi * sin(a)) ** 3 / sqrt(1 + (2 * pi * sin(a)) ** 6) + 0.05

    for j in range(alphaMaxIdx, len(alphas)):     # from alphaMax to Pi in the CLIFT array
        a = alphas[j] * pi / 180  # alpha in radians
        blendVal = blendFuncValue(blendWindow, a, alphaMax, 'aboveCLmax')  # we are on the alphaCLmax side of things going up in CL
        # this follows the flat plate lift and drag equations times the blend val coefficient
        CLIFT[j] = CLIFT[j] * blendVal + (1 - blendVal) * cos(a) * 2 * pi * sin(a) / sqrt(1 + (2 * pi * sin(a)) ** 2)
        CDRAG[j] = CDRAG[j] * blendVal + (1 - blendVal) * sin(a) * (2 * pi * sin(a)) ** 3 / sqrt(1 + (2 * pi * sin(a)) ** 6) + 0.05
    return CLIFT, CDRAG


########################################################################################################################
def calcClCd(xrotorDict, alphas, machNum, nrRstation):
    """

    This function is transcribed from the Xrotor source code. https://web.mit.edu/drela/Public/web/xrotor/
    Use the 2D polar parameters from the Xrotor input file to get the Cl and Cd at the various Alphas and given MachNum

    Calculate compressibility factor taken from xaero.f in xrotor source code
    Factors for compressibility drag model, HHY 10/23/00
    Mcrit is set by user ( ie read in from Xrotor file )
    Effective Mcrit is Mcrit_eff = Mcrit - CLMFACTOR*(CL-CLDmin) - DMDD
    DMDD is the delta Mach to get CD=CDMDD (usually 0.0020)
    Compressible drag is CDC = CDMFACTOR*(Mach-Mcrit_eff)^MEXP
    CDMstall is the drag at which compressible stall begins


    :param xrotorDict: dictionary of Xrotor data as read in by def readXROTORFile(xrotorFileName):
    :param alphas: list of ints, alphas we have for the polar.
    :param machNum: float, mach number we do this polar at.
    :param nrRstation: int, which r/R station we have to define this polar for.
    :return: 2 list of floats representing the CL and CD for  that polar
    """

    CDMFACTOR = 10.0
    CLMFACTOR = 0.25
    MEXP = 3.0
    CDMDD = 0.0020
    CDMSTALL = 0.1000

    # Prandtl-Glauert compressibility factor
    MSQ = machNum ** 2

    if MSQ > 1.0:
        print('CLFUNC: Local Mach^2 number limited to 0.99, was ', MSQ)
        MSQ = 0.99

    PG = 1.0 / sqrt(1.0 - MSQ)
    MACH = machNum

    # Generate CL from dCL/dAlpha and Prandtl-Glauert scaling
    A_zero = xrotorDict['a0deg'][nrRstation] * pi / 180
    A0 = array([A_zero for i in range(len(alphas))])
    DCLDA = xrotorDict['dclda'][nrRstation]
    CLA = DCLDA * PG * ((array(alphas) * pi / 180) - A0)

    # Reduce CLmax to match the CL of onset of serious compressible drag
    CLMAX = xrotorDict['clmax'][nrRstation]
    CLMIN = xrotorDict['clmin'][nrRstation]
    CLDMIN = xrotorDict['clcdmin'][nrRstation]
    MCRIT = xrotorDict['mcrit'][nrRstation]

    DMSTALL = (CDMSTALL / CDMFACTOR) ** (1.0 / MEXP)
    CLMAXM = max(0.0, (MCRIT + DMSTALL - MACH) / CLMFACTOR) + CLDMIN
    CLMAX = min(CLMAX, CLMAXM)
    CLMINM = min(0.0, - (MCRIT + DMSTALL - MACH) / CLMFACTOR) + CLDMIN
    CLMIN = max(CLMIN, CLMINM)

    # CL limiter function (turns on after +-stall)
    DCL_STALL = xrotorDict['dclstall'][nrRstation]
    ECMAX = exp(clip((CLA - CLMAX) / DCL_STALL, None, 200))
    ECMIN = exp(clip((CLMIN - CLA) / DCL_STALL, None, 200))
    CLLIM = DCL_STALL * log((1.0 + ECMAX) / (1.0 + ECMIN))

    # Subtract off a (nearly unity) fraction of the limited CL function
    # This sets the dCL/dAlpha in the stalled regions to 1-FSTALL of that
    # in the linear lift range
    DCLDA_STALL = xrotorDict['dcldastall'][nrRstation]
    FSTALL = DCLDA_STALL / DCLDA
    CLIFT = CLA - (1.0 - FSTALL) * CLLIM

    # In the basic linear lift range drag is a quadratic function of lift
    # CD = CD0 (constant) + quadratic with CL)
    CDMIN = xrotorDict['cdmin'][nrRstation]
    DCDCL2 = xrotorDict['dcddcl2'][nrRstation]

    # Don't do any reynolds number corrections b/c we know it is minimal
    RCORR = 1
    CDRAG = (CDMIN + DCDCL2 * (CLIFT - CLDMIN) ** 2) * RCORR

    # Post-stall drag added
    FSTALL = DCLDA_STALL / DCLDA
    DCDX = (1.0 - FSTALL) * CLLIM / (PG * DCLDA)
    DCD = 2.0 * DCDX ** 2

    # Compressibility drag (accounts for drag rise above Mcrit with CL effects
    # CDC is a function of a scaling factor*(M-Mcrit(CL))**MEXP
    # DMDD is the Mach difference corresponding to CD rise of CDMDD at MCRIT
    DMDD = (CDMDD / CDMFACTOR) ** (1.0 / MEXP)
    CRITMACH = MCRIT - CLMFACTOR * abs(CLIFT - CLDMIN) - DMDD
    CDC = [0 for i in range(len(CRITMACH))]
    for critMachIdx in range(len(CRITMACH)):
        if (MACH < CRITMACH[critMachIdx]):
            continue
        else:
            CDC[critMachIdx] = CDMFACTOR * (MACH - CRITMACH[critMachIdx]) ** MEXP

    # you could use something like this to add increase drag by Prandtl-Glauert
    # (or any function you choose)
    FAC = 1.0
    # --- Total drag terms
    CDRAG = FAC * CDRAG + DCD + CDC

    # Now we modify the Clift and CDrag outside of the large alpha range to smooth out
    # the Cl and CD outside of the expected operating range

    # Find the Alpha for ClMax and CLMin
    alphaMinIdx, alphaMaxIdx = findClMinMaxAlphas(CLIFT, CLMIN, CLMAX)
    # Blend the CLIFt and CDRAG values from above with the flat plate formulation to
    # be used outside of the alphaCLmin to alphaCLMax window
    CLIFT, CDRAG = blend2flatPlate(CLIFT, CDRAG, alphas, alphaMinIdx, alphaMaxIdx)

    return list(CLIFT), list(CDRAG)


########################################################################################################################
def getPolar(xrotorDict, alphas, machs, rRstation):
    """
    Return the 2D Cl and CD polar expected by the Flow360 BET model.
    b/c we have 4 Mach Values * 1 Reynolds value we need 4 different arrays per sectional polar as in:
    since the order of brackets is Mach#, Rey#, Values then we need to return:
    [[[array for MAch #1]],[[array for MAch #2]],[[array for MAch #3]],[[array for MAch #4]]]

    :param xrotorDict: dictionary of Xrotor data as read in by def readXROTORFile(xrotorFileName):
    :param alphas: list of floats
    :param machs: list of float
    :param rRstation: station index.
    :return: list of dictionaries
    """

    secpol = {}
    secpol['liftCoeffs'] = []
    secpol['dragCoeffs'] = []
    for machNum in machs:
        cl, cd = calcClCd(xrotorDict, alphas, machNum, rRstation)
        secpol['liftCoeffs'].append([cl])
        secpol['dragCoeffs'].append([cd])
    return secpol


########################################################################################################################
def generateXrotorBETJSON(xrotorFileName, axisOfRotation, centerOfRotation,
                    rotationDirectionRule, **kwargs):
    """

    This file takes in an Xrotor or DFDC input file and translates it into a flow360 BET input dictionary

    DFDC and Xrotor come from the same family of CFD codes. They are both written by Mark Drela over at MIT.
    we can use the same translator for both DFDC and Xrotor.

    :param xrotorFileName: string, filepath to the Xrotor/DFDC file we want to translate into a BET disk
    :param axisOfRotation: [x,y,z] coordinates of the rotation vector
    :param centerOfRotation: [x,y,z] coordinates of the rotation vector
    :param rotationDirectionRule: string, either "rightHand" or "leftHand". See https://docs.flexcompute.com/projects/flow360/en/latest/capabilities/bladeElementTheory.html#bet-input
    :param kwargs: various other arguments see https://docs.flexcompute.com/projects/flow360/en/latest/capabilities/bladeElementTheory.html#bet-input
    :return: dictionary that we should append to the Flow360.json file we want to run with.
    """

    diskThickness = kwargs['diskThickness']
    gridUnit = kwargs['gridUnit']
    chordRef = kwargs.pop('chordRef', 1.0)
    nLoadingNodes = kwargs.pop('nLoadingNodes', 20)
    tipGap = kwargs.pop('tipGap', 'inf')
    initialBladeDirection = kwargs.pop('initialBladeDirection', [1, 0, 0])

    if rotationDirectionRule not in ['rightHand', 'leftHand']:
        raise ValueError(f'Exiting. Invalid rotationDirectionRule of:{rotationDirectionRule}')
    if len(axisOfRotation) != 3:
        raise ValueError(f'axisOfRotation must be a list of size 3. Exiting.')
    if len(centerOfRotation) != 3:
        raise ValueError('centerOfRotation must be a list of size 3. Exiting')

    xrotorDict = readXROTORFile(xrotorFileName)


    diskJSON = {'axisOfRotation': axisOfRotation,
                'centerOfRotation': centerOfRotation,
                'rotationDirectionRule': rotationDirectionRule}

    # xrotorInflowMach = xrotorDict['vel'] / xrotorDict['vso']

    diskJSON['omega'] = xrotorDict['omegaDim'] * gridUnit / xrotorDict['vso']  # check this
    diskJSON['numberOfBlades'] = xrotorDict['nBlades']
    diskJSON['radius'] = xrotorDict['rad'] / gridUnit
    diskJSON['omega'] = xrotorDict['omegaDim'] * gridUnit / xrotorDict['vso']
    diskJSON['twists'] = generateTwists(xrotorDict, gridUnit)
    diskJSON['chords'] = generateChords(xrotorDict, gridUnit)
    diskJSON['MachNumbers'] = generateMachs()
    diskJSON['alphas'] = generateAlphas()
    diskJSON['ReynoldsNumbers'] = generateReys()
    diskJSON['thickness'] = diskThickness
    diskJSON['chordRef'] = chordRef
    diskJSON['nLoadingNodes'] = nLoadingNodes
    diskJSON['tipGap'] = tipGap
    diskJSON['sectionalRadiuses'] = [diskJSON['radius'] * r for r in xrotorDict['rRstations']]
    diskJSON['initialBladeDirection'] = initialBladeDirection
    diskJSON['sectionalPolars'] = []

    for secId in range(0, xrotorDict['nAeroSections']):
        polar = getPolar(xrotorDict, diskJSON['alphas'], diskJSON['MachNumbers'], secId)
        diskJSON['sectionalPolars'].append(polar)

    return diskJSON


########################################################################################################################
def test_translator():
    """
    run the translator with a representative set of inputs
    dumps betDisk JSON file that can be added to a Flow360 JSON file.
    """
    diskThickness = 0.05
    gridUnit = 1
    chordRef = 1
    nLoadingNodes = 20
    tipGap = 'inf'
    bladeLineChord = 1
    # initialBladeDirection =  [1, 0, 0]  # Used for time accurate Blade Line simulations
    xrotorFileName = 'examples/xrotorTranslator/ecruzer.prop'
    axisOfRotation = [0, 0, 1]
    centerOfRotation = [0, 0, 0]
    rotationDirectionRule = 'rightHand'

    xrotorInputDict = generateXrotorBETJSON(xrotorFileName, axisOfRotation, centerOfRotation,
                        rotationDirectionRule, diskThickness=diskThickness, gridUnit=gridUnit,
                        chordRef=chordRef, nLoadingNodes=nLoadingNodes, tipGap=tipGap,
                        bladeLineChord=bladeLineChord)
    betDiskJson = {'BETDisks': [xrotorInputDict]}  # make all that data a subset of BETDisks dictionary, notice the [] b/c
    # the BETDisks dictionary accepts a list of bet disks
    # dump the sample dictionary to a json file
    json.dump(betDiskJson, open('sampleBETJSON.json', 'w'), indent=4)


########################################################################################################################
if __name__ == '__main__':
    # if run on its own, then just run the test_translator() function
    test_translator()
