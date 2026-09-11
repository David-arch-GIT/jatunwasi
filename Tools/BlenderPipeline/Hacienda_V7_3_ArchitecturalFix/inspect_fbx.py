import bpy, sys
from mathutils import Vector
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.fbx(filepath=sys.argv[-1])
for o in bpy.context.scene.objects:
    if o.type=='MESH':
        c=[o.matrix_world@Vector(x) for x in o.bound_box]
        lo=tuple(round(min(v[i] for v in c),3) for i in range(3)); hi=tuple(round(max(v[i] for v in c),3) for i in range(3))
        print('FBXOBJ',o.name,lo,hi,len(o.data.polygons),[m.name if m else None for m in o.data.materials])
