from pathlib import Path
import json
import platform
import sys

import numpy as np
import opensim as osim

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "synthetic_data"
OUTPUTS = ROOT / "outputs"
DATA.mkdir(exist_ok=True)
OUTPUTS.mkdir(exist_ok=True)

trc_path = DATA / "synthetic_markers.trc"

# Five frames, three synthetic markers, coordinates in millimeters.
frames = [
    (1, 0.00, (0, 0, 0),    (100, 0, 0),   (0, 100, 0)),
    (2, 0.01, (1, 0, 0),    (101, 1, 0),   (0, 100, 1)),
    (3, 0.02, (2, 1, 0),    (102, 2, 1),   (0, 101, 2)),
    (4, 0.03, (3, 1, 1),    (103, 3, 2),   (1, 102, 3)),
    (5, 0.04, (4, 2, 1),    (104, 4, 3),   (1, 103, 4)),
]

with trc_path.open("w", newline="\n") as f:
    f.write("PathFileType\t4\t(X/Y/Z)\tsynthetic_markers.trc\n")
    f.write(
        "DataRate\tCameraRate\tNumFrames\tNumMarkers\tUnits\t"
        "OrigDataRate\tOrigDataStartFrame\tOrigNumFrames\n"
    )
    f.write("100.00\t100.00\t5\t3\tmm\t100.00\t1\t5\n")
    f.write("Frame#\tTime\tMarker1\t\t\tMarker2\t\t\tMarker3\n")
    f.write("\t\tX1\tY1\tZ1\tX2\tY2\tZ2\tX3\tY3\tZ3\n")

    for frame, time, m1, m2, m3 in frames:
        values = [frame, f"{time:.5f}"]
        for marker in (m1, m2, m3):
            values.extend(f"{coordinate:.3f}" for coordinate in marker)
        f.write("\t".join(map(str, values)) + "\n")

# Load the generated TRC through OpenSim's data-table API.
table = osim.TimeSeriesTableVec3(str(trc_path))

result = {
    "python_version": sys.version,
    "platform": platform.platform(),
    "opensim_version": osim.GetVersionAndDate(),
    "numpy_version": np.__version__,
    "trc_file": str(trc_path),
    "rows_loaded": table.getNumRows(),
    "columns_loaded": table.getNumColumns(),
    "time_range_seconds": [
        float(table.getIndependentColumn()[0]),
        float(table.getIndependentColumn()[-1]),
    ],
    "marker_labels": list(table.getColumnLabels()),
}

assert result["rows_loaded"] == 5, result
assert result["columns_loaded"] == 3, result
assert result["marker_labels"] == ["Marker1", "Marker2", "Marker3"], result

report_path = OUTPUTS / "synthetic_smoke_test.json"
report_path.write_text(json.dumps(result, indent=2), encoding="utf-8")

print("PASS: OpenSim loaded the synthetic marker file.")
print(json.dumps(result, indent=2))
print(f"\nReport saved to: {report_path}")
