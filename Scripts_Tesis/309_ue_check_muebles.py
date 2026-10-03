import unreal, json
OUT=r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/check_muebles.json"
res={"en_origen_REAL":[], "ok":[]}
eas=unreal.EditorActorSubsystem()
for a in eas.get_all_level_actors():
    lbl=a.get_actor_label()
    if not (lbl.startswith("CV2_") or lbl.startswith("TMP2_") or lbl in ["CNVP_Bell"]): continue
    o,e=a.get_actor_bounds(False)  # centro de bounds = donde se dibuja de verdad
    dist=(o.x**2+o.y**2)**0.5
    entry={"lbl":lbl,"bounds":[round(o.x),round(o.y),round(o.z)]}
    if dist<200 and abs(o.z)<200:  # bounds cerca del origen = pilado de verdad
        res["en_origen_REAL"].append(entry)
    else:
        res["ok"].append(lbl)
res["n_origen"]=len(res["en_origen_REAL"]); res["n_ok"]=len(res["ok"])
open(OUT,"w").write(json.dumps(res,indent=1))
