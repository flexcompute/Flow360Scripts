The genSlidingInterface.py generates a concentric ring-based rotational interface around an input profile.

To execute:

python genSlidingInterface.py --input examples/int_cylinder_coarse.json --output test.cgns

Things to consider:

1. Please see readme_prfoile.png to see how to define the input profile coordinates correctly.
2. Multiple segments can be defined in the 2D profile input. Please see examples in the examples/profiles directory.
3. The ending line of the input profile is required to not be an empty line.
4. The output file extension is used as the format to write the interface. UGRID, CGNS, dat, vtk, stl, obj, ply and etc are supported.
5. The cgns is written via pyCGNS python package and it is necessary to have it installed. (pip install pyCGNS)
6. Other formats are written via the meshio python package. (pip install meshio)

Examples can be found in the examples directory. The corresponding input profiles are in the examples/profiles directory.