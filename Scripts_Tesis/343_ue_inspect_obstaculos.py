# Inspecciona los actores que bloquean navegacion (escaleras, entrada, arcos convento).
import unreal, json
OUT=r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/obstaculos.json"
res={"actores":[]}
eas=unreal.EditorActorSubsystem()
acts=eas.get_all_level_actors()
res["n"]=len(acts)
if len(acts)<400:
    res["estado"]="cargando"; open(OUT,"w").write(json.dumps(res,indent=1)); raise SystemExit
TARGETS=["HACV7_EXP_Staircase","HACV7_UpperLandingConnector","COL_Puente_Escalera2P","MUS_Alfombra_dorm",
 "HACV7_EntranceApron_Final","HACV7_EXP_Foundation_Floors","CONV_ISM_02"]
for a in acts:
  try:
    lbl=a.get_actor_label()
    if not any(t in lbl for t in TARGETS): continue
    try: o,e=a.get_actor_bounds(False)
    except Exception: o,e=a.get_actor_location(), unreal.Vector(0,0,0)
    loc=a.get_actor_location(); sc=a.get_actor_scale3d()
    info={"label":lbl[:40],"clase":a.get_class().get_name(),
          "loc":[round(loc.x),round(loc.y),round(loc.z)],
          "escala":[round(sc.x,2),round(sc.y,2),round(sc.z,2)],
          "bounds_centro":[round(o.x),round(o.y),round(o.z)],
          "bounds_ext":[round(e.x),round(e.y),round(e.z)],
          "z_rango":[round(o.z-e.z),round(o.z+e.z)],
          "comps":[]}
    for c in a.get_components_by_class(unreal.StaticMeshComponent):
        sm=c.get_editor_property("static_mesh")
        try:
            info["comps"].append({"mesh":(sm.get_name() if sm else "?"),
                "col":str(c.get_editor_property("collision_enabled")).split(".")[-1].strip(">"),
                "hidden":bool(c.get_editor_property("hidden_in_game"))})
        except Exception: pass
    n_ism=0
    for c in a.get_components_by_class(unreal.InstancedStaticMeshComponent):
        sm=c.get_editor_property("static_mesh")
        try: n=c.get_instance_count()
        except Exception: n=0
        n_ism+=n
        info["comps"].append({"ISM_mesh":(sm.get_name() if sm else "?"),"inst":n,
            "col":str(c.get_editor_property("collision_enabled")).split(".")[-1].strip(">")})
    res["actores"].append(info)
  except Exception as ex:
    res["actores"].append({"error_en":str(ex)[:60]})
res["encontrados"]=[a["label"] for a in res["actores"]]
open(OUT,"w").write(json.dumps(res,indent=1))
