from pathlib import Path
import traceback
import opensim as osim

project = Path.home() / "Documents" / "OpenBiomechanics-OpenSim"
model_path = project / "models" / "RajagopalLaiUhlrich2023.osim"
trc_path = project / "outputs" / "pitch_3034_1_mapped.trc"
out_dir = project / "outputs" / "ik_3034_1"
out_dir.mkdir(parents=True, exist_ok=True)

motion_path = out_dir / "pitch_3034_1_ik.mot"
log_path = out_dir / "inverse_kinematics_log.txt"

if not model_path.exists():
    raise FileNotFoundError(model_path)
if not trc_path.exists():
    raise FileNotFoundError(trc_path)

print("Loading model...")
model = osim.Model(str(model_path))
model.initSystem()

print("Creating inverse kinematics tool...")
ik = osim.InverseKinematicsTool()
ik.setModel(model)
ik.setMarkerDataFileName(str(trc_path))
ik.setStartTime(0.0)
ik.setEndTime(2.0138888889)
ik.setOutputMotionFileName(str(motion_path))

# OpenSim versions expose the results-directory setter under this name.
if hasattr(ik, "setResultsDir"):
    ik.setResultsDir(str(out_dir))
elif hasattr(ik, "set_results_directory"):
    ik.set_results_directory(str(out_dir))

if hasattr(ik, "set_report_errors"):
    ik.set_report_errors(True)

print("Model:", model_path)
print("Marker data:", trc_path)
print("Output motion:", motion_path)
print("Time range: 0.0000 to 2.0139 s")
print("\nRunning IK; this may take a little while...")

try:
    result = ik.run()
    print("\nIK tool returned:", result)
except Exception:
    with log_path.open("w", encoding="utf-8") as f:
        f.write(traceback.format_exc())
    print("\nIK FAILED. Traceback saved to:", log_path)
    raise

if motion_path.exists():
    print("\nSUCCESS: motion file created.")
    print("File size:", motion_path.stat().st_size, "bytes")
    with motion_path.open("r", encoding="utf-8", errors="replace") as f:
        for line in f:
            if line.strip() and not line.lstrip().startswith("#"):
                print("First data/header line:", line.strip()[:220])
                break
else:
    print("\nWARNING: IK returned but the expected motion file was not found.")
    print("Inspect the OpenSim console messages and output folder.")

print("Results folder:", out_dir)
print("Run log:", log_path)
