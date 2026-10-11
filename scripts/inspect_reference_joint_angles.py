from pathlib import Path
import csv
import io
import zipfile

project = Path.home() / "Documents" / "OpenBiomechanics-OpenSim"
zip_path = project / "openbiomechanics" / "baseball_pitching" / "data" / "full_sig" / "joint_angles.zip"

with zipfile.ZipFile(zip_path) as z:
    with z.open("joint_angles.csv") as raw:
        stream = io.TextIOWrapper(raw, encoding="utf-8-sig", newline="")
        reader = csv.DictReader(stream)

        print("=== COLUMN NAMES ===")
        print(reader.fieldnames)

        print("\n=== FIRST THREE ROWS ===")
        for i, row in enumerate(reader):
            print(row)
            if i == 2:
                break

    print("\n=== SEARCH FOR SESSION 3034 ===")
    with z.open("joint_angles.csv") as raw:
        stream = io.TextIOWrapper(raw, encoding="utf-8-sig", newline="")
        reader = csv.DictReader(stream)
        matches = []
        count = 0

        for row in reader:
            # Search identifier fields first; fall back to all fields.
            identifiers = [
                str(value) for key, value in row.items()
                if key and any(token in key.lower()
                               for token in ("session", "pitch", "trial"))
            ]
            if any("3034" in value for value in identifiers):
                count += 1
                if len(matches) < 5:
                    matches.append(row)

        print("Matching rows:", count)
        for row in matches:
            print(row)
