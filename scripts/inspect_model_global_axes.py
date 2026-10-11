from pathlib import Path
import opensim

project = Path.home() / "Documents" / "OpenBiomechanics-OpenSim"
model_path = project / "models" / "RajagopalLaiUhlrich2023.osim"

model = opensim.Model(str(model_path))
state = model.initSystem()

print("MODEL:", model_path.name)
print("\n=== SELECTED MARKER POSITIONS IN GROUND FRAME ===")

marker_set = model.getMarkerSet()
selected = {
    "C7", "CLAV", "LASI", "RASI", "LPSI", "RPSI",
    "LTOE", "RTOE", "LHJC", "RHJC", "RACR", "LACR"
}

for i in range(marker_set.getSize()):
    marker = marker_set.get(i)
    name = marker.getName()
    if name in selected:
        pos = marker.getLocationInGround(state)
        print(
            f"{name:6s} "
            f"x={pos.get(0): .4f} "
            f"y={pos.get(1): .4f} "
            f"z={pos.get(2): .4f}"
        )

print("\n=== SELECTED BODY ORIGINS IN GROUND FRAME ===")
for name in ["pelvis", "torso", "humerus_r", "femur_r", "calcn_r"]:
    try:
        body = model.getBodySet().get(name)
        pos = body.getPositionInGround(state)
        print(
            f"{name:12s} "
            f"x={pos.get(0): .4f} "
            f"y={pos.get(1): .4f} "
            f"z={pos.get(2): .4f}"
        )
    except Exception as exc:
        print(f"{name}: unavailable ({exc})")
