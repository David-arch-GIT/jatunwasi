import unreal, json
OUT=r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/check_overlap.json"
res={}
eas=unreal.EditorActorSubsystem()
targets=["PLZP_CanastaChuno","PLZP_CanastaChuno_Fix","FlowerA_L11","FlowerA_L12","FlowerA_R11","FlowerA_R12"]
for a in eas.get_all_level_actors():
    lbl=a.get_actor_label()
    if lbl in targets:
        loc=a.get_actor_location()
        wl=None
        for c in a.get_components_by_class(unreal.StaticMeshComponent):
            if isinstance(c, unreal.InstancedStaticMeshComponent): continue
            wl=c.get_world_location(); break
        res[lbl]={"actor":[round(loc.x,1),round(loc.y,1),round(loc.z,1)],
                  "mesh_wloc":[round(wl.x,1),round(wl.y,1),round(wl.z,1)] if wl else None}
open(OUT,"w").write(json.dumps(res,indent=1))
