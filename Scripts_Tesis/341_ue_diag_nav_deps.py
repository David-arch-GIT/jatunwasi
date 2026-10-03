# Diagnostico: pisos de colision del NavMesh, runtime_generation, y refs de recovery/plaza.
import unreal, json
OUT=r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/diag_nav_deps.json"
res={"pisos_nav":[], "recast":{}, "sospechosos_recovery":[]}
eas=unreal.EditorActorSubsystem()
acts=eas.get_all_level_actors()
res["n_actores"]=len(acts)
if len(acts)<400:
    res["estado"]="cargando"; open(OUT,"w").write(json.dumps(res,indent=1)); raise SystemExit
for a in acts:
    lbl=a.get_actor_label()
    low=lbl.lower()
    cn=a.get_class().get_name()
    # pisos/colisiones que el navmesh necesita
    if any(k in low for k in ["navfloor","nav_floor","col_conv","col_plz","navmesh","piso_nav","navcol"]) or "PLZ_nav" in lbl:
        for c in a.get_components_by_class(unreal.StaticMeshComponent):
            try:
                res["pisos_nav"].append({"label":lbl[:34],"col":str(c.get_editor_property("collision_enabled")).split(".")[-1].strip(">"),"hidden":bool(c.get_editor_property("hidden_in_game")),"vis":bool(c.get_editor_property("visible"))})
            except Exception: pass
    # recovery / reset / plaza refs
    if any(k in low for k in ["recovery","reset","respawn","volver","return","inicio","safe","recover"]):
        res["sospechosos_recovery"].append(lbl[:40]+" ["+cn+"]")
    if cn=="RecastNavMesh" or "RecastNavMesh" in cn:
        try:
            res["recast"]={"runtime_generation":str(a.get_editor_property("runtime_generation")),
                           "agent_max_slope":a.get_editor_property("agent_max_slope")}
        except Exception as e: res["recast"]={"err":str(e)[:50]}
# navsystem project settings (runtime generation global)
try:
    ns=unreal.get_default_object(unreal.NavigationSystemV1)
    res["navsys"]={}
    for p in ["b_auto_create_navigation_data","b_allow_client_side_navigation","b_should_discard_sub_level_navigation_data"]:
        try: res["navsys"][p]=str(ns.get_editor_property(p))
        except Exception: pass
except Exception as e:
    res["navsys_err"]=str(e)[:50]
res["n_pisos"]=len(res["pisos_nav"])
open(OUT,"w").write(json.dumps(res,indent=1))
