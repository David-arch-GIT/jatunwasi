import unreal, json
OUT=r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/audit_pcg.json"
res={"pcg":[]}
eas=unreal.EditorActorSubsystem()
for a in eas.get_all_level_actors():
    comps=a.get_components_by_class(unreal.PCGComponent)
    for c in comps:
        d={"actor":a.get_actor_label()[:30]}
        for prop in ["generation_trigger","generated","is_generating","bActivated","generate_on_load","one_time"]:
            try: d[prop]=str(c.get_editor_property(prop))
            except Exception: pass
        res["pcg"].append(d)
res["n"]=len(res["pcg"])
open(OUT,"w").write(json.dumps(res,indent=1))
