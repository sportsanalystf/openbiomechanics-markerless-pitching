from pathlib import Path
import xml.etree.ElementTree as ET

project = Path.home() / "Documents" / "OpenBiomechanics-OpenSim"
model_path = project / "models" / "RajagopalLaiUhlrich2023.osim"

root = ET.parse(model_path).getroot()

def local_name(tag):
    return tag.rsplit("}", 1)[-1]

print("MODEL:", model_path.name)

for element in root.iter():
    if local_name(element.tag) == "gravity":
        print("GRAVITY:", element.text.strip() if element.text else "(empty)")

print("\n=== ROOT / PELVIS JOINT XML ===")
found = False

for element in root.iter():
    tag = local_name(element.tag)
    if not tag.endswith("Joint"):
        continue

    details = {}
    for child in element.iter():
        name = local_name(child.tag)
        if name in {
            "socket_parent_frame", "socket_child_frame",
            "location_in_parent", "orientation_in_parent",
            "location_in_child", "orientation_in_child",
            "coordinates"
        }:
            details[name] = child.text.strip() if child.text else ""

    name = element.attrib.get("name", "")
    joined = " ".join(details.values()).lower()

    if "pelvis" in name.lower() or "ground" in joined:
        found = True
        print(f"\nJOINT TYPE: {tag}")
        print("NAME:", name)
        for key, value in details.items():
            print(f"{key}: {value}")

if not found:
    print("No joint matched automatically. Showing joints connected to pelvis:")
    for element in root.iter():
        tag = local_name(element.tag)
        if not tag.endswith("Joint"):
            continue
        text = " ".join(
            (child.text or "").strip()
            for child in element.iter()
            if local_name(child.tag) in {
                "socket_parent_frame", "socket_child_frame"
            }
        )
        if "pelvis" in text.lower():
            print(tag, element.attrib.get("name", ""), text)
