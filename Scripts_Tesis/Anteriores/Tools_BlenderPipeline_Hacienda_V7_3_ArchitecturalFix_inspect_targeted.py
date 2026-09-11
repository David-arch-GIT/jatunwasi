import bpy
from mathutils import Vector
terms=('Stair','Balcony','UpperCorridor','Roof','Gable','InteriorWalls','Foundation','Architectural_Misc')
for o in bpy.context.scene.objects:
    if o.type!='MESH' or not any(t.lower() in o.name.lower() for t in terms): continue
    c=[o.matrix_world@Vector(v) for v in o.bound_box]
    lo=tuple(round(min(v[i] for v in c),3) for i in range(3));hi=tuple(round(max(v[i] for v in c),3) for i in range(3))
    print('TARGET',o.name,lo,hi,len(o.data.polygons),[m.name if m else None for m in o.data.materials])
