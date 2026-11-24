# 449_ue_test_final_pie.py
# Proyecto: Jatun Wasi Nawpa Kay (tesis VR Quest 2)
# Fecha: 2026-11-24
# Proposito: prueba PIE (Convai apagado con 400) del FINAL en la Sala de Baile.
#   PHASE="entrar": lleva al pawn del corredor al centro del salon con barrido (dispara Trig_HaciendaFin).
#   PHASE="leer": valores TF/TL/T0 del MPC_Final, tiempo de juego, posicion/giro de Adela, visibilidad
#     de FadeFinal y CreditosFinal del pawn, y si se mostro el panel viejo de creditos (no debe).
import unreal, json, traceback
try:
    PHASE
except NameError:
    PHASE = "leer"
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/test449_%s.json" % PHASE
res = {"phase": PHASE, "err": None}
try:
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
    pawn = unreal.GameplayStatics.get_player_pawn(world, 0)
    if PHASE == "entrar":
        pawn.set_actor_location(unreal.Vector(-7700, -1925, 445), False, True)
        pawn.set_actor_location(unreal.Vector(-8375, -1600, 445), True, True)
    mpc = unreal.load_asset("/Game/JWN/FX/MPC_Final")
    res["t_juego"] = round(unreal.GameplayStatics.get_time_seconds(world), 1)
    for p in ("TF", "TL", "T0"):
        res[p] = round(unreal.MaterialLibrary.get_scalar_parameter_value(world, mpc, p), 1)
    for a in unreal.GameplayStatics.get_all_actors_of_class(world, unreal.Actor):
        lb = a.get_actor_label()
        if lb == "Adela_Convai":
            L = a.get_actor_location(); R = a.get_actor_rotation(); res["adela"] = [round(L.x), round(L.y), round(L.z), round(R.yaw, 1)]
        if lb == "Creditos_Panel":
            res["panel_viejo_oculto"] = a.get_editor_property("hidden")
    for c in pawn.get_components_by_class(unreal.StaticMeshComponent):
        if c.get_name().startswith(("FadeFinal", "CreditosFinal")):
            res[c.get_name()] = c.is_visible()
    L = pawn.get_actor_location(); res["pawn"] = [round(L.x), round(L.y), round(L.z)]
except Exception:
    res["err"] = traceback.format_exc()[:900]
open(OUT, "w").write(json.dumps(res))
