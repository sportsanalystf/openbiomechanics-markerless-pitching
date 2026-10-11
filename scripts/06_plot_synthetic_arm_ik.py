from pathlib import Path
import csv
import matplotlib.pyplot as plt

project = Path(__file__).resolve().parents[1]
csv_path = project / "outputs" / "synthetic_arm_ik_comparison.csv"
output_dir = project / "outputs"

if not csv_path.exists():
    raise FileNotFoundError(f"Comparison CSV not found: {csv_path}")

with csv_path.open("r", newline="", encoding="utf-8-sig") as f:
    rows = list(csv.DictReader(f))

if not rows:
    raise ValueError("The comparison CSV contains no data rows.")

time = [float(r["time"]) for r in rows]

true_shoulder = [
    float(r["true_shoulder_rad"]) * 180.0 / 3.141592653589793
    for r in rows
]
estimated_shoulder = [
    float(r["estimated_shoulder_rad"]) * 180.0 / 3.141592653589793
    for r in rows
]
true_elbow = [
    float(r["true_elbow_rad"]) * 180.0 / 3.141592653589793
    for r in rows
]
estimated_elbow = [
    float(r["estimated_elbow_rad"]) * 180.0 / 3.141592653589793
    for r in rows
]

shoulder_error = [float(r["shoulder_error_deg"]) for r in rows]
elbow_error = [float(r["elbow_error_deg"]) for r in rows]

# Figure 1: ground-truth and estimated joint angles.
fig, axes = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

axes[0].plot(time, true_shoulder, label="Ground truth")
axes[0].plot(time, estimated_shoulder, "--", label="IK estimate")
axes[0].set_ylabel("Angle (degrees)")
axes[0].set_title("Shoulder elevation: ground truth vs IK")
axes[0].legend()
axes[0].grid(True, alpha=0.3)

axes[1].plot(time, true_elbow, label="Ground truth")
axes[1].plot(time, estimated_elbow, "--", label="IK estimate")
axes[1].set_xlabel("Time (seconds)")
axes[1].set_ylabel("Angle (degrees)")
axes[1].set_title("Elbow flexion: ground truth vs IK")
axes[1].legend()
axes[1].grid(True, alpha=0.3)

fig.tight_layout()
angles_path = output_dir / "synthetic_arm_ik_angles.png"
fig.savefig(angles_path, dpi=160, bbox_inches="tight")
plt.close(fig)

# Figure 2: angle estimation errors.
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(time, shoulder_error, label="Shoulder error")
ax.plot(time, elbow_error, label="Elbow error")
ax.axhline(0, linewidth=1)
ax.set_xlabel("Time (seconds)")
ax.set_ylabel("Estimated - true (degrees)")
ax.set_title("Synthetic arm IK joint-angle error")
ax.legend()
ax.grid(True, alpha=0.3)

fig.tight_layout()
errors_path = output_dir / "synthetic_arm_ik_errors.png"
fig.savefig(errors_path, dpi=160, bbox_inches="tight")
plt.close(fig)

print(f"Frames plotted: {len(rows)}")
print(f"Joint-angle plot: {angles_path}")
print(f"Error plot: {errors_path}")

