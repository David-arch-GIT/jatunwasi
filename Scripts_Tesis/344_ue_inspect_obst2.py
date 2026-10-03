import unreal, json
OUT=r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/obst2.json"
res={"actores":[]}
eas=unreal.EditorActorSubsystem()
acts=eas.get_all_level_actors()
res["n"]=len(acts)
TARGETS=["HACV7_EXP_Staircase","HACV7_UpperLandingConnector","COL_Puente_Escalera2P","MUS_Alfombra_dorm","HACV7_EntranceApron_Final","HACV7_EXP_Foundation_Floors","CONV_ISM_02"]
for a in acts:
    try:
        lbl=a.get_actor_label()
        if not any(t in lbl for t in TARGETS):
            continue
        loc=a.get_actor_location()
        sc=a.get_actor_scale3d()
        info={"label":lbl[:40],"clase":a.get_class().get_name(),"loc":[round(loc.x),round(loc.y),round(loc.z)],"escala":[round(sc.x,2),round(sc.y,2),round(sc.z,2)],"comps":[]}
        try:
            o,e=a.get_actor_bounds(False)
            info["z_rango"]=[round(o.z-e.z),round(o.z+e.z)]
            info["bounds_ext"]=[round(e.x),round(e.y),round(e.z)]
        except Exception:
            info["z_rango"]="n/a"
        for c in a.get_components_by_class(unreal.StaticMeshComponent):
            sm=c.get_editor_property("static_mesh")
            try:
                col=str(c.get_editor_property("collision_enabled")).split(".")[-1].replace(">","")
                info["comps"].append({"mesh":(sm.get_name() if sm else "?"),"col":col,"hidden":bool(c.get_editor_property("hidden_in_game"))})
            except Exception:
                pass
        for c in a.get_components_by_class(unreal.InstancedStaticMeshComponent):
            sm=c.get_editor_property("static_mesh")
            try:
                cnt=c.get_instance_count()
            except Exception:
                cnt=0
            try:
                col=str(c.get_editor_property("collision_enabled")).split(".")[-1].replace(">","")
            except Exception:
                col="?"
            info["comps"].append({"ISM_mesh":(sm.get_name() if sm else "?"),"inst":cnt,"col":col})
        res["actores"].append(info)
    except Exception as ex:
        res["actores"].append({"err":str(ex)[:70]})
res["encontrados"]=[x.get("label","?") for x in res["actores"]]
open(OUT,"w").write(json.dumps(res,indent=1))
