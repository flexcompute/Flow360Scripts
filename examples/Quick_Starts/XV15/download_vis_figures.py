"""Downloads visualizations of surface CP, CF and streamlines"""

import os

from flow360 import MyCases
from PIL import Image

with open("case_name_list.dat", "r", encoding="utf-8") as file:
    case_name_list = file.read().splitlines()

fields = ["Cp", "Cf", "Fv"]


def fetch_png(case, field, res="H"):
    """Download the required figures from Flexcompute servers"""
    # download the legend i.e. color bar
    case_name = case.name
    os.makedirs("visualize", exist_ok=True)

    legend = f"visualize/{field}Legend.png"
    case._download_file(legend, to_file=legend)

    # list all available theta and phi
    view_angles = [(0, 0), (180, 0)]
    for theta in [60, 120]:
        for phi in range(0, 360, 90):
            view_angles.append((theta, phi))
    # download the contour + axis files
    for theta, phi in view_angles:
        fname = f"{theta:03d}_{phi:03d}.png"
        contour = f"visualize/{field}_{res}_{fname}"
        axis = f"visualize/Ax_{fname}"
        case._download_file(contour, to_file=contour)
        case._download_file(axis, to_file=axis)
        # load and overlap contour + axis + legend
        img_contour = Image.open(contour).convert("RGBA")
        img_axis = Image.open(axis)
        img_axis = img_axis.resize((img_axis.width * 3, img_axis.height * 3))
        img_axis = img_axis.convert("RGBA")
        img_legend = Image.open(legend).convert("RGBA")
        background = Image.new("RGBA", img_contour.size, (67, 100, 200))
        img_contour.paste(img_axis, (0, img_contour.height - img_axis.height), img_axis)
        img_contour.paste(
            img_legend,
            (-int(0.1 * img_contour.height), int(0.1 * img_contour.height)),
            img_legend,
        )
        background.paste(img_contour, (0, 0), img_contour)
        background.save(
            f"vis_figures/{case_name}_{field}_{res}_{theta:03d}_{phi:03d}_final.png"
        )


# set output directory
dir_path = os.path.join(os.getcwd(), "vis_figures")
os.makedirs(dir_path, exist_ok=True)

case = None
my_cases = MyCases(limit=None)

for case_name in case_name_list:
    case_folder = os.path.join(os.getcwd(), case_name)
    os.makedirs(case_folder, exist_ok=True)
    # Find the latest case with the name corresponding to the name in case_name_list
    for case in my_cases:
        if case.name == case_name:
            break
    print(case.name)
    for field in fields:
        fetch_png(case, field)
