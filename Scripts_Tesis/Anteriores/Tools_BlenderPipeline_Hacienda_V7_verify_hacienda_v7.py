import bpy, bmesh, json

c=bpy.data.collections.get("EXPORT_UNREAL")
objects=[o for o in c.objects if o.type=='MESH']
bad={k:[] for k in ("negative","nonmanifold","open","uv0","uv1","materials","empty")}
triangles=0
for o in objects:
    if any(v<0 for v in o.scale): bad["negative"].append(o.name)
    if len(o.data.uv_layers)<1: bad["uv0"].append(o.name)
    if len(o.data.uv_layers)<2: bad["uv1"].append(o.name)
    if not o.data.materials: bad["materials"].append(o.name)
    if not o.data.polygons: bad["empty"].append(o.name)
    bm=bmesh.new(); bm.from_mesh(o.data)
    if any(not e.is_manifold for e in bm.edges): bad["nonmanifold"].append(o.name)
    if any(e.is_boundary for e in bm.edges): bad["open"].append(o.name)
    bm.free()
    triangles += sum(max(0,len(p.vertices)-2) for p in o.data.polygons)
result={"export_meshes":len(objects),"triangles":triangles,"bad":bad,"main_left":sum(o.name=="EXP_MainDoor_Left" for o in objects),"main_right":sum(o.name=="EXP_MainDoor_Right" for o in objects),"reference_objects":len(bpy.data.collections.get("REFERENCE_ONLY").objects),"roof_valleys":sum("Valley" in o.name for o in bpy.context.scene.objects)}
print("FINAL_V7_AUDIT="+json.dumps(result,sort_keys=True))
assert len(objects)<=25 and triangles<=150000
assert all(not values for values in bad.values())
assert result["main_left"]==1 and result["main_right"]==1
