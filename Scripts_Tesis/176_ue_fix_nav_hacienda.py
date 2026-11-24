# Proyecto: JatunWasi Nawpaqay - Tesis
# Fecha: 2026-11-09  Hace que los PISOS REALES de la hacienda generen NavMesh (a su altura
#  real z58), en vez de depender del terreno (bug: nav estaba bajo el piso). Luego rebuild.
import unreal, json, traceback
out="C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups"; R={"set":[]}
try:
    w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    # pisos reales de la hacienda que deben generar navegacion
    floors=["HACV7_EXP_Foundation_Floors","HACV7_EntranceApron_Final",
            "COL_HACV7_UpperCorridor","COL_Baile_navfloor","COL_HACV7_StairRamp",
            "COL_Puente_Escalera2P"]
    for a in eas.get_all_level_actors():
        if a.get_actor_label() in floors:
            for c in a.get_components_by_class(unreal.StaticMeshComponent):
                c.set_editor_property("can_ever_affect_navigation", True)
            R["set"].append(a.get_actor_label())
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
    unreal.SystemLibrary.execute_console_command(w, "RebuildNavigation")
    R["rebuild"]=True
except Exception as e:
    R["err"]=str(e); R["tb"]=traceback.format_exc()[-400:]
open(out+"/fix_nav_hac.json","w").write(json.dumps(R)); print("FIXNAVHAC", json.dumps(R))
