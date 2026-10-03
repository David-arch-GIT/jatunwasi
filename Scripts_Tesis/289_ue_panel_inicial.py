import unreal, json
OUT=r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/panelini.json"
res={"ok":[]}
eas=unreal.EditorActorSubsystem()
for a in eas.get_all_level_actors():
    if not a.get_actor_label().startswith("Cartela_"): continue
    for c in a.get_components_by_class(unreal.StaticMeshComponent):
        # empezar OCULTO (el clic lo mostrara con ToggleVisibility)
        c.set_visibility(False, False)
        c.set_editor_property("hidden_in_game", False)
        # quitar culling por distancia
        try: c.set_editor_property("ld_max_draw_distance", 0.0)
        except Exception: pass
        try: c.set_editor_property("cached_max_draw_distance", 0.0)
        except Exception: pass
    res["ok"].append(a.get_actor_label())
les=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem); les.save_current_level()
res["n"]=len(res["ok"])
open(OUT,"w").write(json.dumps(res,indent=1))
