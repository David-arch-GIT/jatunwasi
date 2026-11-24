# 455_ue_auditoria_pie.py
# Proyecto: Jatun Wasi Nawpa Kay (tesis VR Quest 2)
# Fecha: 2026-11-24
# Proposito: auditoria PIE consolidada pre-APK (con Convai APAGADO via 400 convai_off). Fases:
#   PHASE="estado": barreras BAR_Convento/BAR_Hacienda (colision/oculta), disparadores del Gestor
#     (componentes caja: centro y extension), posicion del pawn.
#   PHASE="tp" + TP=(x,y): lleva al pawn al NavMesh en (x,y) con barrido (dispara overlaps).
#   PHASE="pozo": coloca al pawn a ~3 m del pozo (tag PozoDeseos) y lanza el mismo rayo de 9 m que el
#     BP; verifica que el actor golpeado tiene el tag.
import unreal, json, math, traceback
try:
    PHASE
except NameError:
    PHASE = "estado"
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/test455_%s.json" % PHASE
res = {"phase": PHASE, "err": None}
try:
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
    pawn = unreal.GameplayStatics.get_player_pawn(world, 0)
    acts = unreal.GameplayStatics.get_all_actors_of_class(world, unreal.Actor)
    def nav(x, y, z=100):
        r = unreal.NavigationSystemV1.project_point_to_navigation(world, unreal.Vector(x, y, z), None, None, unreal.Vector(200, 200, 600))
        return r[0] if isinstance(r, tuple) else r
    if PHASE == "estado":
        for a in acts:
            lb = a.get_actor_label()
            if lb in ("BAR_Convento", "BAR_Hacienda"):
                res[lb] = {"colision": a.get_actor_enable_collision(), "oculta": a.get_editor_property("hidden")}
            if lb == "GestorRecorrido_Inst":
                tr = {}
                for c in a.get_components_by_class(unreal.BoxComponent):
                    L = c.get_world_location(); E = c.get_scaled_box_extent()
                    tr[c.get_name()] = [round(L.x), round(L.y), round(L.z), round(E.x), round(E.y), round(E.z)]
                res["trigs"] = tr
        L = pawn.get_actor_location(); res["pawn"] = [round(L.x), round(L.y), round(L.z)]
    elif PHASE == "tp":
        p = nav(TP[0], TP[1], TP[2] if len(TP) > 2 else 100)
        if p is None:
            res["err"] = "sin NavMesh en %s" % (TP,)
        else:
            pawn.set_actor_location(unreal.Vector(p.x, p.y, p.z + 90), True, True)
            L = pawn.get_actor_location(); res["pawn"] = [round(L.x), round(L.y), round(L.z)]
    elif PHASE == "pozo":
        pozo = [a for a in acts if a.actor_has_tag("PozoDeseos")]
        res["n_pozo"] = len(pozo)
        if pozo:
            P = pozo[0].get_actor_location(); res["pozo"] = [round(P.x), round(P.y), round(P.z)]
            best = None
            for k in range(12):
                ang = k * math.pi / 6
                q = nav(P.x + 300 * math.cos(ang), P.y + 300 * math.sin(ang), P.z)
                if q is not None and abs(q.z - P.z) < 150:
                    best = q; break
            res["desde"] = [round(best.x), round(best.y), round(best.z)] if best else None
            if best:
                pawn.set_actor_location(unreal.Vector(best.x, best.y, best.z + 90), False, True)
                o = unreal.Vector(best.x, best.y, best.z + 120)
                d = unreal.Vector(P.x - o.x, P.y - o.y, (P.z + 40) - o.z); n = math.sqrt(d.x ** 2 + d.y ** 2 + d.z ** 2)
                e = unreal.Vector(o.x + d.x / n * 900, o.y + d.y / n * 900, o.z + d.z / n * 900)
                h = unreal.SystemLibrary.line_trace_single(world, o, e, unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, False, [pawn], unreal.DrawDebugTrace.NONE, True)
                t = h.to_tuple() if h else None
                ha = t[9] if t else None
                res["golpea"] = ha.get_actor_label() if ha else None
                res["tiene_tag"] = bool(ha and ha.actor_has_tag("PozoDeseos"))
except Exception:
    res["err"] = traceback.format_exc()[:1200]
open(OUT, "w").write(json.dumps(res))
