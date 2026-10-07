import unreal, json, traceback
OUT=r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/relieve_cull.json"
res={"removed":0,"kept":0,"err":None}
try:
    w=unreal.EditorLevelLibrary.get_editor_world()
    eas=unreal.EditorActorSubsystem()
    EXT=unreal.Vector(270,270,170)  # buffer ~2.7m de la ruta
    host=None
    for a in eas.get_all_level_actors():
        if a.get_actor_label()=="PCG_RelieveVol": host=a; break
    if not host:
        res["err"]="no PCG_RelieveVol"; open(OUT,"w").write(json.dumps(res)); raise SystemExit
    for c in host.get_components_by_class(unreal.InstancedStaticMeshComponent):
        n=c.get_instance_count()
        rem=[]
        for i in range(n):
            tr=c.get_instance_transform(i, True)
            loc=tr.translation
            pr=unreal.NavigationSystemV1.project_point_to_navigation(w, loc, None, None, EXT)
            if pr is not None and not (abs(pr.x)<1 and abs(pr.y)<1 and abs(pr.z)<1):
                if abs(pr.x-loc.x)<270 and abs(pr.y-loc.y)<270:
                    rem.append(i)
        if rem:
            c.remove_instances(rem); res["removed"]+=len(rem)
        # culling por distancia (perf) + sin sombra
        try: c.set_cull_distances(0, 7000)
        except: pass
        try: c.set_editor_property("cast_shadow", False)
        except: pass
        res["kept"]+=c.get_instance_count()
    # camara oblicua sobre un cruce camino+bosque (plaza->convento)
    cam=unreal.Vector(2200,900,750)
    look=unreal.MathLibrary.find_look_at_rotation(cam, unreal.Vector(3600,2600,0))
    unreal.EditorLevelLibrary.set_level_viewport_camera_info(cam, look)
    res["ok"]=True
except Exception as e:
    res["err"]=traceback.format_exc()
open(OUT,"w").write(json.dumps(res,indent=1,default=str))
