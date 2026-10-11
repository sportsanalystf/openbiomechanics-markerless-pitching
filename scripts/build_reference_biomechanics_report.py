from pathlib import Path
import csv
import io
import zipfile
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

project = Path.home() / "Documents" / "OpenBiomechanics-OpenSim"
zip_path = project / "openbiomechanics" / "baseball_pitching" / "data" / "full_sig" / "joint_angles.zip"
out = project / "outputs"
out.mkdir(parents=True, exist_ok=True)

target = "3034_1"
event_cols = ("pkh_time", "fp_10_time", "fp_100_time",
              "MER_time", "BR_time", "MIR_time")

with zipfile.ZipFile(zip_path) as z:
    with z.open("joint_angles.csv") as raw:
        reader = csv.DictReader(io.TextIOWrapper(raw, encoding="utf-8-sig", newline=""))
        rows = [r for r in reader if r["session_pitch"] == target]

if not rows:
    raise RuntimeError(f"No rows found for {target} in {zip_path}")

times = [float(r["time"]) for r in rows]
events = {}
for col in event_cols:
    value = rows[0].get(col, "")
    if value:
        events[col] = float(value)

# Save the exact reference trajectory for reproducibility.
csv_path = out / "reference_joint_angles_3034_1.csv"
with csv_path.open("w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)

# Angles are in degrees in the official full-signal table.
plots = [
    ("pelvis_angle_x", "pelvis_angle_y", "pelvis_angle_z"),
    ("torso_angle_x", "torso_angle_y", "torso_angle_z"),
    ("torso_pelvis_angle_x", "torso_pelvis_angle_y", "torso_pelvis_angle_z"),
    ("rear_hip_angle_x", "rear_hip_angle_y", "rear_hip_angle_z"),
    ("rear_knee_angle_x", "rear_knee_angle_y", "rear_knee_angle_z"),
    ("shoulder_angle_x", "shoulder_angle_y", "shoulder_angle_z"),
    ("elbow_angle_x", "elbow_angle_y", "elbow_angle_z"),
    ("wrist_angle_x", "wrist_angle_y", "wrist_angle_z"),
]

def event_label(key):
    return {
        "pkh_time": "Peak knee height",
        "fp_10_time": "Foot plant (10%)",
        "fp_100_time": "Foot plant (100%)",
        "MER_time": "Max external rotation",
        "BR_time": "Ball release",
        "MIR_time": "Max internal rotation",
    }.get(key, key)

plot_files = []
for group in plots:
    available = [c for c in group if c in rows[0]]
    if not available:
        continue

    fig, ax = plt.subplots(figsize=(11, 5.5))
    for col in available:
        values = [float(r[col]) if r[col] else float("nan") for r in rows]
        ax.plot(times, values, label=col)

    for key, t in events.items():
        ax.axvline(t, linestyle="--", linewidth=0.9, alpha=0.65)
    ax.set_title(" / ".join(available))
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Angle (degrees)")
    ax.grid(True, alpha=0.25)
    ax.legend(loc="best")
    fig.tight_layout()

    filename = "reference_" + available[0].rsplit("_", 1)[0] + "_3034_1.png"
    path = out / filename
    fig.savefig(path, dpi=150)
    plt.close(fig)
    plot_files.append(filename)

event_names = {
    "pkh_time": "Peak knee height",
    "fp_10_time": "Foot plant (10%)",
    "fp_100_time": "Foot plant (100%)",
    "MER_time": "Maximum external rotation",
    "BR_time": "Ball release",
    "MIR_time": "Maximum internal rotation",
}
summary = {
    "session_pitch": target,
    "rows": len(rows),
    "start_time_s": min(times),
    "end_time_s": max(times),
    "duration_s": max(times) - min(times),
    "estimated_sampling_hz": 1 / (times[1] - times[0]) if len(times) > 1 else None,
    "events": [
        {"event": event_names.get(k, k), "column": k, "time_s": v}
        for k, v in events.items()
    ],
    "plots": plot_files,
    "reference_csv": csv_path.name,
}
(out / "reference_biomechanics_summary_3034_1.json").write_text(
    json.dumps(summary, indent=2), encoding="utf-8"
)

html_path = out / "reference_biomechanics_report_3034_1.html"
parts = [
    "<!doctype html><html><head><meta charset='utf-8'>",
    "<meta name='viewport' content='width=device-width,initial-scale=1'>",
    "<title>Pitching Biomechanics Reference — 3034_1</title>",
    "<style>body{font:16px system-ui;max-width:1100px;margin:30px auto;padding:0 18px;color:#202a35}",
    "img{max-width:100%;height:auto;border:1px solid #ddd;border-radius:8px}",
    "table{border-collapse:collapse}td,th{padding:8px 12px;border-bottom:1px solid #ddd;text-align:left}",
    "code{background:#f2f4f7;padding:2px 4px}</style></head><body>",
    "<h1>Pitching biomechanics reference</h1>",
    f"<p>Trial <code>{target}</code> · {len(rows)} frames · "
    f"{min(times):.4f}–{max(times):.4f} s · official joint-angle trajectories</p>",
    "<p>Dashed vertical lines indicate recorded event times. Angle conventions should be "
    "confirmed before interpreting signs or comparing directly with another model.</p>",
    "<h2>Pitching events</h2><table><tr><th>Event</th><th>Time (s)</th></tr>",
]
for key, t in events.items():
    parts.append(f"<tr><td>{event_names.get(key, key)}</td><td>{t:.4f}</td></tr>")
parts.append("</table><h2>Joint-angle trajectories</h2>")
for filename in plot_files:
    parts.append(f"<h3>{filename}</h3><img src='{filename}' alt='{filename}'>")
parts.append(
    f"<p>Raw reference table: <a href='{csv_path.name}'>{csv_path.name}</a></p>"
    "</body></html>"
)
html_path.write_text("\n".join(parts), encoding="utf-8")

print("Reference trial:", target)
print("Frames:", len(rows))
print(f"Duration: {max(times)-min(times):.4f} s")
print("Plots created:", len(plot_files))
print("CSV:", csv_path)
print("Summary:", out / "reference_biomechanics_summary_3034_1.json")
print("HTML report:", html_path)
