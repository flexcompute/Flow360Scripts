import numpy as np
import math
from scipy import linalg

# rotational matrix around an axis
def Mrotate (axis,theta):
    return linalg.expm(np.cross(np.eye(3), axis/linalg.norm(axis)*theta))
#end

#rotates around Z from origin
def rotatePointZ (points,theta):
    rotCoords = []
    for i in range(len(points)):
        rotCoords.append(np.dot(Mrotate(np.array([0,0,1]),theta),points[i]).tolist())
    return rotCoords
#end

#rotates around Y from origin
def rotatePointY (points,theta):
    rotCoords = []
    for i in range(len(points)):
        rotCoords.append(np.dot(Mrotate(np.array([0,1,0]),theta),points[i]).tolist())
    return rotCoords
#end

#translates points with dx dy dz
def translatePoints (points,dx,dy,dz):
    return (points + np.array([dx,dy,dz])).tolist()
#end

#scale points with a factor
def scalePoints(points,scale_f):
    return (np.array(points)*scale_f).tolist()
#end

#calculates angles to align the interface axis
def rotationalAngles (intAxis):
    thetaY = math.asin(intAxis[2]/linalg.norm(intAxis))
    thetaZ = math.asin(intAxis[1]/linalg.norm(intAxis))
    return [thetaY,thetaZ]
#end

#transform mesh points according to interface axis
def transformMesh(mesh, rotAngles,centerInterface,centerPosition):
    meshTranslate = translatePoints(mesh[0][0],-centerInterface[0],-centerInterface[1],-centerInterface[2])
    meshRotY = rotatePointY(meshTranslate,rotAngles[0])
    meshRotZ = rotatePointZ(meshRotY,rotAngles[1])
    meshTranslateBack = translatePoints(meshRotZ,centerInterface[0],centerInterface[1],centerInterface[2])
    deltaX = centerInterface[0]-centerPosition[0]
    deltaY = centerInterface[1]-centerPosition[1]
    deltaZ = centerInterface[2]-centerPosition[2]
    meshTranslatePosition = translatePoints(meshTranslateBack,-deltaX,-deltaY,-deltaZ)
    return [meshTranslatePosition,mesh[1][0]]
#end