# 470_ue_test_cartelas_pie.py
# Proyecto: Jatun Wasi Nawpa Kay (tesis VR Quest 2)
# Fecha: 2026-11-24
# Proposito: prueba PIE (Convai APAGADO via 400) de las 24 cartelas con la MISMA logica del BP_Cartela:
#   PHASE="lista": etiquetas de las cartelas.
#   PHASE="apuntar" + IDX: lleva al pawn al NavMesh a ~2.5 m de la cartela IDX y orienta el
#     MotionControllerRightAim hacia ella (como si el visitante la apuntara).
#   PHASE="desviar": gira el control 120 grados (deja de apuntar) -> debe cerrarse.
#   PHASE="leer" + IDX: Abierto, panel visible, audio sonando de esa cartela.
import unreal, json, math, traceback
try:
    PHASE
except NameError:
    PHASE = "lista"
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/test470_%s.json" % PHASE
res = {"phase": PHASE, "err": None}
try:
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
    pawn = unreal.GameplayStatics.get_player_pawn(world, 0)
    carts = sorted([a for a in unreal.GameplayStatics.get_all_actors_of_class(world, unreal.Actor) if a.get_class().get_name() == "BP_Cartela_C"], key=lambda a: a.get_actor_label())
    aim = [c for c in pawn.get_components_by_class(unreal.SceneComponent) if c.get_name().startswith("MotionControllerRightAim")][0]
    if PHASE == "lista":
        res["cartelas"] = [a.get_actor_label() for a in carts]
    elif PHASE == "apuntar":
        a = carts[IDX]; casa = a.get_editor_property("Casa").translation
        res["cartela"] = a.get_actor_label()
        best = None
        for k in range(16):
            ang = k * math.pi / 8
            for dd in (100, 150, 200, 250, 300):
                r = unreal.NavigationSystemV1.project_point_to_navigation(world, unreal.Vector(casa.x + dd * math.cos(ang), casa.y + dd * math.sin(ang), casa.z), None, None, unreal.Vector(30, 30, 400))
                p = r[0] if isinstance(r, tuple) else r
                if p is None: continue
                h = unreal.SystemLibrary.line_trace_single(world, unreal.Vector(p.x, p.y, p.z + 140), casa, unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, False, [pawn, a], unreal.DrawDebugTrace.NONE, True)
                libre = not (h and h.to_tuple()[0])
                d = math.dist([p.x, p.y], [casa.x, casa.y])
                d3 = math.dist([p.x, p.y, p.z + 120], [casa.x, casa.y, casa.z])
                pen = (abs(d3 - 200) if d3 >= 90 else 500) + (0 if libre else 1000)   # ~2 m en 3D; vista libre preferida, no obligatoria (el BP no la exige)
                if best is None or pen < best[2]:
                    best = (p, d, pen, libre)
            if best and best[2] < 40: break
        if best is None:
            res["err"] = "sin punto con vista libre"
        else:
            p = best[0]
            pawn.set_actor_location(unreal.Vector(p.x, p.y, p.z + 90), False, True)
            L = aim.get_world_location()
            rot = unreal.MathLibrary.find_look_at_rotation(L, casa)
            aim.set_world_rotation(rot, False, False)
            res["dist"] = round(math.dist([L.x, L.y, L.z], [casa.x, casa.y, casa.z])); res["vista_libre"] = best[3]
    elif PHASE == "desviar":
        r0 = aim.get_world_rotation()
        aim.set_world_rotation(unreal.Rotator(r0.roll, r0.pitch, r0.yaw + 120), False, False)
    elif PHASE == "leer":
        a = carts[IDX]
        res["cartela"] = a.get_actor_label()
        res["abierto"] = a.get_editor_property("Abierto")
        for c in a.get_components_by_class(unreal.StaticMeshComponent):
            if c.get_name().startswith("Panel"): res["panel_visible"] = c.is_visible()
        for c in a.get_components_by_class(unreal.AudioComponent):
            if c.get_name().startswith("Audio"):
                s = c.get_editor_property("sound"); res["audio"] = s.get_name() if s else None; res["sonando"] = c.is_playing()
except Exception:
    res["err"] = traceback.format_exc()[:1200]
open(OUT, "w").write(json.dumps(res))
