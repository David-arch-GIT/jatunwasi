# 498_ue_test_movimiento_spawn_pie.py
# Proyecto: Jatun Wasi Nawpa Kay (tesis VR Quest 2)
# Fecha: 2026-11-24
# Proposito: (PIE, Convai apagado) diagnosticar "no me deja mover" reproduciendo EXACTAMENTE la logica del
#   Tick de BP_XRPawn en la posicion real del pawn: (1) ProjectPointToNavigation(actor, 300/300/400) del lugar
#   seguro; (2) en 8 direcciones: LineTraceByChannel(Visibility, simple, ignora self) de actor+60 a +45 cm
#   -> si choca, contra que; (3) ProjectPointToNavigation(actor + dir*3.3 cm, 40/40/300).
import unreal, json, math, traceback
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/test498.json"
res = {"err": None}
try:
    w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
    pawn = unreal.GameplayStatics.get_player_pawn(w, 0)
    L = pawn.get_actor_location(); res["pawn"] = [round(L.x), round(L.y), round(L.z)]
    def proj(p, e):
        r = unreal.NavigationSystemV1.project_point_to_navigation(w, p, None, None, e)
        q = r[0] if isinstance(r, tuple) else r
        return [round(q.x), round(q.y), round(q.z)] if q else None
    res["lugar_seguro_proy"] = proj(L, unreal.Vector(300, 300, 400))
    dirs = {}
    for k in range(8):
        a = k * math.pi / 4; dx, dy = math.cos(a), math.sin(a)
        s = unreal.Vector(L.x, L.y, L.z + 60); e = unreal.Vector(L.x + dx * 45, L.y + dy * 45, L.z + 60)
        h = unreal.SystemLibrary.line_trace_single(w, s, e, unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, False, [], unreal.DrawDebugTrace.NONE, True)
        t = h.to_tuple() if h else None
        hit = bool(t and t[0])
        quien = None
        if hit:
            ha = t[9]; hc = t[10]
            quien = (ha.get_actor_label() if ha else "?") + "/" + (hc.get_name() if hc else "?") + " dist=" + str(round(t[3], 1)) + " inicial=" + str(t[1])
        paso = proj(unreal.Vector(L.x + dx * 3.3, L.y + dy * 3.3, L.z), unreal.Vector(40, 40, 300))
        dirs[str(k * 45)] = {"bloquea": hit, "quien": quien, "nav_paso": paso}
    res["dirs"] = dirs
    ps = [a for a in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.PlayerStart)]
    res["playerstarts"] = [[a.get_actor_label(), [round(a.get_actor_location().x), round(a.get_actor_location().y), round(a.get_actor_location().z)]] for a in ps]
except Exception:
    res["err"] = traceback.format_exc()[:1200]
open(OUT, "w").write(json.dumps(res, indent=1))
