# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-09-02
# Que hace: (UE) Arregla la escalera de la hacienda como el templo/convento: ACTIVA la colision de la escalera visual
#   real (tiene body_setup) usando complex-as-simple (escalones reales caminables) y DESACTIVA la rampa a 30 que no jala.
#   Mantiene el landing. Guarda.
# ------------------------------------------------------------
import unreal, json
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/escalera_real.json"
res = {"acciones": [], "err": []}
eas = unreal.EditorActorSubsystem()
for a in eas.get_all_level_actors():
    lbl = a.get_actor_label()
    if lbl == "HACV7_EXP_Staircase":
        for comp in a.get_components_by_class(unreal.StaticMeshComponent):
            try:
                # usar la geometria del mesh como colision (complex as simple = escalones reales)
                m = comp.get_editor_property("static_mesh")
                if m:
                    bs = m.get_editor_property("body_setup")
                    if bs:
                        bs.set_editor_property("collision_trace_flag", unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
                comp.set_collision_enabled(unreal.CollisionEnabled.QUERY_AND_PHYSICS)
                comp.set_collision_profile_name("BlockAll")
                res["acciones"].append("escalera visual: colision ACTIVADA (complex-as-simple)")
            except Exception as e:
                res["err"].append("stair: %s" % str(e)[:60])
    elif lbl == "COL_HACV7_StairRamp":
        for comp in a.get_components_by_class(unreal.StaticMeshComponent):
            try:
                comp.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
                res["acciones"].append("rampa 30: DESACTIVADA")
            except Exception as e:
                res["err"].append("ramp: %s" % str(e)[:60])
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
open(OUT, "w").write(json.dumps(res, indent=1))
unreal.log("ESCALERA REAL %s" % res["acciones"])
