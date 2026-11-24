# 446_ue_test_subida_salon_pie.py
# Proyecto: Jatun Wasi Nawpa Kay (tesis VR Quest 2)
# Fecha: 2026-11-24
# Proposito: prueba PIE (Convai apagado) de la SUBIDA REAL a la Sala de Baile: el pawn sigue los puntos
#   del camino del NavMesh (entrada hacienda -> salon 2do piso) moviendose con la MISMA logica del
#   joystick de BP_XRPawn (rayo 45 cm a 60 cm de altura + proyeccion al NavMesh extent 40/40/300,
#   pasos de 4 cm). Reporta si llega, donde se frena y contra que.
import unreal, json, math, traceback
try:
    GUIADO
except NameError:
    GUIADO = False
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/test446.json"
res = {"err": None}
try:
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
    pawn = unreal.GameplayStatics.get_player_pawn(world, 0)
    start = unreal.Vector(-7317, -1100, 60); goal = unreal.Vector(-8375, -1600, 430)
    r = unreal.NavigationSystemV1.project_point_to_navigation(world, start, None, None, unreal.Vector(100, 100, 300))
    pawn.set_actor_location(r[0] if isinstance(r, tuple) else r, False, False)
    path = unreal.NavigationSystemV1.find_path_to_location_synchronously(world, pawn.get_actor_location(), goal)
    pts = list(path.get_editor_property("path_points"))
    # v2: tras subir, caminar como persona: centro del corredor y giro por la abertura del salon (x~-8000)
    if GUIADO:
        cut = [p for p in pts if p.z > 400]
        first_up = pts.index(cut[0]) if cut else len(pts)
        R = json.load(open(r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/ruta_libre.json"))["ruta"]   # v3: ruta con holgura (447)
        pts = pts[:first_up + 1] + [unreal.Vector(x, y, 440) for x, y in R]
    res["path_pts"] = [[round(p.x), round(p.y), round(p.z)] for p in pts]
    stop = None; steps = 0
    for tgt in pts[1:]:
        for _ in range(3000):
            c = pawn.get_actor_location()
            dx, dy = tgt.x - c.x, tgt.y - c.y; d = math.hypot(dx, dy)
            if d < 8: break
            dx, dy = dx / d, dy / d
            s = unreal.Vector(c.x, c.y, c.z + 60)
            h = unreal.SystemLibrary.line_trace_single(world, s, unreal.Vector(s.x + dx * 45, s.y + dy * 45, s.z), unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, False, [pawn], unreal.DrawDebugTrace.NONE, True)
            if h is not None and h.to_tuple()[0]:
                t = h.to_tuple(); stop = ["MURO", t[10].get_owner().get_actor_label() if t[10] else "?", [round(c.x), round(c.y), round(c.z)]]; break
            q = unreal.NavigationSystemV1.project_point_to_navigation(world, unreal.Vector(c.x + dx * 4, c.y + dy * 4, c.z), None, None, unreal.Vector(40, 40, 300))
            q = q[0] if isinstance(q, tuple) else q
            if q is None:
                stop = ["BORDE_NAV", None, [round(c.x), round(c.y), round(c.z)]]; break
            pawn.set_actor_location(q, False, False); steps += 1
        if stop: break
    e = pawn.get_actor_location()
    res.update({"llego": stop is None and math.dist([e.x, e.y], [goal.x, goal.y]) < 60, "fin": [round(e.x), round(e.y), round(e.z)], "tope": stop, "metros": round(steps * 4 / 100, 1)})
except Exception:
    res["err"] = traceback.format_exc()[:900]
open(OUT, "w").write(json.dumps(res))
