import bpy
import bmesh
import json
import math
import os
import sys
import traceback
from mathutils import Vector

ROOT = os.path.dirname(os.path.abspath(__file__))
BLEND_OUT = os.path.join(ROOT, "JW_Hacienda_Mayorazgo_V7_2_RailingFix.blend")
FBX_OUT = os.path.join(ROOT, "JW_Hacienda_V7_RailingFix.fbx")
RENDER_DIR = os.path.join(ROOT, "Renders")
MANIFEST = os.path.join(ROOT, "railing_fix_manifest.json")
AUDIT = os.path.join(ROOT, "railing_fix_audit.json")
BUILD_LOG = os.path.join(ROOT, "railing_fix_build.log")

SOURCE_NAME = "EXP_ExteriorBalcony"
OUTPUT_NAME = "EXP_ExteriorBalcony_RailingFix"
OPENING_CENTER_X = -5.29
OPENING_LEFT_X = -6.15
OPENING_RIGHT_X = -4.43
OPENING_WIDTH_M = OPENING_RIGHT_X - OPENING_LEFT_X
RAIL_Y = -6.65
HANDRAIL_Z = 4.92
POST_Z = 4.42


def log(message):
    print(message)
    with open(BUILD_LOG, "a", encoding="utf-8") as handle:
        handle.write(message + "\n")


def connected_components_world(obj):
    mesh = obj.data
    adjacency = [[] for _ in mesh.vertices]
    for edge in mesh.edges:
        a, b = edge.vertices
        adjacency[a].append(b)
        adjacency[b].append(a)
    unseen = set(range(len(mesh.vertices)))
    result = []
    while unseen:
        seed = unseen.pop()
        stack = [seed]
        indices = [seed]
        while stack:
            current = stack.pop()
            for nxt in adjacency[current]:
                if nxt in unseen:
                    unseen.remove(nxt)
                    stack.append(nxt)
                    indices.append(nxt)
        coords = [obj.matrix_world @ mesh.vertices[i].co for i in indices]
        mins = Vector((min(v.x for v in coords), min(v.y for v in coords), min(v.z for v in coords)))
        maxs = Vector((max(v.x for v in coords), max(v.y for v in coords), max(v.z for v in coords)))
        result.append({"indices": indices, "min": mins, "max": maxs, "center": (mins + maxs) * 0.5})
    return result


def remove_target_components(obj):
    components = connected_components_world(obj)
    remove_indices = set()
    removed = []
    for comp in components:
        mn, mx, center = comp["min"], comp["max"], comp["center"]
        dims = mx - mn
        is_inner = abs(center.y - RAIL_Y) < 0.10
        is_full_handrail = is_inner and dims.x > 30.0 and 4.84 < center.z < 5.00
        is_opening_baluster = (
            is_inner
            and dims.x < 0.20
            and dims.y < 0.20
            and 0.85 < dims.z < 1.15
            and OPENING_LEFT_X < center.x < OPENING_RIGHT_X
        )
        if is_full_handrail or is_opening_baluster:
            remove_indices.update(comp["indices"])
            removed.append({
                "kind": "handrail" if is_full_handrail else "baluster",
                "center": list(center),
                "dimensions": list(dims),
            })
    if len(removed) != 4:
        raise RuntimeError(f"Expected one handrail and three balusters, found {removed}")
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bm.verts.ensure_lookup_table()
    bmesh.ops.delete(bm, geom=[bm.verts[i] for i in sorted(remove_indices)], context="VERTS")
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()
    return removed


def duplicate_applied(source, name, location, scale):
    new = source.copy()
    new.data = source.data.copy()
    new.name = name
    bpy.context.collection.objects.link(new)
    new.location = location
    new.rotation_euler = source.rotation_euler.copy()
    new.scale = scale
    bpy.context.view_layer.objects.active = new
    new.select_set(True)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    new.select_set(False)
    return new


def add_terminations_and_split_handrail(target):
    rail_source = bpy.data.objects["ARCH_WoodTrim_InnerRail"]
    post_source = bpy.data.objects["ARCH_WoodTrim_INT_13"]
    full_min, full_max = -15.5, 15.5
    pieces = []
    left_length = OPENING_LEFT_X - full_min
    right_length = full_max - OPENING_RIGHT_X
    pieces.append(duplicate_applied(
        rail_source, "RF_Handrail_Left",
        ((full_min + OPENING_LEFT_X) * 0.5, RAIL_Y, HANDRAIL_Z),
        (left_length / 31.0, 1.0, 1.0)))
    pieces.append(duplicate_applied(
        rail_source, "RF_Handrail_Right",
        ((OPENING_RIGHT_X + full_max) * 0.5, RAIL_Y, HANDRAIL_Z),
        (right_length / 31.0, 1.0, 1.0)))
    post_half = 0.052
    left_post_x = OPENING_LEFT_X - post_half
    right_post_x = OPENING_RIGHT_X + post_half
    post_scale = (0.104 / 0.065, 0.100 / 0.065, 1.0)
    pieces.append(duplicate_applied(post_source, "RF_TerminalPost_Left", (left_post_x, RAIL_Y, POST_Z), post_scale))
    pieces.append(duplicate_applied(post_source, "RF_TerminalPost_Right", (right_post_x, RAIL_Y, POST_Z), post_scale))
    bpy.ops.object.select_all(action="DESELECT")
    target.select_set(True)
    for obj in pieces:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = target
    bpy.ops.object.join()
    target.name = OUTPUT_NAME
    return {"left_post_x": left_post_x, "right_post_x": right_post_x}


def make_material(name, color, metallic=0.0, roughness=0.55):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1.0)
    mat.metallic = metallic
    mat.roughness = roughness
    mat.use_nodes = True
    shader = mat.node_tree.nodes.get("Principled BSDF")
    if shader:
        shader.inputs["Base Color"].default_value = (*color, 1.0)
        shader.inputs["Metallic"].default_value = metallic
        shader.inputs["Roughness"].default_value = roughness
    return mat


def box(name, location, scale, material):
    bpy.ops.mesh.primitive_cube_add(location=location)
    obj = bpy.context.object
    obj.name = name
    obj.scale = (scale[0] * 0.5, scale[1] * 0.5, scale[2] * 0.5)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(material)
    return obj


def point_camera(camera, target):
    camera.rotation_euler = (Vector(target) - camera.location).to_track_quat("-Z", "Y").to_euler()


def render_scene(target_obj, before_obj):
    os.makedirs(RENDER_DIR, exist_ok=True)
    for obj in bpy.context.scene.objects:
        obj.hide_render = True
    wood = make_material("RF_WoodPreview", (0.16, 0.055, 0.018), 0.0, 0.42)
    guide = make_material("RF_OpeningGuide", (0.08, 0.32, 0.10), 0.0, 0.65)
    for obj in (target_obj, before_obj):
        if obj.data.materials:
            obj.data.materials[0] = wood
        else:
            obj.data.materials.append(wood)
    walkway = box("RF_ConnectorReference", (OPENING_CENTER_X, -5.72, 3.94), (OPENING_WIDTH_M, 1.85, 0.10), guide)
    human = None
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=0.22, depth=1.75, location=(OPENING_CENTER_X, -5.45, 4.825))
    human = bpy.context.object
    human.name = "RF_HumanReference"
    human.data.materials.append(make_material("RF_Human", (0.14, 0.22, 0.45), 0.0, 0.5))
    for obj in (walkway, human):
        obj.hide_render = False
    bpy.ops.object.light_add(type="AREA", location=(-5.3, -3.0, 8.0))
    key = bpy.context.object
    key.data.energy = 1600
    key.data.shape = "DISK"
    key.data.size = 6.0
    point_camera(key, (OPENING_CENTER_X, RAIL_Y, 4.45))
    key.hide_render = False
    bpy.ops.object.light_add(type="AREA", location=(-1.0, -8.0, 6.0))
    fill = bpy.context.object
    fill.data.energy = 900
    fill.data.size = 5.0
    point_camera(fill, (OPENING_CENTER_X, RAIL_Y, 4.5))
    fill.hide_render = False
    bpy.ops.object.camera_add()
    camera = bpy.context.object
    camera.data.lens = 48
    camera.hide_render = False
    bpy.context.scene.camera = camera
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 720
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.world.color = (0.025, 0.025, 0.025)

    def shot(filename, loc, look, show_before=False, show_human=False):
        before_obj.hide_render = not show_before
        target_obj.hide_render = show_before
        human.hide_render = not show_human
        camera.location = loc
        point_camera(camera, look)
        scene.render.filepath = os.path.join(RENDER_DIR, filename)
        bpy.ops.render.render(write_still=True)

    camera.data.lens = 38
    shot("01_Railing_Before.png", (-5.3, -2.4, 5.45), (-5.3, -6.65, 4.45), True)
    shot("02_Railing_After.png", (-5.3, -2.4, 5.45), (-5.3, -6.65, 4.45))
    shot("03_Connector_Opening_From_Landing.png", (-5.3, -3.6, 4.85), (-5.3, -7.0, 4.45))
    shot("04_Connector_Opening_From_Corridor.png", (-5.3, -9.2, 4.85), (-5.3, -5.3, 4.45))
    shot("05_Handrail_Terminations.png", (-5.3, -3.2, 5.35), (-5.3, -6.65, 4.65))
    shot("06_Human_Scale.png", (-2.2, -2.8, 5.6), (-5.3, -6.0, 4.55), False, True)
    before_obj.hide_render = True
    human.hide_render = True
    target_obj.data.materials[0] = bpy.data.materials["MAT_Dark_Wood"]


def mesh_audit(obj):
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    non_manifold = sum(1 for e in bm.edges if not e.is_manifold)
    open_boundaries = sum(1 for e in bm.edges if e.is_boundary)
    triangles = sum(max(1, len(face.verts) - 2) for face in bm.faces)
    bm.free()
    return {
        "object": obj.name,
        "scale": list(obj.scale),
        "dimensions": list(obj.dimensions),
        "triangles": triangles,
        "non_manifold": non_manifold,
        "open_boundaries": open_boundaries,
        "negative_scale": int(obj.scale.x < 0 or obj.scale.y < 0 or obj.scale.z < 0),
        "uv_layers": [uv.name for uv in obj.data.uv_layers],
        "material_slots": [slot.material.name if slot.material else None for slot in obj.material_slots],
    }


def export_fbx(obj):
    bpy.ops.object.select_all(action="DESELECT")
    obj.hide_set(False)
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.export_scene.fbx(
        filepath=FBX_OUT,
        use_selection=True,
        object_types={"MESH"},
        global_scale=1.0,
        apply_unit_scale=False,
        apply_scale_options="FBX_SCALE_NONE",
        axis_forward="-Y",
        axis_up="Z",
        use_mesh_modifiers=True,
        mesh_smooth_type="FACE",
        add_leaf_bones=False,
        bake_anim=False,
    )


def main():
    os.makedirs(RENDER_DIR, exist_ok=True)
    with open(BUILD_LOG, "w", encoding="utf-8") as handle:
        handle.write("Hacienda V7 railing surgical fix\n")
    source = bpy.data.objects.get(SOURCE_NAME)
    if source is None or source.type != "MESH":
        raise RuntimeError(f"Missing source mesh object {SOURCE_NAME}")
    before = source.copy()
    before.data = source.data.copy()
    before.name = "RF_BeforeReference"
    bpy.context.collection.objects.link(before)
    before.hide_viewport = True
    before.hide_render = True
    original_dimensions = list(source.dimensions)
    original_materials = [slot.material.name if slot.material else None for slot in source.material_slots]
    original_uvs = [uv.name for uv in source.data.uv_layers]
    removed = remove_target_components(source)
    terminals = add_terminations_and_split_handrail(source)
    render_scene(source, before)
    audit = mesh_audit(source)
    audit.update({
        "original_dimensions": original_dimensions,
        "dimensions_unchanged": all(abs(a - b) < 0.0001 for a, b in zip(original_dimensions, audit["dimensions"])),
        "original_material_slots": original_materials,
        "material_slots_unchanged": original_materials == audit["material_slots"],
        "original_uv_layers": original_uvs,
        "uv0_valid": len(audit["uv_layers"]) >= 1,
        "uv1_valid": len(audit["uv_layers"]) >= 2,
        "normals_valid": all(p.normal.length > 0.99 for p in source.data.polygons),
        "opening_width_cm": OPENING_WIDTH_M * 100.0,
        "removed_components": removed,
        "terminal_posts": terminals,
    })
    if audit["non_manifold"] or audit["open_boundaries"]:
        raise RuntimeError(f"Mesh topology invalid: {audit}")
    if not audit["dimensions_unchanged"] or not audit["material_slots_unchanged"]:
        raise RuntimeError(f"Original contract changed: {audit}")
    export_fbx(source)
    manifest = {
        "source_object": SOURCE_NAME,
        "export_object": OUTPUT_NAME,
        "source_asset": "/Game/JWN/Architecture/Hacienda_V7/Meshes/EXP_ExteriorBalcony",
        "temporary_destination": "/Game/JWN/Architecture/Hacienda_V7/RailingFixValidation/EXP_ExteriorBalcony_RailingFix",
        "opening_center_x_m": OPENING_CENTER_X,
        "opening_width_cm": OPENING_WIDTH_M * 100.0,
        "rail_y_m": RAIL_Y,
        "fbx": FBX_OUT,
    }
    with open(AUDIT, "w", encoding="utf-8") as handle:
        json.dump(audit, handle, indent=2)
    with open(MANIFEST, "w", encoding="utf-8") as handle:
        json.dump(manifest, handle, indent=2)
    bpy.ops.wm.save_as_mainfile(filepath=BLEND_OUT)
    log("BUILD_SUCCESS")
    log(json.dumps(audit, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        log("BUILD_FAILED")
        log(traceback.format_exc())
        raise
