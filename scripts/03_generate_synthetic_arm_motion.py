from pathlib import Path
import json
import math
import opensim as osim

project = Path(__file__).resolve().parents[1]
model_path = project / "models" / "arm26.osim"
output_path = project / "synthetic_data" / "synthetic_arm_motion.trc"

model = osim.Model(str(model_path))
state = model.initSystem()

coordinates = model.getCoordinateSet()
shoulder = coordinates.get("r_shoulder_elev")
elbow = coordinates.get("r_elbow_flex")
markers = model.getMarkerSet()

marker_names = [markers.get(i).getName() for i in range(markers.getSize())]
if len(marker_names) != 3:
    raise RuntimeError(f"Expected 3 model markers, found {len(marker_names)}")

fps = 100.0
num_frames = 101
duration = (num_frames - 1) / fps

# Smooth, deliberately modest movements within the model's coordinate ranges.
frames = []
for i in range(num_frames):
    t = i / fps
    phase = 2.0 * math.pi * t / duration

    shoulder_angle = 0.2 + 0.5 * (1.0 - math.cos(phase)) / 2.0
    elbow_angle = 0.25 + 0.7 * (1.0 - math.cos(phase + math.pi / 3.0)) / 2.0

    shoulder.setValue(state, shoulder_angle)
    elbow.setValue(state, elbow_angle)
    model.realizePosition(state)

    row = []
    for j in range(markers.getSize()):
        p = markers.get(j).getLocationInGround(state)
        row.extend([p.get(0), p.get(1), p.get(2)])
    frames.append((t, row))

output_path.parent.mkdir(parents=True, exist_ok=True)

with output_path.open("w", encoding="utf-8", newline="") as f:
    f.write(f"PathFileType\t4\t(X/Y/Z)\t{output_path.name}\n")
    f.write(
        "DataRate\tCameraRate\tNumFrames\tNumMarkers\tUnits\t"
        "OrigDataRate\tOrigDataStartFrame\tOrigNumFrames\n"
    )
    f.write(f"{fps:g}\t{fps:g}\t{num_frames}\t3\tm\t{fps:g}\t1\t{num_frames}\n")

    f.write("Frame#\tTime")
    for name in marker_names:
        f.write(f"\t{name}\t\t")
    f.write("\n")

    f.write("\t\t")
    for j in range(1, len(marker_names) + 1):
        f.write(f"X{j}\tY{j}\tZ{j}")
        if j < len(marker_names):
            f.write("\t")
    f.write("\n")

    for frame_number, (t, values) in enumerate(frames, start=1):
        f.write(f"{frame_number}\t{t:.6f}")
        for value in values:
            f.write(f"\t{value:.9f}")
        f.write("\n")

# Re-open with OpenSim to verify the generated TRC.
table = osim.TimeSeriesTableVec3(str(output_path))
loaded_labels = list(table.getColumnLabels())

if table.getNumRows() != num_frames:
    raise RuntimeError(f"Expected {num_frames} rows, got {table.getNumRows()}")
if loaded_labels != marker_names:
    raise RuntimeError(f"Marker label mismatch: {loaded_labels} vs {marker_names}")

report = {
    "model": str(model_path),
    "trc_file": str(output_path),
    "frames": table.getNumRows(),
    "markers": loaded_labels,
    "frame_rate_hz": fps,
    "duration_seconds": duration,
    "coordinate_inputs": ["r_shoulder_elev", "r_elbow_flex"],
    "validation": "OpenSim successfully re-read the generated TRC"
}

report_path = project / "outputs" / "synthetic_arm_motion_report.json"
report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

print(json.dumps(report, indent=2))
print(f"\nReport saved to: {report_path}")
