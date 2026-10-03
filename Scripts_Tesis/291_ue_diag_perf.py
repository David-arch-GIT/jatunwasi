import unreal, json
OUT=r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/diag_perf.json"
res={"total":0, "tick_on":[], "ticking_count":0, "level_seq":[], "hism":0, "ism":0, "skeletal":0, "particle":0, "widgetcomp":0, "audio_autoactivate":0, "by_tickclass":{}}
eas=unreal.EditorActorSubsystem()
acts=eas.get_all_level_actors()
res["total"]=len(acts)
for a in acts:
    try:
        if a.get_editor_property("actor_tick_enabled"):
            res["ticking_count"]+=1
            cn=a.get_class().get_name()
            res["by_tickclass"][cn]=res["by_tickclass"].get(cn,0)+1
    except Exception: pass
    cn=a.get_class().get_name()
    if "LevelSequenceActor" in cn or "SequenceActor" in cn:
        res["level_seq"].append(a.get_actor_label())
    for c in a.get_components_by_class(unreal.HierarchicalInstancedStaticMeshComponent): res["hism"]+=1
    for c in a.get_components_by_class(unreal.InstancedStaticMeshComponent): res["ism"]+=1
    for c in a.get_components_by_class(unreal.SkeletalMeshComponent): res["skeletal"]+=1
    for c in a.get_components_by_class(unreal.AudioComponent):
        try:
            if c.get_editor_property("auto_activate"): res["audio_autoactivate"]+=1
        except Exception: pass
# top tick classes
res["by_tickclass"]=dict(sorted(res["by_tickclass"].items(), key=lambda x:-x[1])[:15])
open(OUT,"w").write(json.dumps(res,indent=1))
