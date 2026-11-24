# Proyecto: JatunWasi Nawpaqay - Tesis
# Fecha: 2026-11-09  ARREGLO de contencion (0 fuga + patio hacienda). TODO INVISIBLE.
#  1) Ground_Cochabamba -> can_ever_affect_navigation = False (borra NavMesh del bosque)
#  2) Piso de colision invisible en el PATIO de la hacienda (z58, al ras) -> no te caes
#  3) RebuildNavigation
import unreal, json, traceback
out="C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups"; R={}
try:
    w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    # 1) excluir terreno de navegacion
    for a in eas.get_all_level_actors():
        if a.get_actor_label()=="Ground_Cochabamba":
            for c in a.get_components_by_class(unreal.StaticMeshComponent):
                c.set_editor_property("can_ever_affect_navigation", False)
            R["terreno_excluido"]=True
    # 2) piso de colision invisible en el patio (cubo plano, rotado 12 como la hacienda)
    # quitar uno previo si existe
    for a in eas.get_all_level_actors():
        if a.get_actor_label()=="COL_Hac_PatioFloor":
            eas.destroy_actor(a)
    cube=unreal.EditorAssetLibrary.load_asset("/Engine/BasicShapes/Cube")
    loc=unreal.Vector(-6900.0,-1350.0,53.0)  # top ~z58 (cubo 100*0.1=10cm, centro 53 -> top 58)
    act=unreal.EditorLevelLibrary.spawn_actor_from_object(cube, loc, unreal.Rotator(pitch=0.0,yaw=12.0,roll=0.0))
    act.set_actor_label("COL_Hac_PatioFloor")
    act.set_actor_scale3d(unreal.Vector(32.0,10.0,0.1))  # ~3200 x 1000 x 10cm
    smc=act.get_component_by_class(unreal.StaticMeshComponent)
    smc.set_collision_profile_name("InvisibleWall")
    smc.set_collision_enabled(unreal.CollisionEnabled.QUERY_AND_PHYSICS)
    smc.set_editor_property("cast_shadow",False)
    smc.set_editor_property("can_ever_affect_navigation", True)
    act.set_actor_hidden_in_game(True)
    R["patio_floor"]=True
    # guardar nivel
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
    # 3) reconstruir navegacion
    unreal.SystemLibrary.execute_console_command(w, "RebuildNavigation")
    R["rebuild_issued"]=True
except Exception as e:
    R["err"]=str(e); R["tb"]=traceback.format_exc()[-400:]
open(out+"/fix_contencion.json","w").write(json.dumps(R)); print("FIX", json.dumps(R))
