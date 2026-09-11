import bpy
import bmesh
import json
import math
import os
import traceback
from mathutils import Vector

ROOT = os.path.dirname(os.path.abspath(__file__))
RENDERS = os.path.join(ROOT, "Renders")
BLEND_OUT = os.path.join(ROOT, "JW_Hacienda_Mayorazgo_V7_1_UpperConnection.blend")
FBX_OUT = os.path.join(ROOT, "JW_Hacienda_V7_UpperConnection.fbx")
LOG_OUT = os.path.join(ROOT, "upper_connection_build.log")
MANIFEST_OUT = os.path.join(ROOT, "upper_connection_manifest.json")
AUDIT_OUT = os.path.join(ROOT, "upper_connection_audit.json")
DESIGN_OUT = os.path.join(ROOT, "upper_connection_design.json")

# Real measurements from MAP_JatunWasi_MCP_V06, converted cm -> m.
GAP = 1.9940184877893353
OVERLAP = 0.10
LENGTH = GAP + 2.0 * OVERLAP
WIDTH = 1.70
LANDING_Z = 4.41
CORRIDOR_Z = 4.32
MID_Z = (LANDING_Z + CORRIDOR_Z) * 0.5
FLOOR_THICKNESS = 0.20
RAIL_HEIGHT = 1.05
RAIL_EDGE_X = WIDTH * 0.5 - 0.035
SLOPE = math.atan2(CORRIDOR_Z - LANDING_Z, LENGTH)
WORLD_LOCATION_CM = [-7587.72909386006, -2281.566, 0.0]
WORLD_ROTATION_DEG = [0.0, 12.094757080078134, 0.0]

log_lines = []
def log(msg):
    print(msg)
    log_lines.append(str(msg))

def material(name, color, roughness=0.65):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1.0)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    return m

def add_box(name, dims, location, mat=None, rotation=(0, 0, 0), collection=None):
    bpy.ops.mesh.primitive_cube_add(location=location, rotation=rotation)
    o = bpy.context.object
    o.name = name
    o.dimensions = dims
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if mat:
        o.data.materials.append(mat)
    if collection:
        for c in list(o.users_collection): c.objects.unlink(o)
        collection.objects.link(o)
    return o

def floor_z(y):
    return MID_Z + math.tan(SLOPE) * y

def add_beam_between(name, a, b, thickness, mat, collection):
    a, b = Vector(a), Vector(b)
    mid = (a + b) * 0.5
    direction = b - a
    o = add_box(name, (thickness, thickness, direction.length), mid, mat, collection=collection)
    o.rotation_mode = 'QUATERNION'
    o.rotation_quaternion = direction.to_track_quat('Z', 'Y')
    bpy.context.view_layer.objects.active = o
    o.select_set(True)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.rotation_mode = 'XYZ'
    return o

def apply_uvs(obj):
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=math.radians(66), island_margin=0.02)
    bpy.ops.object.mode_set(mode='OBJECT')
    uv0 = obj.data.uv_layers.active
    uv0.name = "UV0"
    uv1 = obj.data.uv_layers.new(name="UV1")
    for i, loop in enumerate(uv0.data):
        uv1.data[i].uv = loop.uv

def audit_mesh(obj):
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    boundary = sum(1 for e in bm.edges if e.is_boundary)
    non_manifold = sum(1 for e in bm.edges if not e.is_manifold)
    tris = sum(max(0, len(f.verts) - 2) for f in bm.faces)
    bm.free()
    return {"triangles": tris, "open_boundaries": boundary, "non_manifold_edges": non_manifold}

try:
    os.makedirs(RENDERS, exist_ok=True)
    # Isolate the working copy; source .blend remains untouched.
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for c in list(bpy.data.collections):
        if c.name != bpy.context.scene.collection.name and c.users == 0:
            bpy.data.collections.remove(c)
    main_col = bpy.data.collections.new("UPPER_CONNECTION")
    ucx_col = bpy.data.collections.new("UCX_COLLISION")
    ref_col = bpy.data.collections.new("RENDER_REFERENCE")
    bpy.context.scene.collection.children.link(main_col)
    bpy.context.scene.collection.children.link(ucx_col)
    bpy.context.scene.collection.children.link(ref_col)

    wood = material("M_Wood_Preview", (0.16, 0.055, 0.018), 0.72)
    floor_mat = material("M_ColonialFloor_Preview", (0.36, 0.12, 0.055), 0.82)
    plaster = material("M_Plaster_Preview", (0.58, 0.43, 0.28), 0.9)
    visible = []

    # Continuous sloped colonial floor, 20 cm structural thickness.
    slab = add_box("Floor_Slab", (WIDTH, LENGTH, FLOOR_THICKNESS),
                   (0, 0, MID_Z - FLOOR_THICKNESS * 0.5), floor_mat,
                   rotation=(SLOPE, 0, 0), collection=main_col)
    visible.append(slab)
    # Front beam and two longitudinal stringers.
    visible.append(add_box("Front_Structural_Beam", (WIDTH + 0.12, 0.16, 0.24),
                           (0, 0, MID_Z - 0.31), wood, rotation=(SLOPE,0,0), collection=main_col))
    for x in (-0.55, 0.55):
        visible.append(add_box("Longitudinal_Beam", (0.14, LENGTH + 0.12, 0.22),
                               (x, 0, MID_Z - 0.29), wood, rotation=(SLOPE,0,0), collection=main_col))
    # Secondary joists.
    for y in (-0.78, -0.39, 0.0, 0.39, 0.78):
        visible.append(add_box("Secondary_Joist", (WIDTH + 0.08, 0.10, 0.16),
                               (0, y, floor_z(y) - 0.25), wood, rotation=(SLOPE,0,0), collection=main_col))
    # End ledgers establish real support at both existing structures.
    for y in (-LENGTH * 0.5 + 0.05, LENGTH * 0.5 - 0.05):
        visible.append(add_box("End_Ledger", (WIDTH + 0.10, 0.12, 0.28),
                               (0, y, floor_z(y) - 0.30), wood, rotation=(SLOPE,0,0), collection=main_col))
    # Four visible timber corbels anchored to landing/corridor, avoiding ground route.
    for x in (-0.58, 0.58):
        visible.append(add_beam_between("Landing_Corbel", (x,-LENGTH/2+0.04,floor_z(-LENGTH/2)-0.12),
                                        (x,-LENGTH/2+0.48,floor_z(-LENGTH/2)-0.72), 0.12, wood, main_col))
        visible.append(add_beam_between("Corridor_Corbel", (x,LENGTH/2-0.04,floor_z(LENGTH/2)-0.12),
                                        (x,LENGTH/2-0.48,floor_z(LENGTH/2)-0.72), 0.12, wood, main_col))
    # Side railings: open at both ends, 11.5 cm maximum baluster spacing.
    baluster_count = 19
    for side in (-1, 1):
        x = side * RAIL_EDGE_X
        for i in range(baluster_count):
            y = -LENGTH/2 + 0.10 + i * (LENGTH - 0.20) / (baluster_count - 1)
            z = floor_z(y) + RAIL_HEIGHT * 0.5
            visible.append(add_box("Rail_Baluster", (0.055,0.055,RAIL_HEIGHT), (x,y,z), wood, collection=main_col))
        visible.append(add_box("Continuous_Handrail", (0.10,LENGTH-0.04,0.10),
                               (x,0,MID_Z+RAIL_HEIGHT), wood, rotation=(SLOPE,0,0), collection=main_col))
        visible.append(add_box("Lower_Rail", (0.075,LENGTH-0.12,0.075),
                               (x,0,MID_Z+0.43), wood, rotation=(SLOPE,0,0), collection=main_col))

    # Join all visible architectural pieces into exactly one exportable mesh.
    bpy.ops.object.select_all(action='DESELECT')
    for o in visible: o.select_set(True)
    bpy.context.view_layer.objects.active = slab
    bpy.ops.object.join()
    main = bpy.context.object
    main.name = "EXP_UpperLandingConnector"
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    apply_uvs(main)

    # Three simple custom collision volumes: walkable slab and exposed side guards.
    ucx_floor = add_box("UCX_EXP_UpperLandingConnector_00", (WIDTH-0.06,LENGTH,FLOOR_THICKNESS),
                        (0,0,MID_Z-FLOOR_THICKNESS*0.5), rotation=(SLOPE,0,0), collection=ucx_col)
    ucx_left = add_box("UCX_EXP_UpperLandingConnector_01", (0.08,LENGTH-0.06,RAIL_HEIGHT),
                       (-RAIL_EDGE_X,0,MID_Z+RAIL_HEIGHT*0.5), rotation=(SLOPE,0,0), collection=ucx_col)
    ucx_right = add_box("UCX_EXP_UpperLandingConnector_02", (0.08,LENGTH-0.06,RAIL_HEIGHT),
                        (RAIL_EDGE_X,0,MID_Z+RAIL_HEIGHT*0.5), rotation=(SLOPE,0,0), collection=ucx_col)
    for o in (ucx_floor,ucx_left,ucx_right):
        o.display_type='WIRE'
        o.hide_render=True

    # Human-scale reference, excluded from export.
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.18, depth=1.70, location=(0,0,MID_Z+0.85))
    human=bpy.context.object;human.name="REFERENCE_Human_170cm"
    for c in list(human.users_collection): c.objects.unlink(human)
    ref_col.objects.link(human)
    human.data.materials.append(plaster)

    # Render setup.
    scene=bpy.context.scene
    scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1.0
    scene.render.engine='BLENDER_EEVEE'
    scene.render.resolution_x=1000;scene.render.resolution_y=750;scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG'
    scene.world.color=(0.035,0.045,0.06)
    bpy.ops.object.light_add(type='AREA', location=(3,-4,8));key=bpy.context.object;key.data.energy=1200;key.data.shape='DISK';key.data.size=5
    bpy.ops.object.light_add(type='AREA', location=(-4,2,6));fill=bpy.context.object;fill.data.energy=700;fill.data.size=4
    bpy.ops.object.camera_add();cam=bpy.context.object;scene.camera=cam
    def point_camera(pos, target=(0,0,MID_Z)):
        cam.location=pos
        cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler()
    shots=[
      ("01_Connector_Aerial.png",(4.2,-4.8,8.4),(0,0,MID_Z),False),
      ("02_Connector_From_Landing.png",(0,-4.8,5.25),(0,0.35,MID_Z+0.35),False),
      ("03_Connector_From_Corridor.png",(0,4.8,5.10),(0,-0.35,MID_Z+0.35),False),
      ("04_Connector_Underside.png",(3.6,-3.0,2.5),(0,0,MID_Z-0.35),False),
      ("05_Connector_Supports.png",(-3.6,-2.8,3.0),(0,0,MID_Z-0.25),False),
      ("06_Connector_HumanScale.png",(3.2,-4.2,5.5),(0,0,MID_Z+0.45),True),
    ]
    for filename,pos,target,show_human in shots:
        human.hide_render=not show_human
        point_camera(pos,target)
        scene.render.filepath=os.path.join(RENDERS,filename)
        bpy.ops.render.render(write_still=True)

    # Export only the connector and its three UCX objects.
    bpy.ops.object.select_all(action='DESELECT')
    for o in (main,ucx_floor,ucx_left,ucx_right):o.select_set(True)
    bpy.context.view_layer.objects.active=main
    bpy.ops.export_scene.fbx(filepath=FBX_OUT,use_selection=True,object_types={'MESH'},
                             axis_forward='-Y',axis_up='Z',apply_unit_scale=True,
                             bake_space_transform=False,add_leaf_bones=False,
                             use_mesh_modifiers=True,mesh_smooth_type='FACE')

    audit=audit_mesh(main)
    audit.update({
      "negative_scale": int(any(v < 0 for v in main.scale)),
      "missing_uv0": int(main.data.uv_layers.get("UV0") is None),
      "missing_uv1": int(main.data.uv_layers.get("UV1") is None),
      "material_slots": [m.name for m in main.data.materials],
      "missing_materials": sum(1 for m in main.data.materials if m is None),
      "ucx_count": 3,
      "scale": list(main.scale),
      "dimensions_m": list(main.dimensions),
    })
    design={
      "gap_length_cm": GAP*100, "connector_length_cm": LENGTH*100,
      "walkable_width_cm": WIDTH*100, "floor_thickness_cm": FLOOR_THICKNESS*100,
      "landing_top_z_cm": LANDING_Z*100, "corridor_top_z_cm": CORRIDOR_Z*100,
      "slope_degrees": math.degrees(SLOPE), "railing_height_cm": RAIL_HEIGHT*100,
      "support_system": "end ledgers, twin longitudinal beams, secondary joists, four anchored timber corbels",
      "world_location_cm": WORLD_LOCATION_CM, "world_rotation_deg": WORLD_ROTATION_DEG,
      "world_scale": [1,1,1]
    }
    manifest={
      "source_object":"EXP_UpperLandingConnector",
      "ucx_objects":["UCX_EXP_UpperLandingConnector_00","UCX_EXP_UpperLandingConnector_01","UCX_EXP_UpperLandingConnector_02"],
      "fbx":FBX_OUT,"unreal_destination":"/Game/JWN/Architecture/Hacienda_V7/StructuralFix",
      "unreal_asset":"SM_HACV7_UpperLandingConnector",
      "actor_name":"HACV7_UpperLandingConnector",
      "actor_folder":"JatunWasi/Hacienda_V7/Architecture/StructuralFix",
      "transform":{"location_cm":WORLD_LOCATION_CM,"rotation_deg":WORLD_ROTATION_DEG,"scale":[1,1,1]},
      "material_slots":["MI_HACV7_Brick_Floor","MI_HACV7_Dark_Wood"]
    }
    with open(DESIGN_OUT,'w',encoding='utf-8') as f:json.dump(design,f,indent=2)
    with open(MANIFEST_OUT,'w',encoding='utf-8') as f:json.dump(manifest,f,indent=2)
    with open(AUDIT_OUT,'w',encoding='utf-8') as f:json.dump(audit,f,indent=2)
    bpy.ops.wm.save_as_mainfile(filepath=BLEND_OUT)
    log("BUILD_SUCCESS")
    log(json.dumps(audit))
except Exception:
    log("BUILD_FAILED")
    log(traceback.format_exc())
    raise
finally:
    with open(LOG_OUT,'w',encoding='utf-8') as f:f.write("\n".join(log_lines)+"\n")
