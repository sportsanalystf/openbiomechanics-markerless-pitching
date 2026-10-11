from pathlib import Path
import ezc3d

project = Path.home() / "Documents" / "OpenBiomechanics-OpenSim"
data_dir = project / "openbiomechanics" / "baseball_pitching" / "data"
filename = "000002_003034_73_207_002_FF_809.c3d"

matches = list(data_dir.rglob(filename))
if len(matches) != 1:
    raise FileNotFoundError(
        f"Expected one {filename}; found {len(matches)}: {matches}"
    )

c3d_path = matches[0]
c3d = ezc3d.c3d(str(c3d_path))
labels = [str(x).strip() for x in c3d["parameters"]["POINT"]["LABELS"]["value"]]

output_path = project / "outputs" / "pitching_c3d_marker_labels.txt"
output_path.parent.mkdir(parents=True, exist_ok=True)
output_path.write_text("\n".join(labels) + "\n", encoding="utf-8")

print("C3D:", c3d_path)
print("Marker count:", len(labels))
print("Saved labels:", output_path)
print("Labels:", ", ".join(labels))
