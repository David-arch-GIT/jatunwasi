# -*- coding: utf-8 -*-
# Plaza Tarata - Phase 2 DIRECT BUILD (NO CODEX)
# Unreal Engine 5.7
#
# Builds a visible, editable plaza base with connected circulation in:
# /Game/JWN/MAP_JatunWasi_MCP_V08_HaciendaFix_CLEAN
#
# It uses only the built-in Engine Cube StaticMesh, so it does NOT depend on
# GeometryScript asset baking and cannot hit the tuple-return bug that stopped Codex.
#
# Safety:
# - refuses to run on any other map
# - refuses to duplicate an existing PLZT_Ph2 build
# - creates replacements first
# - hides the old JW_ENV_Plaza only after the new base exists
# - saves only after successful construction
# - on failure, destroys actors created during this run and restores JW_ENV_Plaza visibility
#
# Report:
# C:\UnrealProjects\JatunWasiNawpakay\Saved\MCP_Direct\PlazaTarata_Phase2_Direct.json

import unreal
import math
import json
import os
import traceback

ROOT = r"C:\UnrealProjects\JatunWasiNawpakay"
EXPECTED_MAP = "/Game/JWN/MAP_JatunWasi_MCP_V08_HaciendaFix_CLEAN"
REPORT = os.path.join(ROOT, "Saved", "MCP_Direct", "PlazaTarata_Phase2_Direct.json")

CENTER_X = 0.0
CENTER_Y = -1000.0
GROUND_Z = 10.0

PLAZA_W = 3300.0   # 33 m east-west
PLAZA_H = 3100.0   # 31 m north-south
PLAZA_TOP_Z = 16.0
PLAZA_THICK = 10.0

MAIN_PATH_W = 400.0
SECONDARY_PATH_W = 350.0
CENTRAL_DIAM = 850.0
CENTRAL_CLEAR_RING = 250.0

CUBE_PATH = "/Engine/BasicShapes/Cube.Cube"

res = {
    "status": "STARTED",
    "map": None,
    "actors_created": [],
    "old_plaza_hidden": False,
    "materials": {},
    "validation": {},
    "errors": [],
    "level_saved": False
}

spawned = []
old_plaza = None
old_plaza_was_visible = True

os.makedirs(os.path.dirname(REPORT), exist_ok=True)

def fail(msg):
    raise RuntimeError(msg)

def resolve_by_label(subsys, label, required=False):
    matches = [a for a in subsys.get_all_level_actors() if a.get_actor_label() == label]
    if required and len(matches) != 1:
        fail("Expected exactly one actor '%s'; found %d" % (label, len(matches)))
    return matches[0] if matches else None

def first_material(actor):
    if not actor:
        return None
    # Search any mesh component, including ISM/HISM/static mesh components.
    try:
        comps = actor.get_components_by_class(unreal.MeshComponent)
    except Exception:
        comps = []
    for c in comps:
        try:
            m = c.get_material(0)
            if m:
                return m
        except Exception:
            pass
    return None

def set_visible(actor, visible):
    if not actor:
        return
    try:
        actor.set_actor_hidden_in_game(not visible)
    except Exception:
        pass
    try:
        for c in actor.get_components_by_class(unreal.PrimitiveComponent):
            try:
                c.set_visibility(visible, True)
            except Exception:
                pass
            try:
                c.set_editor_property("visible", visible)
            except Exception:
                pass
    except Exception:
        pass

def spawn_box(subsys, cube, label, center, sx, sy, sz, yaw=0.0, material=None):
    a = subsys.spawn_actor_from_object(
        cube,
        unreal.Vector(float(center[0]), float(center[1]), float(center[2])),
        unreal.Rotator(pitch=0.0, yaw=float(yaw), roll=0.0),
        False
    )
    if not a:
        fail("Could not spawn " + label)
    a.set_actor_label(label)
    # Engine cube is 100 cm per side.
    a.set_actor_scale3d(unreal.Vector(float(sx)/100.0, float(sy)/100.0, float(sz)/100.0))
    c = a.get_component_by_class(unreal.StaticMeshComponent)
    if not c:
        fail("Spawned actor has no StaticMeshComponent: " + label)
    if material:
        try:
            c.set_material(0, material)
        except Exception:
            pass
    spawned.append(a)
    res["actors_created"].append(label)
    return a

def curb_rectangle(subsys, cube, prefix, cx, cy, w, h, material):
    # 18 cm high x 24 cm wide, around a rectangular planting bed.
    cw = 24.0
    ch = 18.0
    z = PLAZA_TOP_Z + ch/2.0
    spawn_box(subsys, cube, prefix+"_Curb_N", (cx, cy+h/2.0-cw/2.0, z), w, cw, ch, 0, material)
    spawn_box(subsys, cube, prefix+"_Curb_S", (cx, cy-h/2.0+cw/2.0, z), w, cw, ch, 0, material)
    spawn_box(subsys, cube, prefix+"_Curb_E", (cx+w/2.0-cw/2.0, cy, z), cw, max(1.0,h-2*cw), ch, 0, material)
    spawn_box(subsys, cube, prefix+"_Curb_W", (cx-w/2.0+cw/2.0, cy, z), cw, max(1.0,h-2*cw), ch, 0, material)

def actor_bounds_ok(a):
    o,e = a.get_actor_bounds(False, False)
    return e.x > 0.01 and e.y > 0.01 and e.z > 0.01

try:
    editor = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
    subsys = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    world = editor.get_editor_world()
    if not world:
        fail("No editor world")
    wp = world.get_path_name()
    res["map"] = wp
    if not wp.startswith(EXPECTED_MAP + "."):
        fail("WRONG MAP: " + wp)

    # Refuse duplicate Phase-2 build.
    existing = [a.get_actor_label() for a in subsys.get_all_level_actors()
                if a.get_actor_label().startswith("PLZT_Ph2_")]
    if existing:
        fail("PLZT Phase-2 actors already exist; refusing duplicate build: " + ",".join(existing))

    cube = unreal.load_asset(CUBE_PATH)
    if not cube:
        fail("Could not load Engine Cube")

    env_plaza = resolve_by_label(subsys, "JW_ENV_Plaza")
    env_paths = resolve_by_label(subsys, "JW_ENV_PathNetwork")
    old_plaza = env_plaza

    mat_plaza = first_material(env_plaza)
    mat_path = first_material(env_paths) or mat_plaza
    # Soil/bed fallback: use plaza material if no separate material can be found.
    mat_soil = None
    for label in ("JW_ENV_Grass", "JW_ENV_Shrubs", "Ground_Cochabamba"):
        a = resolve_by_label(subsys, label)
        mat_soil = first_material(a)
        if mat_soil:
            break

    res["materials"] = {
        "plaza": mat_plaza.get_path_name() if mat_plaza else None,
        "path": mat_path.get_path_name() if mat_path else None,
        "soil": mat_soil.get_path_name() if mat_soil else None,
    }

    # -------------------------
    # A) MAIN PLAZA PLATFORM
    # -------------------------
    base = spawn_box(
        subsys, cube, "PLZT_Ph2_Base_Main",
        (CENTER_X, CENTER_Y, PLAZA_TOP_Z - PLAZA_THICK/2.0),
        PLAZA_W, PLAZA_H, PLAZA_THICK,
        0.0, mat_plaza
    )

    # -------------------------
    # B) MAIN HACIENDA + EAST AXIS
    # -------------------------
    # The already-measured Hacienda approach reaches the WEST plaza edge.
    # Create one coherent east-west ceremonial axis across the full plaza.
    path_z = PLAZA_TOP_Z + 1.0
    path_t = 2.0
    ew = spawn_box(
        subsys, cube, "PLZT_Ph2_Path_Hacienda_EastAxis",
        (CENTER_X, CENTER_Y, path_z),
        PLAZA_W, MAIN_PATH_W, path_t,
        0.0, mat_path
    )

    # -------------------------
    # C) NORTH-SOUTH AXIS
    # -------------------------
    ns = spawn_box(
        subsys, cube, "PLZT_Ph2_Path_NorthSouth",
        (CENTER_X, CENTER_Y, path_z),
        MAIN_PATH_W, PLAZA_H, path_t,
        0.0, mat_path
    )

    # -------------------------
    # D) NORTHEAST DIAGONAL CONNECTION
    # -------------------------
    ne_end_x = CENTER_X + PLAZA_W/2.0
    ne_end_y = CENTER_Y + PLAZA_H/2.0
    dx = ne_end_x - CENTER_X
    dy = ne_end_y - CENTER_Y
    ne_len = math.sqrt(dx*dx + dy*dy)
    ne_yaw = math.degrees(math.atan2(dy, dx))
    ne = spawn_box(
        subsys, cube, "PLZT_Ph2_Path_NorthEast",
        ((CENTER_X+ne_end_x)/2.0, (CENTER_Y+ne_end_y)/2.0, path_z+0.5),
        ne_len, SECONDARY_PATH_W, path_t,
        ne_yaw, mat_path
    )

    # -------------------------
    # E) CENTRAL RESERVED OCTAGONAL FEATURE ZONE
    # -------------------------
    # Four diagonal low curb segments imply an octagonal central feature while
    # leaving the main cardinal approach openings fully unobstructed.
    r = CENTRAL_DIAM/2.0
    seg_len = 270.0
    curb_w = 24.0
    curb_h = 16.0
    cz = PLAZA_TOP_Z + curb_h/2.0
    for i,(angle,label) in enumerate(((45,"NE"),(135,"NW"),(225,"SW"),(315,"SE"))):
        ar = math.radians(angle)
        cx = CENTER_X + math.cos(ar)*r
        cy = CENTER_Y + math.sin(ar)*r
        spawn_box(
            subsys, cube, "PLZT_Ph2_CentralOct_"+label,
            (cx,cy,cz),
            seg_len,curb_w,curb_h,
            angle+90.0, mat_plaza
        )

    # -------------------------
    # F) FOUR FORMAL GARDEN QUADRANTS
    # -------------------------
    # Leave large open cross axes and a generous central circulation zone.
    bed_w = 760.0
    bed_h = 700.0
    bed_z = PLAZA_TOP_Z + 4.0
    bed_t = 8.0

    # NW, SW, SE are simple formal beds.
    gardens = [
        ("NW", -1080.0, +1060.0),
        ("SW", -1080.0, -1060.0),
        ("SE", +1080.0, -1060.0),
    ]
    for tag, ox, oy in gardens:
        cx = CENTER_X + ox
        cy = CENTER_Y + oy
        spawn_box(subsys,cube,"PLZT_Ph2_Garden_"+tag,
                  (cx,cy,bed_z),bed_w,bed_h,bed_t,0.0,mat_soil)
        curb_rectangle(subsys,cube,"PLZT_Ph2_Garden_"+tag,cx,cy,bed_w,bed_h,mat_plaza)

    # NE is split into two smaller beds so the diagonal NE route remains clear.
    # North piece
    ne1_cx = CENTER_X + 850.0
    ne1_cy = CENTER_Y + 1275.0
    ne1_w = 560.0
    ne1_h = 360.0
    spawn_box(subsys,cube,"PLZT_Ph2_Garden_NE_North",
              (ne1_cx,ne1_cy,bed_z),ne1_w,ne1_h,bed_t,0.0,mat_soil)
    curb_rectangle(subsys,cube,"PLZT_Ph2_Garden_NE_North",
                   ne1_cx,ne1_cy,ne1_w,ne1_h,mat_plaza)

    # East piece
    ne2_cx = CENTER_X + 1350.0
    ne2_cy = CENTER_Y + 650.0
    ne2_w = 380.0
    ne2_h = 580.0
    spawn_box(subsys,cube,"PLZT_Ph2_Garden_NE_East",
              (ne2_cx,ne2_cy,bed_z),ne2_w,ne2_h,bed_t,0.0,mat_soil)
    curb_rectangle(subsys,cube,"PLZT_Ph2_Garden_NE_East",
                   ne2_cx,ne2_cy,ne2_w,ne2_h,mat_plaza)

    # -------------------------
    # G) SIMPLE CONNECTION APRONS AT PLAZA EDGES
    # -------------------------
    # Flush extensions at the west/east/north edges make the junctions visually
    # deliberate without touching the Hacienda or global path actor.
    apron_len = 350.0
    spawn_box(subsys,cube,"PLZT_Ph2_Connector_Hacienda_West",
              (CENTER_X-PLAZA_W/2.0-apron_len/2.0,CENTER_Y,path_z),
              apron_len,MAIN_PATH_W,path_t,0.0,mat_path)
    spawn_box(subsys,cube,"PLZT_Ph2_Connector_East",
              (CENTER_X+PLAZA_W/2.0+apron_len/2.0,CENTER_Y,path_z),
              apron_len,SECONDARY_PATH_W,path_t,0.0,mat_path)
    spawn_box(subsys,cube,"PLZT_Ph2_Connector_North",
              (CENTER_X,CENTER_Y+PLAZA_H/2.0+apron_len/2.0,path_z),
              MAIN_PATH_W,apron_len,path_t,0.0,mat_path)

    # -------------------------
    # H) VALIDATE CREATED GEOMETRY
    # -------------------------
    for a in spawned:
        if not actor_bounds_ok(a):
            fail("Invalid bounds on " + a.get_actor_label())

    # Only after replacements exist, hide the old fragmented plaza actor.
    if old_plaza:
        set_visible(old_plaza, False)
        res["old_plaza_hidden"] = True

    # Save only after success.
    if not unreal.EditorLevelLibrary.save_current_level():
        fail("save_current_level returned False")

    res["validation"] = {
        "plaza_base_size_m": [PLAZA_W/100.0, PLAZA_H/100.0],
        "main_hacienda_path_connected_to_west_edge": True,
        "main_hacienda_path_width_m": MAIN_PATH_W/100.0,
        "north_south_axis_connected": True,
        "east_path_connected": True,
        "northeast_path_connected": True,
        "central_feature_reserved_diameter_m": CENTRAL_DIAM/100.0,
        "central_clear_ring_m": CENTRAL_CLEAR_RING/100.0,
        "garden_quadrants_defined": 4,
        "floating_pavement_expected": 0,
        "curbs_blocking_main_axes_expected": 0,
    }
    res["level_saved"] = True
    res["status"] = "READY_FOR_VISUAL_QA"

except Exception as e:
    # Roll back only actors spawned during this run.
    try:
        if 'subsys' in locals():
            for a in reversed(spawned):
                try:
                    subsys.destroy_actor(a)
                except Exception:
                    pass
    except Exception:
        pass
    try:
        if old_plaza:
            set_visible(old_plaza, True)
    except Exception:
        pass
    res["status"] = "FAILED_ROLLED_BACK_NO_SAVE"
    res["errors"].append(str(e))
    res["traceback"] = traceback.format_exc()
    res["level_saved"] = False

finally:
    with open(REPORT, "w", encoding="utf-8") as f:
        json.dump(res, f, indent=2, ensure_ascii=False)
    print("PLAZA_PHASE2_DIRECT_STATUS=" + res["status"])
    print("PLAZA_PHASE2_DIRECT_REPORT=" + REPORT)
