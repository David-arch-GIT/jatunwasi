import unreal, json
OUT=r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/unhide.json"
res={"ok":[]}
eas=unreal.EditorActorSubsystem()
for a in eas.get_all_level_actors():
    if a.get_actor_label().startswith("Cartela_"):
        for c in a.get_components_by_class(unreal.StaticMeshComponent):
            c.set_editor_property("hidden_in_game", False); c.set_visibility(True, False)
        res["ok"].append(a.get_actor_label())
les=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem); les.save_current_level()
res["n"]=len(res["ok"])
open(OUT,"w").write(json.dumps(res,indent=1))
