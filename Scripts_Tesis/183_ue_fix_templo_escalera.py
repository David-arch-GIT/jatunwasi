# Fix: umbral de entrada del templo (piso invisible) + rampa de navegacion de la escalera hacienda.
import unreal, json, math, traceback
out="C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups"; R={}
try:
    w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    cube=unreal.EditorAssetLibrary.load_asset("/Engine/BasicShapes/Cube")
    def inv_floor(label, loc, scale, rot):
        for a in eas.get_all_level_actors():
            if a.get_actor_label()==label: eas.destroy_actor(a)
        act=unreal.EditorLevelLibrary.spawn_actor_from_object(cube, loc, rot)
        act.set_actor_label(label); act.set_actor_scale3d(scale)
        smc=act.get_component_by_class(unreal.StaticMeshComponent)
        smc.set_collision_profile_name("InvisibleWall")
        smc.set_collision_enabled(unreal.CollisionEnabled.QUERY_AND_PHYSICS)
        smc.set_editor_property("cast_shadow",False)
        smc.set_editor_property("can_ever_affect_navigation", True)
        act.set_actor_hidden_in_game(True)
        return act
    # 1) TEMPLO: piso invisible cubriendo el umbral (y 9500-10600, x +/-550), al nivel del piso del templo (~z2)
    inv_floor("COL_Templo_Umbral", unreal.Vector(50.0,10050.0,-3.0), unreal.Vector(11.0,11.0,0.2),
              unreal.Rotator(pitch=0.0,yaw=0.0,roll=0.0))
    R["templo_umbral"]=True
    # 2) ESCALERA HACIENDA: rampa de navegacion invisible continua (base z58 -> top z410)
    # base ~(-7430,-2850,58), top ~(-7590,-2300,410); azimut 106, pendiente 31.6
    inv_floor("COL_Hac_EscaleraNav", unreal.Vector(-7510.0,-2575.0,234.0), unreal.Vector(6.4,3.8,0.2),
              unreal.Rotator(pitch=31.6,yaw=106.0,roll=0.0))
    R["escalera_rampa"]=True
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
    unreal.SystemLibrary.execute_console_command(w, "RebuildNavigation")
    R["rebuild"]=True
except Exception as e:
    R["err"]=str(e); R["tb"]=traceback.format_exc()[-300:]
open(out+"/fix_templo_esc.json","w").write(json.dumps(R)); print("FIX", json.dumps(R))
