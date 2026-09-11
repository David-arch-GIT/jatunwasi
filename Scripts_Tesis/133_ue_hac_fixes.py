# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-09-02
# Que hace: (UE) (1) Quita colision a los tapetes que bloquean (MUS_Alfombra_*, BALL_Alfombra*). (2) Aisla el audio
#   del salon de baile (AMB_SalaBaile) reduciendo su atenuacion para que no se oiga en planta baja. (3) Baja/ensancha
#   la rampa de escalera para asegurar contacto con el piso. Guarda.
# ------------------------------------------------------------
import unreal, json
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/hac_fixes.json"
res = {"tapetes": [], "audio": None, "rampa": None, "err": []}
eas = unreal.EditorActorSubsystem()
RUGS = ["mus_alfombra", "ball_alfombra"]
for a in eas.get_all_level_actors():
    low = a.get_actor_label().lower()
    # (1) tapetes
    if any(r in low for r in RUGS):
        for comp in a.get_components_by_class(unreal.StaticMeshComponent):
            try:
                comp.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
                comp.set_collision_profile_name("NoCollision")
                res["tapetes"].append(a.get_actor_label())
            except Exception as e:
                res["err"].append("rug %s: %s" % (low, str(e)[:30]))
    # (2) audio salon baile: reducir atenuacion (override en el componente)
    if low == "amb_salabaile":
        for ac in a.get_components_by_class(unreal.AudioComponent):
            try:
                ac.set_editor_property("override_attenuation", True)
                ov = ac.get_editor_property("attenuation_overrides")
                ov.set_editor_property("falloff_distance", 450.0)
                # radio interno (donde suena full) chico
                try:
                    ov.set_editor_property("radius", 250.0)
                except Exception:
                    pass
                ac.set_editor_property("attenuation_overrides", ov)
                res["audio"] = "AMB_SalaBaile falloff=450 (aislado 2do piso)"
            except Exception as e:
                res["err"].append("audio: %s" % str(e)[:60])
    # (3) rampa: bajar 40cm + ensanchar (asegurar contacto piso y captura)
    if a.get_actor_label() == "COL_HACV7_StairRamp":
        try:
            loc = a.get_actor_location()
            a.set_actor_location(unreal.Vector(loc.x, loc.y, loc.z - 40.0), False, False)
            sc = a.get_actor_scale3d()
            a.set_actor_scale3d(unreal.Vector(sc.x * 1.4, sc.y * 1.1, sc.z))
            res["rampa"] = "bajada 40cm + ensanchada x1.4"
        except Exception as e:
            res["err"].append("rampa: %s" % str(e)[:60])
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
open(OUT, "w").write(json.dumps(res, indent=1))
unreal.log("HAC FIXES tapetes=%d audio=%s rampa=%s" % (len(res["tapetes"]), res["audio"], res["rampa"]))
