# Tapa el hueco del descanso del 2o piso (entre el puente de la escalera y el corredor).
import unreal, json, traceback
out="C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups"; R={}
try:
    w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    for a in eas.get_all_level_actors():
        if a.get_actor_label()=="COL_Hac_Landing2P": eas.destroy_actor(a)
    cube=unreal.EditorAssetLibrary.load_asset("/Engine/BasicShapes/Cube")
    act=unreal.EditorLevelLibrary.spawn_actor_from_object(cube, unreal.Vector(-7250.0,-2075.0,420.0), unreal.Rotator(pitch=0.0,yaw=12.0,roll=0.0))
    act.set_actor_label("COL_Hac_Landing2P")
    act.set_actor_scale3d(unreal.Vector(5.2,5.8,0.2))  # ~520 x 580 x 20cm, top ~z430
    smc=act.get_component_by_class(unreal.StaticMeshComponent)
    smc.set_collision_profile_name("InvisibleWall")
    smc.set_collision_enabled(unreal.CollisionEnabled.QUERY_AND_PHYSICS)
    smc.set_editor_property("cast_shadow",False)
    smc.set_editor_property("can_ever_affect_navigation", True)
    act.set_actor_hidden_in_game(True)
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
    unreal.SystemLibrary.execute_console_command(w, "RebuildNavigation")
    R["ok"]=True
except Exception as e:
    R["err"]=str(e); R["tb"]=traceback.format_exc()[-300:]
open(out+"/fix_landing.json","w").write(json.dumps(R)); print("LAND", json.dumps(R))
