import json
import struct
from pathlib import Path

import bmesh
import bpy


OUTPUT_DIR = Path(__file__).resolve().parent
BLEND_PATH = OUTPUT_DIR / "blender_pipeline_test.blend"
GLB_PATH = OUTPUT_DIR / "blender_pipeline_test.glb"


def fail(message):
    raise RuntimeError(message)


# Start with an empty scene and explicit metric units (one Blender unit = one metre).
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
for datablock in tuple(bpy.data.meshes):
    if datablock.users == 0:
        bpy.data.meshes.remove(datablock)

scene = bpy.context.scene
scene.unit_settings.system = "METRIC"
scene.unit_settings.scale_length = 1.0
scene.unit_settings.length_unit = "METERS"

# Create a 2 x 2 x 2 metre test cube and bake its object transforms.
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0.0, 0.0, 0.0))
cube = bpy.context.active_object
cube.name = "PipelineTestCube_2m"
cube.data.name = "PipelineTestCube_2m_Mesh"
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

# Recalculate outward-facing normals directly on the mesh.
bm = bmesh.new()
bm.from_mesh(cube.data)
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
bm.to_mesh(cube.data)
bm.free()
cube.data.update()

# Generate a real UV map using Blender's unwrap operation.
bpy.context.view_layer.objects.active = cube
cube.select_set(True)
bpy.ops.object.mode_set(mode="EDIT")
bpy.ops.mesh.select_all(action="SELECT")
bpy.ops.uv.smart_project(angle_limit=1.15192, island_margin=0.02)
bpy.ops.object.mode_set(mode="OBJECT")

# Assign a minimal Principled BSDF material.
material = bpy.data.materials.new(name="PipelineTestMaterial")
material.use_nodes = True
material.diffuse_color = (0.18, 0.42, 0.8, 1.0)
cube.data.materials.append(material)

# Validate the native scene before writing either artifact.
dimensions = tuple(round(float(value), 6) for value in cube.dimensions)
scale = tuple(round(float(value), 6) for value in cube.scale)
if dimensions != (2.0, 2.0, 2.0):
    fail(f"Unexpected cube dimensions: {dimensions}")
if scale != (1.0, 1.0, 1.0):
    fail(f"Transforms were not applied: {scale}")
if not cube.data.uv_layers or len(cube.data.uv_layers.active.data) == 0:
    fail("UV map was not created")
if len(cube.data.polygons) == 0 or any(poly.normal.length == 0 for poly in cube.data.polygons):
    fail("Mesh normals are missing or invalid")
if not cube.data.materials or cube.data.materials[0] is None:
    fail("Material was not assigned")

bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_PATH), check_existing=False)
bpy.ops.export_scene.gltf(
    filepath=str(GLB_PATH),
    export_format="GLB",
    use_selection=True,
    export_apply=True,
)

if not BLEND_PATH.is_file() or BLEND_PATH.stat().st_size == 0:
    fail("BLEND output is missing or empty")
if not GLB_PATH.is_file() or GLB_PATH.stat().st_size < 12:
    fail("GLB output is missing or too small")

with GLB_PATH.open("rb") as stream:
    magic, version, declared_length = struct.unpack("<4sII", stream.read(12))
if magic != b"glTF" or version != 2 or declared_length != GLB_PATH.stat().st_size:
    fail("Invalid GLB header")

result = {
    "blend_file_size": BLEND_PATH.stat().st_size,
    "glb_file_size": GLB_PATH.stat().st_size,
    "glb_header_valid": True,
    "objects": len(scene.objects),
    "mesh_objects": sum(obj.type == "MESH" for obj in scene.objects),
    "dimensions_meters": dimensions,
    "scale": scale,
    "uv_valid": True,
    "normals_valid": True,
    "material_valid": True,
}
print("PIPELINE_TEST_RESULT=" + json.dumps(result, sort_keys=True))
