import unreal, json
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/vis2.json"
res = {"actores": [], "err": []}
eas = unreal.EditorActorSubsystem()
for a in eas.get_all_level_actors():
    lab = a.get_actor_label()
    if not (lab.startswith("App_") or lab.startswith("AppSK_")):
        continue
    d = {"label": lab}
    try: d["hidden_game"] = bool(a.get_editor_property("actor_hidden_in_game"))
    except Exception as e: d["hidden_game"] = "err"
    try: d["hidden_editor"] = bool(a.is_temporarily_hidden_in_editor())
    except Exception: pass
    for c in a.get_components_by_class(unreal.SkeletalMeshComponent):
        try:
            ad = c.get_editor_property("animation_data")
            seq = ad.get_editor_property("anim_to_play") if ad else None
            d["anim"] = seq.get_name() if seq else "NINGUNA"
        except Exception as e:
            d["anim"] = "err:" + str(e)[:18]
    res["actores"].append(d)
open(OUT, "w").write(json.dumps(res, indent=1))
