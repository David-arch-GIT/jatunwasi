import unreal, json, traceback
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/inv_cuadros.json"
res = {"frames": [], "otros_marco": [], "fatal": None}
try:
    eas = unreal.EditorActorSubsystem()
    actors = eas.get_all_level_actors()
    res["n_actors"] = len(actors)
    for a in actors:
        try:
            lbl = a.get_actor_label()
        except Exception:
            continue
        smcs = a.get_components_by_class(unreal.StaticMeshComponent)
        is_frame = False; mats_slot1 = None
        for c in smcs:
            try:
                m = c.get_static_mesh()
            except Exception:
                m = None
            if m and "FN_Cuadro" in m.get_name():
                is_frame = True
                try:
                    mi = c.get_material(1); mats_slot1 = mi.get_name() if mi else None
                except Exception:
                    mats_slot1 = "ERR"
                break
        if is_frame:
            loc = a.get_actor_location()
            res["frames"].append({"lbl": lbl, "slot1": mats_slot1, "loc": [round(loc.x), round(loc.y), round(loc.z)]})
        elif ("cuadro" in lbl.lower()) or ("marco" in lbl.lower()) or ("frame" in lbl.lower()):
            res["otros_marco"].append(lbl)
    res["n_frames"] = len(res["frames"])
except Exception as e:
    res["fatal"] = str(e) + " | " + traceback.format_exc()[:400]
open(OUT, "w").write(json.dumps(res, indent=1))
