from pathlib import Path
import csv
import numpy as np
import ezc3d

project = Path.home() / "Documents" / "OpenBiomechanics-OpenSim"
data_dir = project / "openbiomechanics" / "baseball_pitching" / "data"
filename = "000002_003034_model.c3d"

matches = list(data_dir.rglob(filename))
if len(matches) != 1:
    raise FileNotFoundError(f"Expected one {filename}; found {matches}")

c3d_path = matches[0]
c3d = ezc3d.c3d(str(c3d_path))

labels = [
    str(x).strip()
    for x in c3d["parameters"]["POINT"]["LABELS"]["value"]
]
points = np.asarray(c3d["data"]["points"], dtype=float)
xyz = points[:3, :, :]

output_path = project / "outputs" / "static_marker_coordinates.csv"
output_path.parent.mkdir(parents=True, exist_ok=True)

rows = []
for i, label in enumerate(labels):
    coords = xyz[:, i, :]
    valid = np.all(np.isfinite(coords), axis=0)
    valid_coords = coords[:, valid]

    if valid_coords.shape[1] == 0:
        rows.append({
            "marker": label, "x_m": "", "y_m": "", "z_m": "",
            "frames_valid": 0, "max_deviation_mm": ""
        })
        continue

    mean = np.mean(valid_coords, axis=1)
    deviations = np.linalg.norm(valid_coords - mean[:, None], axis=0)

    rows.append({
        "marker": label,
        "x_m": f"{mean[0]:.6f}",
        "y_m": f"{mean[1]:.6f}",
        "z_m": f"{mean[2]:.6f}",
        "frames_valid": int(valid_coords.shape[1]),
        "max_deviation_mm": f"{np.max(deviations) * 1000:.2f}"
    })

with output_path.open("w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(
        f,
        fieldnames=[
            "marker", "x_m", "y_m", "z_m",
            "frames_valid", "max_deviation_mm"
        ]
    )
    writer.writeheader()
    writer.writerows(rows)

print("Static C3D:", c3d_path)
print("Frames:", xyz.shape[2])
print("Markers:", len(labels))
print("Units:", c3d["parameters"]["POINT"]["UNITS"]["value"])
print("Saved:", output_path)
print("\n=== STATIC MARKER COORDINATES (meters) ===")
for row in rows:
    print(
        f"{row['marker']:6s} "
        f"x={str(row['x_m']):>9s} "
        f"y={str(row['y_m']):>9s} "
        f"z={str(row['z_m']):>9s} "
        f"valid_frames={row['frames_valid']} "
        f"max_deviation_mm={row['max_deviation_mm']}"
    )
