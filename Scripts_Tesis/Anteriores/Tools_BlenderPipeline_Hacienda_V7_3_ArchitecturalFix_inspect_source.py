import bpy
from mathutils import Vector

for obj in bpy.context.scene.objects:
    if obj.type != 'MESH':
        continue
    corners = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
    lo = tuple(round(min(v[i] for v in corners), 3) for i in range(3))
    hi = tuple(round(max(v[i] for v in corners), 3) for i in range(3))
    if lo[1] < -14.0 or hi[2] > 6.0 or 'Upper' in obj.name or 'Roof' in obj.name:
        mats = [m.name if m else 'NULL' for m in obj.data.materials]
        print(f'JWNOBJ|{obj.name}|{lo}|{hi}|{len(obj.data.polygons)}|{mats}')
