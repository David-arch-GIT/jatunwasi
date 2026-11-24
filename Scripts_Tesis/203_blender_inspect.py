import bpy, json, sys
R={"creatures":{}}
files={
 "karisiri":"C:/UnrealProjects/JatunWasiNawpakay/Saved/Models/processed/karisiri_full.glb",
 "condenado":"C:/UnrealProjects/JatunWasiNawpakay/Saved/Models/processed/condenado_full.glb",
 "duende":"C:/UnrealProjects/JatunWasiNawpakay/Saved/Models/processed/duende_full.glb",
}
for name,fp in files.items():
    try:
        bpy.ops.wm.read_factory_settings(use_empty=True)
        bpy.ops.import_scene.gltf(filepath=fp)
        meshes=[o for o in bpy.data.objects if o.type=='MESH']
        arms=[o for o in bpy.data.objects if o.type=='ARMATURE']
        info={"meshes":[m.name for m in meshes],"arms":[a.name for a in arms]}
        sc=bpy.context.scene
        dg=bpy.context.evaluated_depsgraph_get()
        f0,f1=sc.frame_start, sc.frame_end
        info["frames"]=[f0,f1]
        lows=[]
        step=max(1,(f1-f0)//12)
        for f in range(f0,f1+1,step):
            sc.frame_set(f)
            dg=bpy.context.evaluated_depsgraph_get()
            minz=1e9
            for m in meshes:
                ev=m.evaluated_get(dg)
                me=ev.to_mesh()
                mw=ev.matrix_world
                for v in me.vertices:
                    z=(mw @ v.co).z
                    if z<minz: minz=z
                ev.to_mesh_clear()
            lows.append((f,round(minz,1)))
        info["lowest_world_z_por_frame"]=lows
        info["min_low"]=round(min(l[1] for l in lows),1)
        info["max_low"]=round(max(l[1] for l in lows),1)
        R["creatures"][name]=info
    except Exception as e:
        R["creatures"][name]={"err":str(e)[:120]}
open("C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/blender_inspect.json","w").write(json.dumps(R,indent=0))
print("DONE")
