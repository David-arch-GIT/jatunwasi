import json
import math
import os
import random
import unreal

random.seed(2206)
subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
plaza = next((a for a in subsystem.get_all_level_actors() if a.get_actor_label() == "JW_ENV_Plaza"), None)
if not plaza:
    raise RuntimeError("JW_ENV_Plaza not found")
components = plaza.get_components_by_class(unreal.HierarchicalInstancedStaticMeshComponent)
if len(components) != 3:
    raise RuntimeError("JW_ENV_Plaza must retain exactly three HISM components")

mesh_data = []
for comp in components:
    mesh = comp.get_editor_property("static_mesh")
    if not mesh:
        raise RuntimeError("Plaza HISM missing mesh")
    bb = mesh.get_bounding_box()
    mesh_data.append({
        "component": comp,
        "mesh": mesh.get_path_name(),
        "half_x": mesh.get_bounds().box_extent.x,
        "half_y": mesh.get_bounds().box_extent.y,
        "min_z": bb.min.z,
    })

before = sum(c.get_instance_count() for c in components)
for comp in components:
    comp.clear_instances()

CX, CY = 0.0, -1000.0
OUT_X0, OUT_X1 = -1600.0, 1600.0
OUT_Y0, OUT_Y1 = -2500.0, 500.0
HOLE_X0, HOLE_X1 = -700.0, 700.0
HOLE_Y0, HOLE_Y1 = -1700.0, -300.0
GROUND_TOP = -5.0

def corridor(x, y):
    # Keep the five existing path entrances open from the 14 m square center.
    if y < HOLE_Y0 and abs(x) < 330.0:  # Entrada
        return True
    if x < HOLE_X0 and abs(y - CY) < 330.0:  # Hacienda
        return True
    if x > HOLE_X1 and abs(y - CY) < 330.0:  # Salon/east path
        return True
    if y > HOLE_Y1 and abs(x) < 330.0:  # Mirador
        return True
    # Plaza -> Convento diagonal, approximately 45 degrees NE.
    if x > 450.0 and y > -550.0 and abs((y - CY) - x) < 430.0:
        return True
    return False

def add_piece(x, y, index):
    data = mesh_data[index % len(mesh_data)]
    scale = [0.98, 0.99, 1.0, 1.01, 1.02][index % 5]
    yaw = (0.0 if (index // 3) % 2 == 0 else 180.0) + random.uniform(-2.5, 2.5)
    z = GROUND_TOP - data["min_z"] * scale
    transform = unreal.Transform(
        location=unreal.Vector(x, y, z),
        rotation=unreal.Rotator(pitch=0.0, yaw=yaw, roll=0.0),
        scale=unreal.Vector(scale, scale, scale),
    )
    data["component"].add_instance_world_space(transform)

positions = []
# 90-95% spacing based on real mesh sizes: nominal footprint ~285 x 476 cm.
dx = 262.0
dy = 438.0

# North and south bands, two staggered rows each.
xs = [-1440.0 + i * dx for i in range(12)]
for band_ys in ((-62.0, 365.0), (-1935.0, -2362.0)):
    for row, y in enumerate(band_ys):
        for col, x in enumerate(xs):
            xx = x + (dx * 0.5 if row % 2 else 0.0)
            if xx > 1470.0 or corridor(xx, y):
                continue
            positions.append((xx, y))

# West and east side bands between the north/south bands.
side_xs = (-1455.0, -1193.0, -931.0, 931.0, 1193.0, 1455.0)
side_ys = (-1465.0, -1027.0, -589.0)
for row, y in enumerate(side_ys):
    for x in side_xs:
        yy = y + (18.0 if (int(abs(x)) // 200) % 2 else 0.0)
        if corridor(x, yy):
            continue
        positions.append((x, yy))

for i, (x, y) in enumerate(positions):
    add_piece(x, y, i)

after = sum(c.get_instance_count() for c in components)
if before not in (126, 43):
    raise RuntimeError("Unexpected starting plaza count: %d" % before)
if after != len(positions):
    raise RuntimeError("Plaza add count mismatch")

# The nominal spacing overlaps the smallest mesh footprint, so mathematical gap is zero.
min_width = min(d["half_x"] * 2.0 * 0.98 for d in mesh_data)
min_length = min(d["half_y"] * 2.0 * 0.98 for d in mesh_data)
max_gap = max(0.0, dx - min_width, dy - min_length)
report = {
    "cleared_instances": before,
    "instances_final": after,
    "mesh_bounds": [{k: v for k, v in d.items() if k not in ("component", "min_z")} for d in mesh_data],
    "outer_size_cm": [3200, 3000],
    "center_clear_cm": [1400, 1400],
    "spacing_cm": [dx, dy],
    "spacing_percent": [dx / min_width * 98.0, dy / min_length * 98.0],
    "max_plaza_gap_cm": max_gap,
    "coverage_valid": max_gap <= 10.0,
}
out = os.path.join(unreal.Paths.project_saved_dir(), "MCP_Captures", "Environment_V2", "phase_c_plaza.json")
with open(out, "w", encoding="utf-8") as f:
    json.dump(report, f, indent=2)
unreal.log("ENV_V2_PHASE_C_READY=" + json.dumps(report))
