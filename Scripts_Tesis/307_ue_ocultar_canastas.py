import unreal, json
OUT=r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/ocultar_can.json"
res={"ocultadas":[]}
eas=unreal.EditorActorSubsystem()
for a in eas.get_all_level_actors():
    lbl=a.get_actor_label()
    if lbl.startswith("PLZP_Canasta"):
        for c in a.get_components_by_class(unreal.StaticMeshComponent):
            c.set_editor_property("hidden_in_game", True)
            c.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
        res["ocultadas"].append(lbl)
les=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem); les.save_current_level()
res["n"]=len(res["ocultadas"])
open(OUT,"w").write(json.dumps(res,indent=1))
