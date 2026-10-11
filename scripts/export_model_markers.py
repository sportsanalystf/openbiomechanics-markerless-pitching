from pathlib import Path
import csv
import opensim as osim

project = Path.home() / "Documents" / "OpenBiomechanics-OpenSim"
model_path = project / "models" / "RajagopalLaiUhlrich2023.osim"
out_path = project / "outputs" / "opensim_model_markers.csv"

model = osim.Model(str(model_path))
markers = model.getMarkerSet()

rows = []
for i in range(markers.getSize()):
    marker = markers.get(i)
    name = marker.getName()

    try:
        parent = marker.getParentFrame().getName()
    except Exception:
        try:
            parent = marker.getBody().getName()
        except Exception:
            parent = "unknown"

    try:
        loc = marker.get_location()
        xyz = [float(loc.get(j)) for j in range(3)]
    except Exception:
        xyz = ["", "", ""]

    rows.append({
        "marker": name,
        "parent_frame": parent,
        "local_x_m": xyz[0],
        "local_y_m": xyz[1],
        "local_z_m": xyz[2],
    })

with out_path.open("w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)

print("Model:", model_path)
print("Marker count:", len(rows))
print("Saved:", out_path)
print("\nMODEL MARKER NAMES")
for row in rows:
    print(
        f'{row["marker"]:18s} body={row["parent_frame"]:18s} '
        f'local=({row["local_x_m"]}, {row["local_y_m"]}, {row["local_z_m"]})'
    )
