"""
This module is meant as an example of how you would use the C81 polars => Flow360 BET disk translator function
Since the C81 polars provide only the 2D polars of the various sections we need to enter the remaining information
that the BET disk implementation needs. Things like blade Radius, RPM, # of blades, disk location and thrust axis etc...

This can be done either by reading in a JSON file you have setup with all the information not included in the C81 polars
or you can hard code them in you translator script.

In this example, all the required values are hard coded in this sample script.

EXAMPLE useage:
    python3 sampleDFDCTranslateScript.py

"""

import BETTranslatorInterface as interf
import json