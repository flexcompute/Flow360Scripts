import os
import numpy as np
import flow360 as fl
#from flow360.component.case import CaseDownloadable
#from flow360.component.resource_base import Flow360Resource

from flow360 import MyCases
from PIL import Image

def fetchPNG(case, field, res = 'H'):
    # download the legend i.e. color bar
    casename = case.name
    os.makedirs('visualize', exist_ok=True)

    legend = f'visualize/{field}Legend.png'
    case._download_file(legend, to_file=legend)
    
    # list all available theta and phi 
    viewAngles = [(0, 0),(180, 0)]
    for theta in [60, 120]:
        for phi in range(0,360,90):
            viewAngles.append((theta, phi))        
    # download the contour + axis files
    for theta, phi in viewAngles:
        fname   = f'{theta:03d}_{phi:03d}.png'
        contour = f'visualize/{field}_{res}_{fname}'
        axis    = f'visualize/Ax_{fname}' 
        case._download_file(contour, to_file=contour)
        case._download_file(axis, to_file=axis)
        # load and overlap contour + axis + legend
        imgContour = Image.open(contour).convert('RGBA')
        imgAxis    = Image.open(axis)  
        imgAxis    = imgAxis.resize((imgAxis.width * 3, imgAxis.height * 3))
        imgAxis    = imgAxis.convert('RGBA')
        imgLegend  = Image.open(legend).convert('RGBA')
        background = Image.new('RGBA', imgContour.size, (67,100,200))
        imgContour.paste(imgAxis, (0,imgContour.height-imgAxis.height), imgAxis)
        imgContour.paste(imgLegend, (-int(0.1*imgContour.height), int(0.1*imgContour.height)), imgLegend)
        background.paste(imgContour, (0,0), imgContour)
        background.save(f'visualization_figures/{casename}_{field}_{res}_{theta:03d}_{phi:03d}_final.png')

def main():
    os.makedirs('visualization_figures', exist_ok=True)
    with open('caseNameList.dat', 'r') as file:
        caseNameList = file.read().splitlines()
    my_cases = MyCases(limit=None)
    for i in range(0, len(caseNameList)):
        caseFolder = os.path.join(os.getcwd(), caseNameList[i])
        os.makedirs(caseFolder, exist_ok = True)
        #Find the latest case with the name corresponding to the name in caseNameList
        for case in my_cases:
            if case.name == caseNameList[i]:
                break
        print(case.name)
        fetchPNG(case, 'Cp')
        fetchPNG(case, 'Cf')
        fetchPNG(case, 'Fv')

if __name__ == "__main__":
    main()
