import unreal, json
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/vars_instancia.json"
res = {"criaturas": [], "err": []}
eas = unreal.EditorActorSubsystem()
for a in eas.get_all_level_actors():
    lab = a.get_actor_label()
    if not lab.startswith("Cria_"): continue
    d = {"lab": lab}
    for v in ["RadioZona", "VelMin", "VelMax", "PausaMin", "PausaMax", "DistDeteccion", "ProbDeambular"]:
        try: d[v] = a.get_editor_property(v)
        except Exception as e: d[v] = "err:" + str(e)[:20]
    # auto possess
    try: d["auto_possess_ai"] = str(a.get_editor_property("auto_possess_ai"))
    except Exception: pass
    res["criaturas"].append(d)
open(OUT, "w").write(json.dumps(res, indent=1))
