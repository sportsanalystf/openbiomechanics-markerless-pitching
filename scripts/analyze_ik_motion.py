from pathlib import Path
import csv
import math
import matplotlib.pyplot as plt

project = Path(r"C:\Users\xdy6sg\Documents\OpenBiomechanics-OpenSim")
motion = project / "outputs" / "ik_3034_1" / "pitch_3034_1_ik.mot"
out = project / "outputs" / "ik_3034_1"
out.mkdir(parents=True, exist_ok=True)

lines = motion.read_text(encoding="utf-8", errors="replace").splitlines()
endheader = next((i for i, line in enumerate(lines)
                  if line.strip().lower() == "endheader"), None)
if endheader is None:
    raise RuntimeError("Could not find endheader in the motion file.")

labels = lines[endheader + 1].split()
rows = []
for line in lines[endheader + 2:]:
    if not line.strip():
        continue
    values = line.split()
    if len(values) != len(labels):
        print("Skipping malformed row:", line[:100])
        continue
    rows.append(dict(zip(labels, map(float, values))))

if not rows or "time" not in labels:
    raise RuntimeError("No valid motion data or time column found.")

print("Frames:", len(rows))
print("Time range: %.4f to %.4f s" %
      (rows[0]["time"], rows[-1]["time"]))
print("Coordinates:", len(labels) - 1)

events = [
    (0.7500, "Peak knee height"),
    (1.4306, "Foot plant"),
    (1.4444, "Foot plant 100%"),
    (1.5667, "Max external rotation"),
    (1.6000, "Ball release"),
    (1.6417, "Max internal rotation"),
]

groups = {
    "pelvis_trunk": [
        "pelvis_tilt", "pelvis_list", "pelvis_rotation",
        "lumbar_extension", "lumbar_bending", "lumbar_rotation"
    ],
    "lower_body": [
        "hip_flexion_r", "hip_flexion_l",
        "hip_adduction_r", "hip_adduction_l",
        "knee_angle_r", "knee_angle_l",
        "ankle_angle_r", "ankle_angle_l"
    ],
    "throwing_arm": [
        "arm_flex_r", "arm_add_r", "arm_rot_r",
        "elbow_flex_r", "pro_sup_r", "wrist_flex_r", "wrist_dev_r"
    ],
    "non_throwing_arm": [
        "arm_flex_l", "arm_add_l", "arm_rot_l",
        "elbow_flex_l", "pro_sup_l", "wrist_flex_l", "wrist_dev_l"
    ],
}

summary_path = out / "ik_coordinate_summary.csv"
with summary_path.open("w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["coordinate", "minimum", "minimum_time_s",
                     "maximum", "maximum_time_s", "range", "units"])
    for col in labels:
        if col == "time":
            continue
        vals = [r[col] for r in rows]
        imin, imax = min(range(len(vals)), key=vals.__getitem__), \
                     max(range(len(vals)), key=vals.__getitem__)
        units = "m" if col in ("pelvis_tx", "pelvis_ty", "pelvis_tz") else "degrees"
        writer.writerow([
            col, vals[imin], rows[imin]["time"],
            vals[imax], rows[imax]["time"],
            max(vals) - min(vals), units
        ])

for group_name, requested in groups.items():
    cols = [c for c in requested if c in labels]
    if not cols:
        continue

    fig, axes = plt.subplots(
        len(cols), 1,
        figsize=(12, max(4, 1.8 * len(cols))),
        sharex=True, squeeze=False
    )
    axes = axes.ravel()

    for ax, col in zip(axes, cols):
        ax.plot([r["time"] for r in rows],
                [r[col] for r in rows], linewidth=1.2)
        ax.set_ylabel(col, fontsize=8)
        ax.grid(True, alpha=0.3)
        for t, name in events:
            ax.axvline(t, linestyle="--", linewidth=0.8, alpha=0.5)

    axes[-1].set_xlabel("Time (s)")
    axes[0].set_title("OpenSim IK coordinates - " + group_name.replace("_", " ").title())
    fig.tight_layout()
    path = out / (group_name + "_coordinates.png")
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print("Created:", path)

print("Summary CSV:", summary_path)
