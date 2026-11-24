# 220_escalera_descanso.py - colision caminable en el descanso del 2P + puente al pasillo (sigue la geometria visible)
import unreal, json, traceback
R={"added":[], "trace":[], "err":[]}
EXC=["PCG_","Vol","Trig","Nav","Snd","App","Cria","MALEZA","RUTA","Farol","Letrero","Cartela","RELATO"]
try:
    eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    cube=unreal.EditorAssetLibrary.load_asset("/Engine/BasicShapes/Cube")
    def floor(lbl,cx,cy,sx,sy,z):
        for a in list(eas.get_all_level_actors()):
            if a.get_actor_label()==lbl: eas.destroy_actor(a)
        act=unreal.EditorLevelLibrary.spawn_actor_from_object(cube, unreal.Vector(cx,cy,z), unreal.Rotator(0.0,12.0,0.0))
        act.set_actor_label(lbl); act.set_actor_scale3d(unreal.Vector(sx,sy,0.12))
        smc=act.get_component_by_class(unreal.StaticMeshComponent)
        smc.set_collision_profile_name("InvisibleWall"); smc.set_collision_enabled(unreal.CollisionEnabled.QUERY_AND_PHYSICS)
        smc.set_editor_property("cast_shadow",False); smc.set_editor_property("can_ever_affect_navigation",True)
        act.set_actor_hidden_in_game(True)
        R["added"].append(lbl)
    # descanso oeste (sobre UpperLandingConnector) z427
    floor("COL_Hac_Desc2P", -7558.0, -2110.0, 2.4, 3.0, 427.0)   # ~240x300
    # puente descanso -> pasillo (y-2000 a -1760)
    floor("COL_Hac_Desc2P_B", -7430.0, -1900.0, 3.0, 3.2, 427.0) # ~300x320
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
    unreal.SystemLibrary.execute_console_command(w, "RebuildNavigation")
    # re-trazar el CAMINO REAL: rampa (x-7448) y-2870..-2240, luego descanso (x-7558) y-2200..-1991, luego (x-7450) y-1950..-1772
    WS=[unreal.ObjectTypeQuery.OBJECT_TYPE_QUERY1]
    def tr(x,y):
        hrs=unreal.SystemLibrary.line_trace_multi_for_objects(w,unreal.Vector(x,y,520),unreal.Vector(x,y,-80),WS,True,[],unreal.DrawDebugTrace.NONE,True)
        best=None
        if hrs:
            for hr in hrs:
                t=hr.to_tuple(); z=round(t[5].z); n=(t[9].get_actor_label() if t[9] else "?")
                if any(k in n for k in EXC): continue
                if best is None or z>best[0]: best=(z,n)
        return (best[0] if best else None, best[1][:20] if best else "NADA")
    path=[]
    for yi in range(-2860,-2240,120): path.append((-7448.0,float(yi)))
    for yi in range(-2240,-1980,120): path.append((-7558.0,float(yi)))
    for yi in range(-1980,-1760,110): path.append((-7450.0,float(yi)))
    for x,y in path:
        z,n=tr(x,y); R["trace"].append({"xy":[round(x),round(y)],"z":z,"on":n})
    R["ok"]=True
except Exception as e:
    R["fatal"]=str(e); R["tb"]=traceback.format_exc()[-300:]
open("C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/desc2p.json","w").write(json.dumps(R))
