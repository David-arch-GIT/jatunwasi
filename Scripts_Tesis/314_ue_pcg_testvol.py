import unreal, json
OUT=r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/pcg_test.json"
res={}
eas=unreal.EditorActorSubsystem()
for a in eas.get_all_level_actors():
    if a.get_actor_label()=="PCG_ForestTestVol":
        for c in a.get_components_by_class(unreal.PCGComponent):
            for prop,val in [("bActivated",False)]:
                try: c.set_editor_property(prop, val); res[prop]="ok"
                except Exception as e: res[prop]="err:"+str(e)[:40]
        res["hecho"]=True
les=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem); les.save_current_level()
open(OUT,"w").write(json.dumps(res))
