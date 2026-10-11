from pathlib import Path
import opensim

project = Path.home() / "Documents" / "OpenBiomechanics-OpenSim"
model_path = project / "models" / "RajagopalLaiUhlrich2023.osim"

model = opensim.Model(str(model_path))
model.initSystem()

markers = model.getMarkerSet()
joints = model.getJointSet()
coordinates = model.getCoordinateSet()

print("\n=== MODEL SUMMARY ===")
print("Model:", model.getName())
print("Bodies:", model.getBodySet().getSize())
print("Markers:", markers.getSize())
print("Joints:", joints.getSize())
print("Coordinates:", coordinates.getSize())

print("\n=== MODEL MARKERS ===")
for i in range(markers.getSize()):
    marker = markers.get(i)
    location = marker.get_location()
    print(
        f"{marker.getName():30s} "
        f"body={marker.getParentFrame().getName():25s} "
        f"location=({location.get(0): .4f}, "
        f"{location.get(1): .4f}, {location.get(2): .4f})"
    )

print("\n=== JOINTS ===")
for i in range(joints.getSize()):
    print(joints.get(i).getName())

print("\n=== COORDINATES ===")
for i in range(coordinates.getSize()):
    coordinate = coordinates.get(i)
    print(
        f"{coordinate.getName():35s} "
        f"default={coordinate.getDefaultValue(): .4f} "
        f"range=({coordinate.getRangeMin(): .4f}, "
        f"{coordinate.getRangeMax(): .4f})"
    )
