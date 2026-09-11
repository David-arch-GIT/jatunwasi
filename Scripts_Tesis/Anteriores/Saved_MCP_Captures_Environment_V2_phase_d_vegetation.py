import json
import math
import os
import random
import unreal

random.seed(5082026)
subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
actors = {a.get_actor_label(): a for a in subsystem.get_all_level_actors()}
labels = ("JW_ENV_Trees", "JW_ENV_Shrubs", "JW_ENV_Grass", "JW_ENV_Rocks")
targets = {"JW_ENV_Trees": 525, "JW_ENV_Shrubs": 1350, "JW_ENV_Grass": 3300, "JW_ENV_Rocks": 210}
for label in labels:
    if label not in actors:
        raise RuntimeError(label + " not found")

path_defs = [
    ([(0,-11000),(-300,-7500),(300,-4000),(0,-1000)],700),
    ([(0,-1000),(-2500,-1200),(-4800,-1800),(-7000,-2500)],675),
    ([(0,-1000),(2500,-1200),(4800,-1800),(7000,-2500)],675),
    ([(0,-1000),(1800,800),(4300,2600),(6500,5000)],675),
    ([(6500,5000),(6250,6800),(6700,8600),(6500,10500)],650),
    ([(0,-1000),(-500,3500),(400,7500),(-300,11500),(0,15500)],425),
]
rect_reserves = [(-7000,-2500,2750,2450),(6500,5000,2550,2250),(6500,10500,2100,1900),(7000,-2500,2200,1900)]
circle_reserves = [(0,-11000,1600),(0,-1000,2600),(0,15500,1800)]

def segdist(px, py, a, b):
    dx, dy = b[0]-a[0], b[1]-a[1]
    den = dx*dx + dy*dy
    t = max(0.0, min(1.0, ((px-a[0])*dx + (py-a[1])*dy)/den)) if den else 0.0
    return math.hypot(px-(a[0]+t*dx), py-(a[1]+t*dy))

def in_reserve(x, y, pad=0.0):
    for cx, cy, radius in circle_reserves:
        if math.hypot(x-cx, y-cy) < radius + pad:
            return True
    for cx, cy, hx, hy in rect_reserves:
        if abs(x-cx) < hx + pad and abs(y-cy) < hy + pad:
            return True
    return False

def in_path(x, y, pad=0.0):
    for pts, radius in path_defs:
        for i in range(len(pts)-1):
            if segdist(x, y, pts[i], pts[i+1]) < radius + pad:
                return True
    return False

# Localized centers: route sides, plaza exterior, north forest, mirador, borders,
# and backgrounds behind future buildings. They intentionally do not cover the full terrain.
centers = [
    (-1900,-9000),(1900,-9000),(-1800,-6500),(1900,-6200),(-1900,-3900),(1900,-3600),
    (-3300,-500),(3300,-400),(-3200,-3200),(3200,-3300),(-4200,900),(4300,700),
    (-3200,-3600),(-5000,-4300),(-8500,-4700),(-3500,1200),(-6100,1300),
    (3200,1000),(5200,1700),(8500,3400),(9000,6500),(9400,9000),
    (-1800,3000),(1700,3300),(-1900,6100),(1800,6500),(-1700,9200),(1900,9600),
    (-4200,11800),(4300,12000),(-6500,15000),(6500,15000),(-9000,17500),(9500,18000),
    (-12500,10500),(-10000,13500),(11000,12500),(13500,15500),
    (-27000,-15000),(-26500,-5000),(-27000,6000),(-26000,16500),
    (27000,-15000),(26500,-5000),(27000,6000),(26000,16500),
    (-10500,-3000),(-9000,5000),(10500,8000),(10000,-6000),
]

def valid(x, y, kind):
    if not (-33000.0 < x < 33000.0 and -23000.0 < y < 23000.0):
        return False
    pad = 260.0 if kind == "tree" else (120.0 if kind in ("shrub", "rock") else 45.0)
    return not in_reserve(x, y, pad) and not in_path(x, y, pad)

def clustered_points(count, kind, group_min, group_max, radius_min, radius_max, min_spacing=0.0):
    points = []
    center_index = 0
    attempts = 0
    while len(points) < count and attempts < count * 100:
        cx, cy = centers[center_index % len(centers)]
        center_index += 1
        group_count = random.randint(group_min, group_max)
        radius = random.uniform(radius_min, radius_max)
        for _ in range(group_count):
            if len(points) >= count:
                break
            angle = random.random() * math.tau
            distance = radius * math.sqrt(random.random())
            x = cx + math.cos(angle) * distance
            y = cy + math.sin(angle) * distance
            attempts += 1
            if not valid(x, y, kind):
                continue
            if min_spacing and any((x-px)**2 + (y-py)**2 < min_spacing**2 for px, py in points[-160:]):
                continue
            points.append((x, y))
    if len(points) != count:
        raise RuntimeError("Could not generate %s target: %d/%d" % (kind, len(points), count))
    return points

point_sets = {
    "JW_ENV_Trees": clustered_points(525, "tree", 6, 16, 450, 1250, 330),
    "JW_ENV_Shrubs": clustered_points(1350, "shrub", 10, 28, 300, 1150, 90),
    "JW_ENV_Grass": clustered_points(3300, "grass", 24, 70, 220, 1000, 32),
    "JW_ENV_Rocks": clustered_points(210, "rock", 2, 6, 160, 600, 150),
}

component_info = {}
for label in labels:
    comps = actors[label].get_components_by_class(unreal.HierarchicalInstancedStaticMeshComponent)
    if not comps:
        raise RuntimeError(label + " has no HISM components")
    component_info[label] = []
    for comp in comps:
        mesh = comp.get_editor_property("static_mesh")
        if not mesh:
            raise RuntimeError(label + " HISM missing mesh")
        component_info[label].append((comp, mesh.get_bounding_box().min.z))
        comp.clear_instances()

scale_ranges = {
    "JW_ENV_Trees": (0.86, 1.12),
    "JW_ENV_Shrubs": (0.82, 1.18),
    "JW_ENV_Grass": (0.78, 1.22),
    "JW_ENV_Rocks": (0.72, 1.16),
}
for label, points in point_sets.items():
    infos = component_info[label]
    lo, hi = scale_ranges[label]
    for i, (x, y) in enumerate(points):
        comp, min_z = infos[i % len(infos)]
        scale = random.uniform(lo, hi)
        z = -5.0 - min_z * scale
        tr = unreal.Transform(
            location=unreal.Vector(x, y, z),
            rotation=unreal.Rotator(pitch=0.0, yaw=random.uniform(-180.0, 180.0), roll=0.0),
            scale=unreal.Vector(scale, scale, scale),
        )
        comp.add_instance_world_space(tr)

counts = {}
inside_reserves = inside_paths = inside_plaza = floating = buried = 0
for label in labels:
    total = 0
    for comp, min_z in component_info[label]:
        total += comp.get_instance_count()
        for i in range(comp.get_instance_count()):
            tr = comp.get_instance_transform(i, True)
            p, s = tr.translation, tr.scale3d
            inside_reserves += int(in_reserve(p.x, p.y))
            inside_paths += int(in_path(p.x, p.y))
            inside_plaza += int(math.hypot(p.x, p.y + 1000.0) < 2600.0)
            base = p.z + min_z * s.z
            floating += int(base > 10.0)
            buried += int(base < -30.0)
    counts[label] = total

if counts != targets:
    raise RuntimeError("Final vegetation counts mismatch: " + str(counts))
if any((inside_reserves, inside_paths, inside_plaza, floating, buried)):
    raise RuntimeError("Vegetation validation failed")

report = {
    "counts": counts,
    "instances_inside_reserves": inside_reserves,
    "instances_inside_paths": inside_paths,
    "instances_inside_plaza": inside_plaza,
    "floating_instances": floating,
    "buried_instances": buried,
    "localized_cluster_centers": len(centers),
}
out = os.path.join(unreal.Paths.project_saved_dir(), "MCP_Captures", "Environment_V2", "phase_d_vegetation.json")
with open(out, "w", encoding="utf-8") as f:
    json.dump(report, f, indent=2)
unreal.log("ENV_V2_PHASE_D_READY=" + json.dumps(report))
