from pathlib import Path
import csv
import numpy as np
import ezc3d

project = Path.home() / "Documents" / "OpenBiomechanics-OpenSim"
c3d_path = project / "openbiomechanics" / "baseball_pitching" / "data" / "c3d" / "000002" / "000002_003034_73_207_002_FF_809.c3d"
out = project / "outputs"
mapping_path = out / "measured_to_model_marker_mapping.csv"
trc_path = out / "pitch_3034_1_mapped.trc"

with mapping_path.open(newline="", encoding="utf-8-sig") as f:
    mapping = list(csv.DictReader(f))

c3d = ezc3d.c3d(str(c3d_path))
labels = [str(x).strip() for x in c3d["parameters"]["POINT"]["LABELS"]["value"]]
index = {name: i for i, name in enumerate(labels)}
points = np.asarray(c3d["data"]["points"], dtype=float)
rate = float(c3d["header"]["points"]["frame_rate"])
xyz = points[:3, :, :].transpose(2, 1, 0)

# Laboratory Z-up to OpenSim model Y-up.
xyz = xyz[:, :, [0, 2, 1]]
xyz[:, :, 2] *= -1

usable = [m for m in mapping if m["measured_marker"] in index]
n_frames = xyz.shape[0]
n_markers = len(usable)

with trc_path.open("w", newline="", encoding="utf-8") as f:
    f.write(f"PathFileType\t4\t(X/Y/Z)\t{trc_path.name}\n")
    f.write("DataRate\tCameraRate\tNumFrames\tNumMarkers\tUnits\tOrigDataRate\tOrigDataStartFrame\tOrigNumFrames\n")
    f.write(f"{rate:g}\t{rate:g}\t{n_frames}\t{n_markers}\tm\t{rate:g}\t1\t{n_frames}\n")

    # Marker names occupy the first column of each XYZ triplet.
    marker_header = ["Frame#", "Time"]
    for m in usable:
        marker_header.extend([m["model_marker"], "", ""])
    f.write("\t".join(marker_header) + "\n")

    # Coordinate labels must be sequential for every marker.
    coordinate_header = ["", ""]
    for i in range(1, n_markers + 1):
        coordinate_header.extend([f"X{i}", f"Y{i}", f"Z{i}"])
    f.write("\t".join(coordinate_header) + "\n")

    for frame in range(n_frames):
        fields = [str(frame + 1), f"{frame / rate:.8f}"]
        for m in usable:
            p = xyz[frame, index[m["measured_marker"]], :]
            if not np.isfinite(p).all():
                fields.extend(["", "", ""])
            else:
                fields.extend([f"{v:.8f}" for v in p])
        f.write("\t".join(fields) + "\n")

print("Rebuilt TRC:", trc_path)
print("Frames:", n_frames)
print("Markers:", n_markers)
print("Coordinate columns:", n_markers * 3)
print("First two header lines:")
with trc_path.open(encoding="utf-8") as f:
    for _ in range(4):
        print(repr(f.readline().rstrip("\n")))
