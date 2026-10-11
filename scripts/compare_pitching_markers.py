from pathlib import Path
import opensim

project = Path.home() / "Documents" / "OpenBiomechanics-OpenSim"
model_path = project / "models" / "RajagopalLaiUhlrich2023.osim"
labels_path = project / "outputs" / "pitching_c3d_marker_labels.txt"

measured = {
    line.strip()
    for line in labels_path.read_text(encoding="utf-8").splitlines()
    if line.strip()
}

model = opensim.Model(str(model_path))
model.initSystem()
marker_set = model.getMarkerSet()

model_markers = {
    marker_set.get(i).getName()
    for i in range(marker_set.getSize())
}

overlap = sorted(measured & model_markers)
unmatched = sorted(measured - model_markers)

print("\n=== MARKER MAPPING SUMMARY ===")
print("Measured markers:", len(measured))
print("Model markers:", len(model_markers))
print("Exact-name matches:", len(overlap))
print("Measured markers needing mapping:", len(unmatched))

print("\n=== EXACT-NAME MATCHES ===")
print(", ".join(overlap) if overlap else "(none)")

print("\n=== MEASURED MARKERS NEEDING MAPPING ===")
print(", ".join(unmatched) if unmatched else "(none)")

print("\n=== MODEL MARKERS NOT PRESENT IN C3D ===")
print(", ".join(sorted(model_markers - measured)))

print("\n=== STATIC CALIBRATION FILE EXISTS ===")
static_path = project / "openbiomechanics" / "baseball_pitching" / "data" / "c3d" / "000002" / "000002_003034_model.c3d"
print(static_path.exists(), static_path)
