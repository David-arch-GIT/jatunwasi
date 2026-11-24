# 191_ue_ruta_guia.py
# Rastro de marcas luminosas (guia de recorrido) a lo largo de las 3 rutas:
# plaza->hacienda (HC), plaza->convento (CV), plaza->templo (TM).
# Reusa material emisivo existente (M_JW_NarrationMarker). Sin crear material (evita cuelgue).
import unreal, json, math, traceback
out="C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups"; R={"marcas":0,"rutas":{},"err":[]}
try:
    eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    WS=[unreal.ObjectTypeQuery.OBJECT_TYPE_QUERY1]
    EXCL=["PCG_","Vol","Trig","Narr","Cria","Nav","Snd","App","RELATO","PANEL","POSTE","MALEZA","RUTA","COL_"]
    def groundz(x,y):
        hrs=unreal.SystemLibrary.line_trace_multi_for_objects(w,unreal.Vector(x,y,2000),unreal.Vector(x,y,-600),WS,True,[],unreal.DrawDebugTrace.NONE,True)
        if hrs:
            for hr in hrs:
                t=hr.to_tuple(); z=t[5].z; n=(t[9].get_actor_label() if t[9] else "?")
                if any(k in n for k in EXCL): continue
                return z
        return None
    # recoger waypoints por ruta desde los NavMeshBoundsVolume PATH_<R>_nav_<i>
    wps={"HC":[], "CV":[], "TM":[]}
    import re
    for a in eas.get_all_level_actors():
        m=re.match(r"PATH_(HC|CV|TM)_nav_(\d+)$", a.get_actor_label())
        if m:
            loc=a.get_actor_location()
            wps[m.group(1)].append((int(m.group(2)), loc.x, loc.y))
    # puntos de arranque desde la plaza (borde) para cada ruta
    starts={"HC":(-700.0,-1000.0), "CV":(700.0,-350.0), "TM":(0.0,-250.0)}
    mat=unreal.EditorAssetLibrary.load_asset("/Game/JWN/Blueprints/M_JW_NarrationMarker")
    if not mat: mat=unreal.EditorAssetLibrary.load_asset("/Engine/BasicShapes/BasicShapeMaterial")
    disc=unreal.EditorAssetLibrary.load_asset("/Engine/BasicShapes/Cylinder")
    # borrar marcas previas
    for a in list(eas.get_all_level_actors()):
        if a.get_actor_label().startswith("RUTA_"): eas.destroy_actor(a)
    STEP=350.0
    for route in ["HC","CV","TM"]:
        pts=sorted(wps[route])
        line=[starts[route]] + [(x,y) for _,x,y in pts]
        R["rutas"][route]=len(line)
        placed=0
        for i in range(len(line)-1):
            x0,y0=line[i]; x1,y1=line[i+1]
            seg=math.hypot(x1-x0,y1-y0)
            n=max(1,int(seg//STEP))
            for k in range(n):
                t=k/float(n)
                x=x0+(x1-x0)*t; y=y0+(y1-y0)*t
                gz=groundz(x,y)
                if gz is None: continue
                act=unreal.EditorLevelLibrary.spawn_actor_from_object(disc, unreal.Vector(x,y,gz+4.0), unreal.Rotator(0,0,0))
                act.set_actor_label("RUTA_%s_%d_%d"%(route,i,k))
                act.set_actor_scale3d(unreal.Vector(0.42,0.42,0.02))
                smc=act.get_component_by_class(unreal.StaticMeshComponent)
                if mat: smc.set_material(0, mat)
                smc.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
                smc.set_editor_property("cast_shadow", False)
                smc.set_editor_property("can_ever_affect_navigation", False)
                placed+=1; R["marcas"]+=1
        R["rutas"][route]={"tramos":len(line),"marcas":placed}
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
    R["ok"]=True
except Exception as e:
    R["fatal"]=str(e); R["tb"]=traceback.format_exc()[-500:]
open(out+"/ruta.json","w").write(json.dumps(R))
