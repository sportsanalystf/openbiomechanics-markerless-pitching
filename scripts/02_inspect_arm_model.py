from pathlib import Path
import json
import opensim as osim

project = Path.home() / "Documents" / "OpenBiomechanics-OpenSim"
model_path = project / "models" / "arm26.osim"

model = osim.Model(str(model_path))
state = model.initSystem()
model.realizePosition(state)

markers = []
for i in range(model.getMarkerSet().getSize()):
    marker = model.getMarkerSet().get(i)
    p = marker.getLocationInGround(state)
    markers.append({
        "name": marker.getName(),
        "location_in_ground_m": [p.get(0), p.get(1), p.get(2)]
    })

coordinates = []
for i in range(model.getCoordinateSet().getSize()):
    coord = model.getCoordinateSet().get(i)
    coordinates.append({
        "name": coord.getName(),
        "default_value": coord.getDefaultValue(),
        "range_min": coord.getRangeMin(),
        "range_max": coord.getRangeMax(),
        "motion_type": str(coord.getMotionType())
    })

report = {
    "model": str(model_path),
    "body_count": model.getBodySet().getSize(),
    "coordinate_count": len(coordinates),
    "markers": markers,
    "coordinates": coordinates
}

output = project / "outputs" / "arm26_model_inspection.json"
output.write_text(json.dumps(report, indent=2), encoding="utf-8")

print(json.dumps(report, indent=2))
print(f"\nReport saved to: {output}")
