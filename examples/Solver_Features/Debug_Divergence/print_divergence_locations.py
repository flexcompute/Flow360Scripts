"""Print the divergence locations for minimum density, pressure, eddy viscosity and maximum velocity magnitude"""

import os

import pandas as pd

with open("case_name_list.dat", "r", encoding="utf-8") as file:
    case_name_list = file.read().splitlines()

for case in case_name_list:
    csv_path = os.path.join(os.getcwd(), case, "minmax_state_v2.csv")
    data = pd.read_csv(csv_path, skipinitialspace=True)
    print(case)
    print(
            "Minimum Density:{} at location xyz = {}, {}, {}".format(
            data["min_rho"].values[-1],
            data["min_rho_x"].values[-1],
            data["min_rho_y"].values[-1],
            data["min_rho_z"].values[-1],
        )
    )
    print(
        "Minimum Pressure: {} at location xyz = {}, {}, {}".format(
            data["min_p"].values[-1],
            data["min_p_x"].values[-1],
            data["min_p_y"].values[-1],
            data["min_p_z"].values[-1],
        )
    )
    print(
        "Maximum Velocity Magnitude: {} at location xyz = {}, {}, {}".format(
            data["max_umag"].values[-1],
            data["max_umag_x"].values[-1],
            data["max_umag_y"].values[-1],
            data["max_umag_z"].values[-1],
        )
    )
    print(
        "Minimum nuHat Magnitude: {} at location xyz = {}, {}, {}".format(
            data["min_nuHat"].values[-1],
            data["min_nuHat_x"].values[-1],
            data["min_nuHat_y"].values[-1],
            data["min_nuHat_z"].values[-1],
        )
    )
