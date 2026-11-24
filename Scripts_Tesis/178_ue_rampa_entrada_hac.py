# Rampa invisible de entrada a la hacienda (camino z~0 -> apron z59) para que se pueda entrar caminando.
import unreal, json, traceback
out="C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups"; R={}
try:
    w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    for a in eas.get_all_level_actors():
        if a.get_actor_label()=="COL_Rampa_Entrada_V2": eas.destroy_actor(a)
    cube=unreal.EditorAssetLibrary.load_asset("/Engine/BasicShapes/Cube")
    # rampa sobre el eje de entrada: de (~-7250,450,z0) sube a (~-7380,120,z59)
    act=unreal.EditorLevelLibrary.spawn_actor_from_object(cube, unreal.Vector(-7190,400,29), unreal.Rotator(pitch=4.75,yaw=-122.0,roll=0.0))
    act.set_actor_label("COL_Rampa_Entrada_V2")
    act.set_actor_scale3d(unreal.Vector(7.5,5.0,0.2))
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
open(out+"/rampa_entrada.json","w").write(json.dumps(R)); print("RAMPA", json.dumps(R))
