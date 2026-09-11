import unreal, json
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/investigar2.json"
res = {"total": 0, "skeletal": [], "match": [], "err": None}
try:
    eas = unreal.EditorActorSubsystem()
    acts = eas.get_all_level_actors()
    res["total"] = len(acts)
    KW = ["app", "karis", "duend", "conden", "carreta", "aparic"]
    for a in acts:
        try:
            lbl = a.get_actor_label(); nm = a.get_name(); cls = a.get_class().get_name()
        except Exception:
            continue
        loc = a.get_actor_location()
        row = {"label": lbl, "name": nm, "cls": cls, "loc": [round(loc.x), round(loc.y), round(loc.z)]}
        if cls in ("SkeletalMeshActor",):
            res["skeletal"].append(row)
        s = (lbl + " " + nm).lower()
        if any(k in s for k in KW):
            try: row["hig"] = a.get_actor_hidden_in_game()
            except Exception: row["hig"] = "?"
            res["match"].append(row)
except Exception as e:
    import traceback; res["err"] = traceback.format_exc()
open(OUT, "w").write(json.dumps(res, indent=1))
unreal.log("INV2 total=%d skel=%d match=%d" % (res["total"], len(res["skeletal"]), len(res["match"])))
