from pathlib import Path
import csv
import io
import zipfile

project = Path.home() / "Documents" / "OpenBiomechanics-OpenSim"
zip_path = project / "openbiomechanics" / "baseball_pitching" / "data" / "full_sig" / "joint_angles.zip"
target = "3034_1"

count = 0
times = []
first = []
last = []
events = {}

with zipfile.ZipFile(zip_path) as z:
    with z.open("joint_angles.csv") as raw:
        reader = csv.DictReader(io.TextIOWrapper(raw, encoding="utf-8-sig", newline=""))
        for row in reader:
            if row["session_pitch"] != target:
                continue

            count += 1
            t = float(row["time"])
            times.append(t)

            if len(first) < 3:
                first.append((t, row["elbow_angle_x"], row["pelvis_angle_z"]))

            last.append((t, row["elbow_angle_x"], row["pelvis_angle_z"]))
            last = last[-3:]

            for key in ("pkh_time", "fp_10_time", "fp_100_time", "MER_time", "BR_time", "MIR_time"):
                if row.get(key):
                    events[key] = row[key]

print("Reference key:", target)
print("Rows:", count)
if times:
    print(f"First time: {min(times):.4f} s")
    print(f"Last time:  {max(times):.4f} s")
    print(f"Time span:  {max(times) - min(times):.4f} s")
print("\nFirst rows (time, elbow_angle_x, pelvis_angle_z):")
for item in first:
    print(item)
print("\nLast rows (time, elbow_angle_x, pelvis_angle_z):")
for item in last:
    print(item)
print("\nEvent times:")
for key, value in events.items():
    print(f"{key}: {value}")
