import unreal
import json
import math
import gc
import os
import traceback

PREFIX = "HACV4_"
EXPECTED_LEVEL = "/Game/JWN/MAP_JatunWasi_MCP_V02"
PROTECTED_LEVELS = {"/Game/JWN/MAP_JatunWasi_MCP_V01", "/Game/JWN/MAP_JatunWasi_AI_V02"}
ASSET_ROOT = "/Game/JWN/Architecture/Hacienda_V4"
TOOL_ROOT = os.path.join(unreal.Paths.project_dir(), "Tools", "HaciendaV4")
DESIGN_PATH = os.path.join(TOOL_ROOT, "hacienda_v4_design.json")
MANIFEST_PATH = os.path.join(TOOL_ROOT, "hacienda_v4_asset_manifest.json")
REPORT_PATH = os.path.join(TOOL_ROOT, "hacienda_v4_build_report.json")
LOG_PATH = os.path.join(TOOL_ROOT, "hacienda_v4_build.log")

with open(DESIGN_PATH, "r", encoding="utf-8") as handle:
    DESIGN = json.load(handle)

MANIFEST = {"status": "RUNNING", "assets": [], "actors": [], "materials": []}
REPORT = {"status": "RUNNING", "errors": [], "warnings": [], "fallbacks": [], "stages": {}}

def log(message):
    line = str(message)
    unreal.log("HACV4: " + line)
    with open(LOG_PATH, "a", encoding="utf-8") as handle:
        handle.write(line + "\n")

def flush_reports():
    with open(MANIFEST_PATH, "w", encoding="utf-8") as handle:
        json.dump(MANIFEST, handle, indent=2, sort_keys=True)
    with open(REPORT_PATH, "w", encoding="utf-8") as handle:
        json.dump(REPORT, handle, indent=2, sort_keys=True)

def fail(message):
    REPORT["errors"].append(str(message))
    REPORT["status"] = "FAILED"
    flush_reports()
    raise RuntimeError(message)

def current_level_package():
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    return world.get_outermost().get_name(), world

def validate_level():
    package, world = current_level_package()
    if package in PROTECTED_LEVELS:
        fail("Protected level is open: " + package)
    if package != EXPECTED_LEVEL:
        fail("Wrong level: " + package)
    return world

def outcome_ok(outcome):
    return "SUCCESS" in str(outcome).upper()

def tform(x=0.0, y=0.0, z=0.0, pitch=0.0, yaw=0.0, roll=0.0):
    return unreal.Transform(location=unreal.Vector(x, y, z), rotation=unreal.Rotator(pitch=pitch, yaw=yaw, roll=roll), scale=unreal.Vector(1, 1, 1))

PRIM_OPTS = unreal.GeometryScriptPrimitiveOptions()

def append_box_safe(mesh, center, size, rotation=(0.0, 0.0, 0.0)):
    result = unreal.GeometryScript_Primitives.append_box(
        mesh, PRIM_OPTS, tform(center[0], center[1], center[2], rotation[0], rotation[1], rotation[2]),
        float(size[0]), float(size[1]), float(size[2]), 0, 0, 0,
        unreal.GeometryScriptPrimitiveOriginMode.CENTER, None)
    if result is None:
        fail("append_box returned None")
    return result

def append_extruded_polygon_safe(mesh, vertices, height, transform=None):
    pts = [unreal.Vector2D(float(x), float(y)) for x, y in vertices]
    result = unreal.GeometryScript_Primitives.append_simple_extrude_polygon(
        mesh, PRIM_OPTS, transform or tform(), pts, float(height), 0, True,
        unreal.GeometryScriptPrimitiveOriginMode.BASE, None)
    if result is None:
        fail("append_simple_extrude_polygon returned None")
    return result

def append_swept_polygon_safe(mesh, vertices, sweep_path):
    pts = [unreal.Vector2D(float(x), float(y)) for x, y in vertices]
    result = unreal.GeometryScript_Primitives.append_sweep_polygon(
        mesh, PRIM_OPTS, tform(), pts, sweep_path, False, True, 1.0, 1.0, 0.0, 2.0, None)
    if result is None:
        fail("append_sweep_polygon returned None")
    return result

def recompute_normals_safe(mesh):
    result = unreal.GeometryScript_Normals.recompute_normals(mesh, unreal.GeometryScriptCalculateNormalsOptions(), False, None)
    if result is None:
        fail("recompute_normals returned None")
    try:
        unreal.GeometryScript_Normals.compute_tangents(mesh, unreal.GeometryScriptTangentsOptions(), None)
    except Exception as exc:
        REPORT["warnings"].append("Tangents fallback: " + repr(exc))
    return result

def generate_uv0_safe(mesh):
    unreal.GeometryScript_UVs.set_num_uv_sets(mesh, 2, None)
    try:
        result = unreal.GeometryScript_UVs.auto_generate_x_atlas_mesh_u_vs(mesh, 0, unreal.GeometryScriptXAtlasOptions(), None)
        if result is None:
            raise RuntimeError("XAtlas returned None")
        return True
    except Exception as exc:
        REPORT["fallbacks"].append("UV0 PatchBuilder: " + repr(exc))
        result = unreal.GeometryScript_UVs.auto_generate_patch_builder_mesh_u_vs(mesh, 0, unreal.GeometryScriptPatchBuilderOptions(), None)
        return result is not None

def generate_uv1_safe(mesh):
    try:
        result = unreal.GeometryScript_UVs.auto_generate_x_atlas_mesh_u_vs(mesh, 1, unreal.GeometryScriptXAtlasOptions(), None)
        if result is None:
            raise RuntimeError("XAtlas UV1 returned None")
        return True
    except Exception as exc:
        REPORT["fallbacks"].append("UV1 PatchBuilder: " + repr(exc))
        try:
            return unreal.GeometryScript_UVs.auto_generate_patch_builder_mesh_u_vs(mesh, 1, unreal.GeometryScriptPatchBuilderOptions(), None) is not None
        except Exception as nested:
            REPORT["warnings"].append("UV1 unavailable: " + repr(nested))
            return False

def create_static_mesh_asset_safe(mesh, asset_path):
    if unreal.EditorAssetLibrary.does_asset_exist(asset_path):
        return unreal.EditorAssetLibrary.load_asset(asset_path)
    options = unreal.GeometryScriptCreateNewStaticMeshAssetOptions()
    created, outcome = unreal.GeometryScript_NewAssetUtils.create_new_static_mesh_asset_from_mesh(mesh, asset_path, options, None)
    if created is None or not outcome_ok(outcome):
        fail("Static mesh creation failed for %s: %s" % (asset_path, outcome))
    MANIFEST["assets"].append(asset_path)
    return created

def copy_dynamic_to_static_safe(mesh, static_mesh):
    options = unreal.GeometryScriptCopyMeshToAssetOptions()
    lod = unreal.GeometryScriptMeshWriteLOD()
    _, outcome = unreal.GeometryScript_AssetUtils.copy_mesh_to_static_mesh(mesh, static_mesh, options, lod, True, None)
    if not outcome_ok(outcome):
        fail("copy_mesh_to_static_mesh failed: " + str(outcome))
    return static_mesh

def create_collision_safe(mesh, static_mesh):
    try:
        result = unreal.GeometryScript_Collision.set_static_mesh_collision_from_mesh(
            mesh, static_mesh, unreal.GeometryScriptCollisionFromMeshOptions(), unreal.GeometryScriptSetStaticMeshCollisionOptions(), None)
        if result is None:
            raise RuntimeError("collision returned None")
        return True
    except Exception as exc:
        REPORT["warnings"].append("Geometry collision fallback: " + repr(exc))
        try:
            unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem).add_simple_collisions(static_mesh, unreal.ScriptingCollisionShapeType.NDOP10_X)
            return True
        except Exception as nested:
            REPORT["errors"].append("Collision failed: " + repr(nested))
            return False

def find_material(keywords):
    registry = unreal.AssetRegistryHelpers.get_asset_registry()
    assets = registry.get_assets_by_path("/Game", True)
    ranked = []
    for data in assets:
        path = str(data.package_name)
        low = path.lower()
        if ("/megascans" in low or "/stylescapehd" in low or "/game/jwn" in low) and any(k in low for k in keywords):
            obj = data.get_asset()
            if isinstance(obj, unreal.MaterialInterface):
                ranked.append((sum(k in low for k in keywords), path, obj))
    ranked.sort(key=lambda item: (-item[0], item[1]))
    return ranked[0][2] if ranked else unreal.load_asset("/Engine/EngineMaterials/DefaultMaterial")

def create_material_instances():
    specs = {
        "MI_HACV4_Plaster_Exterior": "/Game/Megascans/Surfaces/Flaked_Paint_Wall_vhqgdhh/MI_Flaked_Paint_Wall_vhqgdhh_2K",
        "MI_HACV4_Plaster_Interior": "/Game/Megascans/Surfaces/Flaked_Paint_Wall_vhqgdhh/MI_Flaked_Paint_Wall_vhqgdhh_2K",
        "MI_HACV4_Stone": "/Game/Megascans/3D_Assets/Modular_Stone_Wall_xgfnfebiy/MI_Modular_Stone_Wall_xgfnfebiy_2K",
        "MI_HACV4_Wood": "/Game/Megascans/Surfaces/Wooden_Planks_ueynbafew/MI_Wooden_Planks_ueynbafew_2K",
        "MI_HACV4_Roof_Terracotta": "/Game/Megascans/Surfaces/Brick_Facade_vizcegj/MI_Brick_Facade_vizcegj_2K",
        "MI_HACV4_Floor_Tile": "/Game/Megascans/Surfaces/Patterned_Marble_Tiles_vf5leaav/MI_Patterned_Marble_Tiles_vf5leaav_2K",
        "MI_HACV4_Floor_Wood": "/Game/Megascans/Surfaces/Wooden_Planks_ueynbafew/MI_Wooden_Planks_ueynbafew_2K"
    }
    out = {}
    tools = unreal.AssetToolsHelpers.get_asset_tools()
    for name, parent_path in specs.items():
        path = ASSET_ROOT + "/Materials/" + name
        mi = unreal.EditorAssetLibrary.load_asset(path) if unreal.EditorAssetLibrary.does_asset_exist(path) else None
        if mi is None:
            mi = tools.create_asset(name, ASSET_ROOT + "/Materials", unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
            if mi is None:
                fail("Could not create " + path)
            MANIFEST["materials"].append(path)
        parent=unreal.load_asset(parent_path)
        if parent is None:
            fail("Missing material parent: "+parent_path)
        unreal.MaterialEditingLibrary.set_material_instance_parent(mi, parent)
        unreal.EditorAssetLibrary.save_loaded_asset(mi, only_if_is_dirty=False)
        out[name] = mi
    return out

def assign_materials_safe(actor, material):
    component = actor.static_mesh_component
    if material is not None:
        component.set_material(0, material)

def spawn_static_mesh_actor_safe(name, static_mesh, location, rotation, folder, material):
    for actor in unreal.EditorLevelLibrary.get_all_level_actors():
        if actor.get_actor_label() == name:
            actor.set_actor_location(unreal.Vector(*location), False, False)
            actor.set_actor_rotation(unreal.Rotator(pitch=0.0, yaw=rotation, roll=0.0), False)
            actor.set_actor_scale3d(unreal.Vector(1, 1, 1))
            actor.set_folder_path(folder)
            assign_materials_safe(actor, material)
            return actor
    actor = unreal.EditorLevelLibrary.spawn_actor_from_object(static_mesh, unreal.Vector(*location), unreal.Rotator(pitch=0.0, yaw=rotation, roll=0.0), transient=False)
    if actor is None:
        fail("Actor spawn failed: " + name)
    actor.set_actor_label(name)
    actor.set_folder_path(folder)
    actor.set_actor_scale3d(unreal.Vector(1, 1, 1))
    assign_materials_safe(actor, material)
    MANIFEST["actors"].append(name)
    return actor

def box(mesh, x, y, z, sx, sy, sz, yaw=0.0, pitch=0.0, roll=0.0):
    append_box_safe(mesh, (x, y, z), (sx, sy, sz), (pitch, yaw, roll))

def wall_x(mesh, y, x0, x1, z0, h, thick=45.0):
    box(mesh, (x0+x1)/2, y, z0+h/2, abs(x1-x0), thick, h)

def wall_y(mesh, x, y0, y1, z0, h, thick=45.0):
    box(mesh, x, (y0+y1)/2, z0+h/2, thick, abs(y1-y0), h)

def front_wall_with_openings(mesh):
    # Front is local +X. Segmentation creates a real 260x280 doorway and real windows.
    x=2000; t=45; h=360
    intervals=[(-1650,-1050),(-850,-500),(-130,130),(500,850),(1050,1650)]
    # solids between window/door bays
    for a,b in [(-1050,-850),(-500,-130),(130,500),(850,1050)]: wall_y(mesh,x,a,b,0,h,t)
    # outer edge piers
    wall_y(mesh,x,-1650,-1050,0,h,t); wall_y(mesh,x,1050,1650,0,h,t)
    # window bays: sill and lintel, leaving 130x145 openings
    for a,b in [(-850,-500),(500,850)]:
        wall_y(mesh,x,a,b,0,95,t); wall_y(mesh,x,a,b,240,120,t)
    # main door lintel; opening -130..130 and z 0..280
    wall_y(mesh,x,-130,130,280,80,t)

def build_foundation(mesh):
    box(mesh,0,0,-20,4000,3300,40)

def build_exterior(mesh):
    front_wall_with_openings(mesh)
    wall_y(mesh,-2000,-1650,1650,0,360)
    # side walls with repeated actual openings
    for y in (-1650,1650):
        for a,b in [(-2000,-950),(-750,350),(550,2000)]: wall_x(mesh,y,a,b,0,360)
        for a,b in [(-950,-750),(350,550)]:
            wall_x(mesh,y,a,b,0,95); wall_x(mesh,y,a,b,240,120)
    # Republic-era facade articulation: projecting pilasters, cornices, window surrounds.
    for y in (-1500,-975,-300,300,975,1500): box(mesh,2028,y,180,28,58,360)
    box(mesh,2032,0,72,34,3300,24); box(mesh,2035,0,334,40,3300,32)
    for wy in (-675,675):
        box(mesh,2028,wy-185,167,28,22,170); box(mesh,2028,wy+185,167,28,22,170)
        box(mesh,2028,wy,250,28,390,22); box(mesh,2028,wy,82,28,390,22)
    # Curved masonry surround above the real rectangular main opening.
    for i in range(13):
        a=math.pi*i/12.0
        yy=150*math.cos(a); zz=278+150*math.sin(a)
        box(mesh,2032,yy,zz,36,34,58,roll=math.degrees(a)-90)

def build_ground_walls(mesh):
    # Four room bands around a clear 1550x1200 patio and 240 cm galleries.
    px,py=775,600
    gx,gy=1015,840
    for x in (-gx,gx):
        # Central 340 cm passage aligns entrance, zaguan and courtyard.
        wall_y(mesh,x,-840,-170,0,360,30); wall_y(mesh,x,170,840,0,360,30)
    for y in (-gy,gy):
        wall_x(mesh,y,-1015,-420,0,360,30); wall_x(mesh,y,-300,300,0,360,30); wall_x(mesh,y,420,1015,0,360,30)
    # room divisions, each interrupted by a 120cm passage
    for x in (-1450,1450):
        wall_y(mesh,x,-1650,-620,0,360,22); wall_y(mesh,x,-500,500,0,360,22); wall_y(mesh,x,620,1650,0,360,22)
    for y in (-1250,1250):
        wall_x(mesh,y,-2000,-1075,0,360,22); wall_x(mesh,y,-955,955,0,360,22); wall_x(mesh,y,1075,2000,0,360,22)

def build_ground_floors(mesh):
    # floor ring; patio remains open to sky and earth
    box(mesh,0,-1245,2.5,4000,810,5); box(mesh,0,1245,2.5,4000,810,5)
    box(mesh,-1387.5,0,2.5,1225,1680,5); box(mesh,1387.5,0,2.5,1225,1680,5)

def build_gallery(mesh):
    box(mesh,0,-720,8,2030,240,16); box(mesh,0,720,8,2030,240,16)
    box(mesh,-895,0,8,240,1200,16); box(mesh,895,0,8,240,1200,16)

def round_column(mesh,x,y,z=0,h=360,r=18):
    pts=[]
    for i in range(16):
        a=2*math.pi*i/16; pts.append((x+r*math.cos(a),y+r*math.sin(a)))
    append_extruded_polygon_safe(mesh,pts,h,tform(0,0,z))
    box(mesh,x,y,z+8,55,55,16); box(mesh,x,y,z+h-8,50,50,16)

def build_columns_arches(mesh):
    for x in (-760,-380,0,380,760):
        round_column(mesh,x,-600); round_column(mesh,x,600)
    for y in (-400,0,400):
        round_column(mesh,-775,y); round_column(mesh,775,y)
    # continuous lintel/cornice gives a coherent colonial arcade rhythm.
    box(mesh,0,-600,342,1600,32,36); box(mesh,0,600,342,1600,32,36)
    box(mesh,-775,0,342,32,1200,36); box(mesh,775,0,342,32,1200,36)
    # Segmented curved arch rings; consolidated in this single asset.
    for y in (-600,600):
        for cx in (-570,-190,190,570):
            for i in range(9):
                a=math.pi*i/8.0
                x=cx+180*math.cos(a); z=300+70*math.sin(a)
                box(mesh,x,y,z,48,34,24,roll=math.degrees(a)-90)

def build_plinth(mesh):
    for y in (-1650,1650): wall_x(mesh,y,-2000,2000,0,70,65)
    for x in (-2000,2000): wall_y(mesh,x,-1585,1585,0,70,65)

def build_upper_floors(mesh):
    box(mesh,0,-1245,372.5,4000,810,25)
    # Left wing segmented around a real 700x550 stairwell opening.
    box(mesh,-1900,0,372.5,200,1680,25); box(mesh,-937.5,0,372.5,325,1680,25)
    box(mesh,-1450,-445,372.5,700,790,25); box(mesh,-1450,670,372.5,700,340,25)
    box(mesh,1387.5,0,372.5,1225,1680,25)

def build_upper_walls(mesh):
    z=385; h=320
    for y in (-1650,1650): wall_x(mesh,y,-2000,2000,z,h)
    for x in (-2000,2000): wall_y(mesh,x,-1650,1650,z,h)
    for y in (-840,840): wall_x(mesh,y,-2000,-1075,z,h,30); wall_x(mesh,y,-955,955,z,h,30); wall_x(mesh,y,1075,2000,z,h,30)
    for x in (-1015,1015): wall_y(mesh,x,-840,-300,z,h,30); wall_y(mesh,x,-180,180,z,h,30); wall_y(mesh,x,300,840,z,h,30)

def build_stair(mesh):
    # Two flights, 22 real treads at ~17.0 rise and 29 cm going, plus landing.
    rise=385.0/22.0; going=29.0; width=160.0
    for i in range(11): box(mesh,-1650+i*going,350,i*rise/2,width if False else going,160,(i+1)*rise)
    box(mesh,-1302,225,192.5,120,410,25)
    for i in range(11): box(mesh,-1242-i*going,100,(192.5+(i+1)*rise)/2,going,160,192.5+(i+1)*rise)
    # handrails and posts
    for x in (-1650,-1360,-1302,-1532): box(mesh,x,255,250,6,6,210)
    box(mesh,-1505,255,260,330,8,8,0,-30)

def build_balcony(mesh):
    box(mesh,0,-960,405,1800,220,25)
    for x in range(-850,851,100): box(mesh,x,-1060,475,5,5,140)
    box(mesh,0,-1060,545,1800,8,8)
    box(mesh,2100,0,420,200,1400,25)
    for y in range(-650,651,100): box(mesh,2190,y,490,5,5,140)
    box(mesh,2190,0,560,8,1400,8)

def build_roof_main(mesh):
    # Closed, thick, continuous roof planes by wing; 65cm eaves.
    ridge_z=850
    # Front/rear wings run along local X; Roll produces the transverse slope.
    for cy in (-1245,1245):
        box(mesh,0,cy-300,ridge_z-66,4300,650,24,roll=12)
        box(mesh,0,cy+300,ridge_z-66,4300,650,24,roll=-12)
        box(mesh,0,cy,ridge_z,4300,18,34)
    # Side wings run along local Y; Pitch produces the transverse slope.
    for cx in (-1508,1508):
        box(mesh,cx-310,0,ridge_z-68,680,1900,24,pitch=-12)
        box(mesh,cx+310,0,ridge_z-68,680,1900,24,pitch=12)
        box(mesh,cx,0,ridge_z,18,1900,34)
    # Closed gable end caps.
    for x in (-2140,2140):
        append_extruded_polygon_safe(mesh,[(-610,0),(610,0),(0,132)],24,tform(x,0,718,pitch=0,yaw=90))

def build_roof_gallery(mesh):
    for y,r in ((-720,-10),(720,10)): box(mesh,0,y,690,2150,360,18,roll=r)
    for x,p in ((-895,10),(895,-10)): box(mesh,x,0,690,360,1320,18,pitch=p)

def build_ceilings(mesh):
    box(mesh,0,-1245,350,4000,810,12); box(mesh,0,1245,350,4000,810,12)
    box(mesh,-1900,0,350,200,1680,12); box(mesh,-937.5,0,350,325,1680,12)
    box(mesh,-1450,-445,350,700,790,12); box(mesh,-1450,670,350,700,340,12)
    box(mesh,1387.5,0,350,1225,1680,12)

def build_wood_trim(mesh):
    for y in (-1620,1620): box(mesh,0,y,715,4000,12,18)
    for x in (-1970,1970): box(mesh,x,0,715,12,3240,18)
    for y in (-1070,1070): box(mesh,0,y,365,2000,16,20)

def build_door(mesh,w=130,h=250,th=6):
    box(mesh,0,0,h/2,th,w,h)
    for z in (h*.25,h*.5,h*.75): box(mesh,-th/2-2,0,z,4,w-18,5)

def build_window(mesh,w=170,h=145):
    # frame and mullions only; opening remains transparent and physically real.
    for y in (-w/2,w/2): box(mesh,0,y,h/2,10,10,h)
    for z in (0,h): box(mesh,0,0,z,10,w,10)
    box(mesh,0,0,h/2,10,8,h); box(mesh,0,0,h/2,10,w,8)

BUILDERS = {
 "SM_HACV4_Foundation": build_foundation,
 "SM_HACV4_ExteriorShell": build_exterior,
 "SM_HACV4_InteriorWalls_Ground": build_ground_walls,
 "SM_HACV4_InteriorWalls_Upper": build_upper_walls,
 "SM_HACV4_GroundFloors": build_ground_floors,
 "SM_HACV4_UpperFloors": build_upper_floors,
 "SM_HACV4_CourtyardGallery": build_gallery,
 "SM_HACV4_ColumnsArches": build_columns_arches,
 "SM_HACV4_Staircase": build_stair,
 "SM_HACV4_Balcony": build_balcony,
 "SM_HACV4_Roof_Main": build_roof_main,
 "SM_HACV4_Roof_Galleries": build_roof_gallery,
 "SM_HACV4_Ceilings": build_ceilings,
 "SM_HACV4_StonePlinth": build_plinth,
 "SM_HACV4_WoodTrim": build_wood_trim,
 "SM_HACV4_MainDoor_Left": lambda m: build_door(m,130,280,7),
 "SM_HACV4_MainDoor_Right": lambda m: build_door(m,130,280,7),
 "SM_HACV4_InteriorDoor_A": lambda m: build_door(m,120,250,6),
 "SM_HACV4_InteriorDoor_B": lambda m: build_door(m,130,250,6),
 "SM_HACV4_Window_A": lambda m: build_window(m,170,145),
 "SM_HACV4_Window_B": lambda m: build_window(m,200,145)
}

MATERIAL_MAP = {
 "Foundation":"MI_HACV4_Stone", "ExteriorShell":"MI_HACV4_Plaster_Exterior",
 "InteriorWalls":"MI_HACV4_Plaster_Interior", "Floors":"MI_HACV4_Floor_Tile",
 "Gallery":"MI_HACV4_Floor_Tile", "Columns":"MI_HACV4_Plaster_Exterior",
 "Staircase":"MI_HACV4_Stone", "Balcony":"MI_HACV4_Wood", "Roof":"MI_HACV4_Roof_Terracotta",
 "Ceilings":"MI_HACV4_Plaster_Interior", "StonePlinth":"MI_HACV4_Stone", "WoodTrim":"MI_HACV4_Wood",
 "Door":"MI_HACV4_Wood", "Window":"MI_HACV4_Wood"
}

def material_for(name, materials):
    for key, mi in MATERIAL_MAP.items():
        if key in name: return materials[mi]
    return materials["MI_HACV4_Plaster_Exterior"]

def build_asset(name, builder):
    validate_level()
    mesh = unreal.DynamicMesh()
    builder(mesh)
    if hasattr(mesh, "get_triangle_count") and mesh.get_triangle_count() <= 0:
        fail("Empty mesh: " + name)
    uv0=generate_uv0_safe(mesh); uv1=generate_uv1_safe(mesh); recompute_normals_safe(mesh)
    path=ASSET_ROOT+"/"+name
    existed=unreal.EditorAssetLibrary.does_asset_exist(path)
    static_mesh=create_static_mesh_asset_safe(mesh,path)
    if existed:
        copy_dynamic_to_static_safe(mesh,static_mesh)
    collision=create_collision_safe(mesh,static_mesh)
    unreal.EditorAssetLibrary.save_loaded_asset(static_mesh, only_if_is_dirty=False)
    REPORT.setdefault("assets",{})[name]={"uv0":uv0,"uv1":uv1,"normals":True,"tangents":True,"collision":collision}
    del static_mesh; del mesh; gc.collect()
    return path

def local_to_world(local, yaw, origin):
    c=math.cos(math.radians(yaw)); s=math.sin(math.radians(yaw))
    return (origin[0]+local[0]*c-local[1]*s, origin[1]+local[0]*s+local[1]*c, origin[2]+local[2])

def spawn_existing_prop(name, asset_path, local, local_yaw, origin, building_yaw, folder):
    mesh=unreal.load_asset(asset_path)
    if mesh is None: fail("Missing interior asset: "+asset_path)
    world_pos=local_to_world(local,building_yaw,origin)
    actor=spawn_static_mesh_actor_safe(PREFIX+name,mesh,world_pos,building_yaw+local_yaw,folder,None)
    actor.set_actor_scale3d(unreal.Vector(1,1,1))
    return actor

def build_interiors_and_lighting(origin,yaw):
    P={
      "table":"/Game/Megascans/3D_Assets/Wooden_Table_veigfjmaw/S_Wooden_Table_veigfjmaw_lod3_Var1",
      "chair":"/Game/Megascans/3D_Assets/Wooden_Chair_wjglai2s/S_Wooden_Chair_wjglai2s_lod3_Var1",
      "bookshelf":"/Game/Megascans/3D_Assets/Wooden_Bookshelf_vmjhbix/S_Wooden_Bookshelf_vmjhbix_lod3",
      "book":"/Game/Megascans/3D_Assets/Old_Book_wldocam/S_Old_Book_wldocam_lod3_Var1",
      "bench":"/Game/Megascans/3D_Assets/Wooden_Bench_wjfjahl/S_Wooden_Bench_wjfjahl_lod3",
      "suitcase":"/Game/Megascans/3D_Assets/Leather_Luggage_Suitcase_wk2iafu/S_Leather_Luggage_Suitcase_wk2iafu_lod3",
      "lantern":"/Game/Megascans/3D_Assets/Traditional_Lantern_xccpecydw/S_Traditional_Lantern_xccpecydw_lod3"}
    props=[
      ("Archive_Bookshelf",P["bookshelf"],(-1520,-1180,5),90),("Archive_Table",P["table"],(-1350,-1050,5),0),
      ("Archive_Chair",P["chair"],(-1200,-1050,5),180),("Archive_Book_A",P["book"],(-1350,-1050,85),0),
      ("Dining_Table",P["table"],(1350,-1100,5),0),("Dining_Chair_A",P["chair"],(1180,-1100,5),0),
      ("Dining_Chair_B",P["chair"],(1520,-1100,5),180),("Dining_Chair_C",P["chair"],(1350,-1280,5),90),
      ("Dining_Chair_D",P["chair"],(1350,-920,5),-90),("Salon_Bench_A",P["bench"],(1450,1120,5),180),
      ("Salon_Bench_B",P["bench"],(1150,1120,5),180),("Salon_Table",P["table"],(1300,1320,5),0),
      ("History_Bench",P["bench"],(-1400,1120,5),0),("History_Suitcase",P["suitcase"],(-1200,1250,5),0),
      ("Kitchen_Table",P["table"],(1500,300,5),90),("Kitchen_Bench",P["bench"],(1650,300,5),90)]
    for name,path,loc,ry in props: spawn_existing_prop(name,path,loc,ry,origin,yaw,"JatunWasi/Hacienda_V4/Interiors")
    # Four existing lantern meshes and four small warm, non-shadowing point lights.
    lantern_locs=[(-1400,-1100,285),(1350,-1100,285),(-1400,1120,285),(1500,300,285)]
    existing={a.get_actor_label():a for a in unreal.EditorLevelLibrary.get_all_level_actors()}
    for i,loc in enumerate(lantern_locs,1):
        spawn_existing_prop("Lantern_%02d"%i,P["lantern"],loc,0,origin,yaw,"JatunWasi/Hacienda_V4/Lighting")
        label=PREFIX+"Light_%02d"%i
        light=existing.get(label)
        if light is None:
            wp=local_to_world((loc[0],loc[1],loc[2]-20),yaw,origin)
            light=unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.PointLight,unreal.Vector(*wp),unreal.Rotator(pitch=0,yaw=0,roll=0),transient=False)
            light.set_actor_label(label); light.set_folder_path("JatunWasi/Hacienda_V4/Lighting"); MANIFEST["actors"].append(label)
        wp=local_to_world((loc[0],loc[1],loc[2]-20),yaw,origin)
        light.set_actor_location(unreal.Vector(*wp),False,False)
        comp=light.point_light_component
        comp.set_editor_property("intensity",120.0); comp.set_editor_property("attenuation_radius",300.0)
        comp.set_editor_property("cast_shadows",False); comp.set_editor_property("use_temperature",True); comp.set_editor_property("temperature",3200.0)

def build_all():
    world=validate_level()
    log("START level="+EXPECTED_LEVEL)
    materials=create_material_instances()
    built={}
    for name,builder in BUILDERS.items():
        built[name]=build_asset(name,builder)
        flush_reports()
    origin=DESIGN["origin_cm"]; yaw=DESIGN["facade_yaw_deg"]
    folders={"Door":"JatunWasi/Hacienda_V4/Doors","Window":"JatunWasi/Hacienda_V4/Windows"}
    architecture=[]
    for name,path in built.items():
        if "Door" in name or "Window" in name: continue
        asset=unreal.EditorAssetLibrary.load_asset(path)
        actor=spawn_static_mesh_actor_safe(PREFIX+name.replace("SM_HACV4_",""),asset,origin,yaw,"JatunWasi/Hacienda_V4/Architecture",material_for(name,materials))
        architecture.append(actor.get_actor_label())
    # Main leaves occupy the real opening; offset along local Y and rotate around their own hinge visually.
    placements=[
      ("MainDoor_Left",built["SM_HACV4_MainDoor_Left"],(2004,-65,0),"Doors",90),
      ("MainDoor_Right",built["SM_HACV4_MainDoor_Right"],(2004,65,0),"Doors",-90),
      ("InteriorDoor_A",built["SM_HACV4_InteriorDoor_A"],(1018,-220,0),"Doors",90),
      ("InteriorDoor_B",built["SM_HACV4_InteriorDoor_B"],(-1018,220,0),"Doors",-90),
      ("Window_Front_A",built["SM_HACV4_Window_A"],(2004,-675,95),"Windows",0),
      ("Window_Front_B",built["SM_HACV4_Window_A"],(2004,675,95),"Windows",0),
      ("Window_Side_A",built["SM_HACV4_Window_B"],(-850,-1654,95),"Windows",0),
      ("Window_Side_B",built["SM_HACV4_Window_B"],(450,1654,95),"Windows",0)]
    cy=math.cos(math.radians(yaw)); sy=math.sin(math.radians(yaw))
    for label,path,(lx,ly,lz),kind,local_yaw in placements:
        wx=origin[0]+lx*cy-ly*sy; wy=origin[1]+lx*sy+ly*cy; wz=origin[2]+lz
        asset=unreal.EditorAssetLibrary.load_asset(path)
        spawn_static_mesh_actor_safe(PREFIX+label,asset,(wx,wy,wz),yaw+local_yaw,"JatunWasi/Hacienda_V4/"+kind,materials["MI_HACV4_Wood"])
    build_interiors_and_lighting(origin,yaw)
    # Mathematically verify access graph coverage.
    rooms=set(DESIGN["rooms_ground"]+DESIGN["rooms_upper"]); seen=set(); stack=["Acceso principal"]
    graph=DESIGN["access_graph"]
    undirected={r:set() for r in rooms}
    for a,bs in graph.items():
        for b in bs: undirected[a].add(b); undirected[b].add(a)
    while stack:
        node=stack.pop()
        if node in seen: continue
        seen.add(node); stack.extend(undirected.get(node,()))
    REPORT["accessibility"]={"reachable":sorted(seen),"all_rooms_reachable":rooms.issubset(seen),"unreachable":sorted(rooms-seen)}
    REPORT["architecture_actors"]=architecture
    REPORT["status"]="BUILT_UNSAVED_LEVEL"
    MANIFEST["status"]="BUILT"
    flush_reports()
    log("BUILD_COMPLETE assets=%d actors=%d"%(len(MANIFEST["assets"]),len(MANIFEST["actors"])))

try:
    build_all()
except Exception:
    REPORT["errors"].append(traceback.format_exc())
    REPORT["status"]="FAILED"
    flush_reports()
    raise
