from pathlib import Path
import csv
import json
import math

project = Path.home() / "Documents" / "OpenBiomechanics-OpenSim"
motion_path = project / "outputs" / "synthetic_arm_ik.mot"
comparison_path = project / "outputs" / "synthetic_arm_ik_comparison.csv"
report_path = project / "outputs" / "synthetic_arm_ik_validation.json"
truth_path = project / "outputs" / "synthetic_arm_ground_truth.csv"

if not motion_path.exists():
    raise FileNotFoundError(f"IK motion file not found: {motion_path}")

# Read the OpenSim .mot file and detect its angle units.
lines = motion_path.read_text(encoding="utf-8-sig").splitlines()
endheader = next(
    (i for i, line in enumerate(lines) if line.strip().lower() == "endheader"),
    None,
)
if endheader is None:
    raise ValueError("Could not find endheader in the .mot file.")

header_text = "\n".join(lines[:endheader])
in_degrees = any(
    line.strip().lower().replace(" ", "") in ("indegrees=yes", "indegrees= yes")
    for line in lines[:endheader]
)

data_lines = [
    line.strip()
    for line in lines[endheader + 1:]
    if line.strip() and not line.strip().startswith("#")
]
if not data_lines:
    raise ValueError("No motion data found after endheader.")

column_names = data_lines[0].split()
column_lookup = {name.lower(): i for i, name in enumerate(column_names)}

required = ("time", "r_shoulder_elev", "r_elbow_flex")
missing = [name for name in required if name not in column_lookup]
if missing:
    raise ValueError(
        f"Required columns missing: {missing}. Found: {column_names}"
    )

rows = []
with truth_path.open("w", newline="", encoding="utf-8") as truth_file, \
     comparison_path.open("w", newline="", encoding="utf-8") as comparison_file:

    truth_writer = csv.writer(truth_file)
    comparison_writer = csv.writer(comparison_file)

    truth_writer.writerow([
        "time",
        "true_r_shoulder_elev_rad",
        "true_r_elbow_flex_rad",
    ])
    comparison_writer.writerow([
        "time",
        "true_shoulder_rad",
        "estimated_shoulder_rad",
        "shoulder_error_deg",
        "true_elbow_rad",
        "estimated_elbow_rad",
        "elbow_error_deg",
    ])

    for line in data_lines[1:]:
        values = line.split()
        if len(values) < len(column_names):
            continue

        time = float(values[column_lookup["time"]])
        phase = 2.0 * math.pi * time / 1.0

        true_shoulder = 0.2 + 0.5 * (1.0 - math.cos(phase)) / 2.0
        true_elbow = 0.25 + 0.7 * (
            1.0 - math.cos(phase + math.pi / 3.0)
        ) / 2.0

        estimated_shoulder = float(
            values[column_lookup["r_shoulder_elev"]]
        )
        estimated_elbow = float(
            values[column_lookup["r_elbow_flex"]]
        )

        if in_degrees:
            estimated_shoulder = math.radians(estimated_shoulder)
            estimated_elbow = math.radians(estimated_elbow)

        shoulder_error_deg = math.degrees(
            estimated_shoulder - true_shoulder
        )
        elbow_error_deg = math.degrees(estimated_elbow - true_elbow)

        truth_writer.writerow([
            f"{time:.8f}",
            f"{true_shoulder:.10f}",
            f"{true_elbow:.10f}",
        ])
        comparison_writer.writerow([
            f"{time:.8f}",
            f"{true_shoulder:.10f}",
            f"{estimated_shoulder:.10f}",
            f"{shoulder_error_deg:.8f}",
            f"{true_elbow:.10f}",
            f"{estimated_elbow:.10f}",
            f"{elbow_error_deg:.8f}",
        ])

        rows.append({
            "time": time,
            "shoulder_error_deg": shoulder_error_deg,
            "elbow_error_deg": elbow_error_deg,
        })

if not rows:
    raise ValueError("No motion frames were successfully compared.")

def summarize(key):
    errors = [row[key] for row in rows]
    return {
        "mae_deg": sum(abs(e) for e in errors) / len(errors),
        "rmse_deg": math.sqrt(sum(e * e for e in errors) / len(errors)),
        "max_absolute_error_deg": max(abs(e) for e in errors),
    }

report = {
    "validation": "IK joint angles compared with known synthetic angles",
    "frames_compared": len(rows),
    "motion_file_angles_in_degrees": in_degrees,
    "shoulder_elevation": summarize("shoulder_error_deg"),
    "elbow_flexion": summarize("elbow_error_deg"),
    "outputs": {
        "comparison_csv": str(comparison_path),
        "ground_truth_csv": str(truth_path),
    },
}

report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

print(json.dumps(report, indent=2))
print("\nSaved comparison:", comparison_path)
print("Saved ground truth:", truth_path)
print("Saved validation report:", report_path)
