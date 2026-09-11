import bpy
o=bpy.data.objects['SM_HACV7_EntranceApron_Final_V07Fix']
for p in o.data.polygons:
    print('APRONFACE',p.index,tuple(round(v,3) for v in p.center),tuple(round(v,3) for v in p.normal),len(p.vertices))
