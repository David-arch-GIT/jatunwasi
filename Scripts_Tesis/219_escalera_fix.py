# 219_escalera_fix.py - EVALUADO: puentea el hueco rampa->pasillo (59cm) + limpia colisiones encimadas + nav continuo
import unreal, json, traceback
R={"removed":[], "added":None, "err":[]}
try:
    eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    cube=unreal.EditorAssetLibrary.load_asset("/Engine/BasicShapes/Cube")
    # 1) quitar colisiones conflictivas (alturas distintas que rompen nav/piso)
    for lbl in ["COL_HACV7_StairLanding","COL_Puente_Escalera2P","COL_Hac_Top2P_FINAL"]:
        for a in list(eas.get_all_level_actors()):
            if a.get_actor_label()==lbl:
                eas.destroy_actor(a); R["removed"].append(lbl)
    # 2) DESCANSO continuo que puentea rampa(414 @ y-2241) -> pasillo(427 @ y-2182)
    for a in list(eas.get_all_level_actors()):
        if a.get_actor_label()=="COL_Hac_EscBridge": eas.destroy_actor(a)
    # box grueso que solapa rampa-top y pasillo (z 410-430), cubre ancho escalera
    br=unreal.EditorLevelLibrary.spawn_actor_from_object(cube, unreal.Vector(-7430.0,-2215.0,420.0), unreal.Rotator(0.0,12.0,0.0))
    br.set_actor_label("COL_Hac_EscBridge")
    br.set_actor_scale3d(unreal.Vector(3.6,1.7,0.20))  # ~360 x 170 x 20cm (z 410-430)
    smc=br.get_component_by_class(unreal.StaticMeshComponent)
    smc.set_collision_profile_name("InvisibleWall")
    smc.set_collision_enabled(unreal.CollisionEnabled.QUERY_AND_PHYSICS)
    smc.set_editor_property("cast_shadow", False)
    smc.set_editor_property("can_ever_affect_navigation", True)
    br.set_actor_hidden_in_game(True)
    R["added"]="COL_Hac_EscBridge z410-430 puente"
    # 3) muretes invisibles a los lados de la rampa (que no te caigas de lado)
    for a in list(eas.get_all_level_actors()):
        if a.get_actor_label().startswith("COL_Hac_EscWall"): eas.destroy_actor(a)
    for s,tag in [(1,"R"),(-1,"L")]:
        wx=-7448.0 + s*190.0
        wl=unreal.EditorLevelLibrary.spawn_actor_from_object(cube, unreal.Vector(wx,-2550.0,230.0), unreal.Rotator(31.0,12.0,0.0))
        wl.set_actor_label("COL_Hac_EscWall_%s"%tag)
        wl.set_actor_scale3d(unreal.Vector(0.1,8.5,1.2))
        sw=wl.get_component_by_class(unreal.StaticMeshComponent)
        sw.set_collision_profile_name("InvisibleWall")
        sw.set_collision_enabled(unreal.CollisionEnabled.QUERY_AND_PHYSICS)
        sw.set_editor_property("cast_shadow", False)
        sw.set_editor_property("can_ever_affect_navigation", False)
        wl.set_actor_hidden_in_game(True)
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
    unreal.SystemLibrary.execute_console_command(w, "RebuildNavigation")
    R["ok"]=True
except Exception as e:
    R["fatal"]=str(e); R["tb"]=traceback.format_exc()[-400:]
open("C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/esc_fix.json","w").write(json.dumps(R))
