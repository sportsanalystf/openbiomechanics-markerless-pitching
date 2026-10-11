from pathlib import Path
import opensim as osim

project = Path(__file__).resolve().parents[1]
model_path = project / "models" / "arm26.osim"
trc_path = project / "synthetic_data" / "synthetic_arm_motion.trc"
motion_path = project / "outputs" / "synthetic_arm_ik.mot"

for path in (model_path, trc_path):
    if not path.exists():
        raise FileNotFoundError(f"Required file not found: {path}")

model = osim.Model(str(model_path))

tool = osim.InverseKinematicsTool()
tool.setName("synthetic_arm_ik")
tool.setModel(model)
tool.setMarkerDataFileName(str(trc_path))
tool.setOutputMotionFileName(str(motion_path))
tool.setStartTime(0.0)
tool.setEndTime(1.0)

print("Running OpenSim inverse kinematics...")
success = tool.run()

print("Tool return value:", success)
print("Motion file exists:", motion_path.exists())

if motion_path.exists():
    print("Motion file size:", motion_path.stat().st_size, "bytes")
    print("Motion file:", motion_path)
else:
    raise RuntimeError(
        "OpenSim did not create the expected motion file. "
        "Check the OpenSim log output above."
    )
