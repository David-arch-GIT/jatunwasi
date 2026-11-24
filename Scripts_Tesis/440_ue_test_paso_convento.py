# 440_ue_test_paso_convento.py
# Proyecto: Jatun Wasi Nawpa Kay (tesis VR Quest 2)
# Fecha: 2026-11-24
# Proposito: prueba PIE (Convai apagado) de que el mobiliario nuevo del convento NO bloquea el paso:
#   replica la logica de locomocion (rayo 45 cm a 60 cm de altura + proyeccion NavMesh) caminando por
#   el pasillo del refectorio, por el portico oeste y alrededor del pozo. Reporta cm recorridos y tope.
import unreal, json, math, traceback
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/test440.json"
res = {"err": None}
try:
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
    pawn = unreal.GameplayStatics.get_player_pawn(world, 0)
    def tp(x, y):
        r = unreal.NavigationSystemV1.project_point_to_navigation(world, unreal.Vector(x, y, 50), None, None, unreal.Vector(100, 100, 300))
        p = r[0] if isinstance(r, tuple) else r
        if p is None: return False
        pawn.set_actor_location(p, False, False); return True
    def walk(dx, dy, steps, sl=4.0):
        n = math.hypot(dx, dy); dx, dy = dx / n, dy / n; moved = 0; stop = None
        for i in range(steps):
            c = pawn.get_actor_location(); s = unreal.Vector(c.x, c.y, c.z + 60)
            h = unreal.SystemLibrary.line_trace_single(world, s, unreal.Vector(s.x + dx * 45, s.y + dy * 45, s.z), unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, False, [pawn], unreal.DrawDebugTrace.NONE, True)
            if h is not None and h.to_tuple()[0]:
                t = h.to_tuple(); stop = "MURO:" + (t[10].get_owner().get_actor_label() if t[10] else "?"); break
            r = unreal.NavigationSystemV1.project_point_to_navigation(world, unreal.Vector(c.x + dx * sl, c.y + dy * sl, c.z), None, None, unreal.Vector(40, 40, 300))
            p = r[0] if isinstance(r, tuple) else r
            if p is None: stop = "BORDE_NAV"; break
            pawn.set_actor_location(p, False, False); moved += sl
        e = pawn.get_actor_location()
        return {"cm": round(moved), "tope": stop, "fin": [round(e.x), round(e.y)]}
    T = {}
    T["refectorio_pasillo_norte"] = walk(0, 1, 400) if tp(7700, 4500) else "sin_nav"
    T["portico_oeste_norte"] = walk(0, 1, 400) if tp(4800, 4300) else "sin_nav"
    T["patio_hacia_pozo"] = walk(0, 1, 150) if tp(6250, 3900) else "sin_nav"
    T["refectorio_hacia_mesa_este"] = walk(1, 0, 100) if tp(7700, 5000) else "sin_nav"
    res["tests"] = T
except Exception:
    res["err"] = traceback.format_exc()[:900]
open(OUT, "w").write(json.dumps(res))
