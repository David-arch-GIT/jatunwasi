import unreal, json
OUT=r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/audit_cull.json"
res={"foliage":[]}
eas=unreal.EditorActorSubsystem()
# meshes de vegetacion, agrupados por mesh -> conteo, cull actual
por_mesh={}
for a in eas.get_all_level_actors():
    for c in a.get_components_by_class(unreal.InstancedStaticMeshComponent):
        m=c.get_editor_property("static_mesh"); mn=m.get_name() if m else "?"
        try: n=c.get_instance_count()
        except Exception: n=0
        if n==0: continue
        try:
            sc=c.get_editor_property("instance_start_cull_distance")
            ec=c.get_editor_property("instance_end_cull_distance")
        except Exception:
            sc=ec=-1
        d=por_mesh.setdefault(mn,{"inst":0,"comps":0,"start":sc,"end":ec})
        d["inst"]+=n; d["comps"]+=1
res["foliage"]=[{"mesh":k[:30],"inst":v["inst"],"comps":v["comps"],"cull_start":v["start"],"cull_end":v["end"]} for k,v in sorted(por_mesh.items(), key=lambda x:-x[1]["inst"])[:35]]
open(OUT,"w").write(json.dumps(res,indent=1))
