# 409_ue_test_sonidos_noche_pie.py
# Proyecto: Jatun Wasi Nawpa Kay (tesis VR Quest 2)
# Fecha: 2026-11-24
# Proposito: verificar en PIE (con Convai APAGADO via 400 convai_off) los sonidos nocturnos:
#   PHASE="a": componente Pasos del pawn (sonido, activo, volumen 0 quieto), grillos/lechuzas
#     presentes y sonando cuando el pawn esta en rango; luego teletransporta el pawn dentro de
#     Trig_Templo para disparar el desbloqueo + campanas.
#   PHASE="b": (segundos despues) estado de la barrera del Convento (debe estar abierta) y
#     cantidad de sonidos activos en el dispositivo de audio.
import unreal, json, traceback
try:
    PHASE
except NameError:
    PHASE = "a"
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/test409_%s.json" % PHASE
res = {"phase": PHASE, "err": None}
try:
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
    pawn = unreal.GameplayStatics.get_player_pawn(world, 0)
    res["pawn"] = pawn.get_class().get_name() if pawn else None
    if PHASE == "a":
        pc = [c for c in pawn.get_components_by_class(unreal.AudioComponent) if c.get_name().startswith("Pasos")]
        if pc:
            c = pc[0]
            res["pasos"] = {"sound": c.get_editor_property("sound").get_name() if c.get_editor_property("sound") else None,
                            "playing": c.is_playing(), "vol": c.get_editor_property("volume_multiplier")}
        amb = {}
        for a in unreal.GameplayStatics.get_all_actors_of_class(world, unreal.AmbientSound):
            lb = a.get_actor_label()
            if lb.startswith("NOCHE_"):
                ac = a.get_editor_property("audio_component")
                amb[lb] = {"sound": ac.get_editor_property("sound").get_name() if ac.get_editor_property("sound") else None,
                           "active": ac.is_active(), "playing": ac.is_playing()}
        res["amb"] = amb
        # mover al pawn junto a un campo con grillos y medir
        g = next(a for a in unreal.GameplayStatics.get_all_actors_of_class(world, unreal.AmbientSound) if a.get_actor_label() == "NOCHE_Grillos_3")
        L = g.get_actor_location()
        res["grillo3_loc"] = [round(L.x), round(L.y)]
        # disparar el desbloqueo del Templo: llevar al pawn al centro del Trig_Templo
        r = unreal.NavigationSystemV1.project_point_to_navigation(world, unreal.Vector(50, 9300, 100), None, None, unreal.Vector(200, 200, 400))
        loc = r[0] if isinstance(r, tuple) else r
        pawn.set_actor_location(loc, False, True)
        res["tp"] = [round(loc.x), round(loc.y), round(loc.z)]
    else:
        bar = next(a for a in unreal.GameplayStatics.get_all_actors_of_class(world, unreal.Actor) if a.get_actor_label() == "BAR_Convento")
        res["bar_convento_hidden"] = bar.is_hidden_ed() if False else bar.get_editor_property("hidden") if hasattr(bar, "hidden") else None
        try:
            res["bar_convento_hidden"] = bar.get_editor_property("b_hidden")
        except Exception:
            pass
        res["bar_convento_collision"] = bar.get_actor_enable_collision()
except Exception:
    res["err"] = traceback.format_exc()[:900]
open(OUT, "w").write(json.dumps(res, indent=1))
