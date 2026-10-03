import unreal, json
OUT=r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/hide_catre.json"
res={}
eas=unreal.EditorActorSubsystem()
for a in eas.get_all_level_actors():
    if a.get_actor_label()=="CV2_Catre":
        for c in a.get_components_by_class(unreal.StaticMeshComponent):
            c.set_editor_property("hidden_in_game", True)
            c.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
        res["hecho"]=True
les=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem); les.save_current_level()
open(OUT,"w").write(json.dumps(res))
