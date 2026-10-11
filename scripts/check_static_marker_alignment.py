from pathlib import Path
import csv
import numpy as np
import opensim

project = Path.home() / "Documents" / "OpenBiomechanics-OpenSim"
model_path = project / "models" / "RajagopalLaiUhlrich2023.osim"
csv_path = project / "outputs" / "static_marker_coordinates.csv"

fit_names = ["LASI", "LPSI", "RASI", "RPSI"]
check_names = ["C7", "CLAV", "LASI", "LPSI", "RASI", "RPSI", "LTOE", "RTOE"]

static_raw = {}
with csv_path.open("r", newline="", encoding="utf-8-sig") as f:
    for row in csv.DictReader(f):
        static_raw[row["marker"]] = np.array(
            [float(row["x_m"]), float(row["y_m"]), float(row["z_m"])]
        )

# Convert laboratory Z-up coordinates to the model's Y-up convention.
static = {
    name: np.array([static_raw[name][0], static_raw[name][2], -static_raw[name][1]])
    for name in check_names
}

model = opensim.Model(str(model_path))
state = model.initSystem()
marker_set = model.getMarkerSet()
model_positions = {}

for i in range(marker_set.getSize()):
    marker = marker_set.get(i)
    name = marker.getName()
    if name in check_names:
        p = marker.getLocationInGround(state)
        model_positions[name] = np.array([p.get(0), p.get(1), p.get(2)])

X = np.vstack([model_positions[n] for n in fit_names])
Y = np.vstack([static[n] for n in fit_names])

x_mean = X.mean(axis=0)
y_mean = Y.mean(axis=0)
U, _, Vt = np.linalg.svd((X - x_mean).T @ (Y - y_mean))
R = U @ Vt
if np.linalg.det(R) < 0:
    U[:, -1] *= -1
    R = U @ Vt

print("\nPELVIS-FIT RESIDUALS (no scaling)")
print("Fit markers:", ", ".join(fit_names))
print("Marker   Residual (mm)   Model position (m)       Static position (m)")

for name in check_names:
    aligned = (model_positions[name] - x_mean) @ R + y_mean
    error = np.linalg.norm(aligned - static[name]) * 1000
    print(
        f"{name:5s}   {error:8.1f}       "
        f"{np.array2string(aligned, precision=3, suppress_small=True):24s} "
        f"{np.array2string(static[name], precision=3, suppress_small=True)}"
    )
