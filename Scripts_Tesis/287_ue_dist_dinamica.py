import unreal, json
OUT=r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/distdin.json"
res={"ok":[], "err":[]}
eas=unreal.EditorActorSubsystem()
DIST=500.0   # cm: la cartela se ve dentro de 5 m del objeto, se oculta al alejarse
for a in eas.get_all_level_actors():
    if not a.get_actor_label().startswith("Cartela_"): continue
    try:
        for c in a.get_components_by_class(unreal.StaticMeshComponent):
            c.set_editor_property("hidden_in_game", False)
            # distancia maxima de dibujado -> aparece/desaparece por cercania
            try: c.set_editor_property("ld_max_draw_distance", DIST)
            except Exception: pass
            try: c.set_editor_property("cached_max_draw_distance", DIST)
            except Exception: pass
            try: c.set_cull_distance(DIST) if hasattr(c,"set_cull_distance") else None
            except Exception: pass
        res["ok"].append(a.get_actor_label())
    except Exception as e:
        res["err"].append(a.get_actor_label()+":"+str(e)[:50])
les=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem); les.save_current_level()
res["n"]=len(res["ok"]); res["dist"]=DIST
open(OUT,"w").write(json.dumps(res,indent=1))
