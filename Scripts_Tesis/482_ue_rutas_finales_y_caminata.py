# 482_ue_rutas_finales_y_caminata.py
# Proyecto: Jatun Wasi Nawpa Kay (tesis VR Quest 2)
# Fecha: 2026-11-24
# Proposito: (solo lectura) con el NavMesh ya conectado (481), obtener los caminos COMPLETOS de las 3 etapas
#   (Plaza->Templo, Templo->Convento, Convento->Hacienda) y SIMULAR la locomocion real del visitante por
#   cada uno (rayo 45 cm a +60; proyeccion 40/40/300; pasos 4 cm; barreras ignoradas = abiertas; con
#   GUARDA anti-bucle). Calcula estaciones de Adela: Templo/Hacienda al final del camino (a un costado);
#   Convento ANTES de las puertas (para que Adela no las atraviese cerradas). Escribe rutas_finales.json.
import unreal, json, math, traceback
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/rutas_finales.json"
res = {"err": None, "rutas": {}, "caminata": {}, "estaciones": {}}
try:
    w = unreal.EditorLevelLibrary.get_editor_world()
    acts = {a.get_actor_label(): a for a in unreal.EditorLevelLibrary.get_all_level_actors()}
    ign = [acts["BAR_Convento"], acts["BAR_Hacienda"]]
    def proj(x, y, z=100, e=(60, 60, 600)):
        r = unreal.NavigationSystemV1.project_point_to_navigation(w, unreal.Vector(x, y, z), None, None, unreal.Vector(*e))
        return r[0] if isinstance(r, tuple) else r
    def camino(a, b):
        p = unreal.NavigationSystemV1.find_path_to_location_synchronously(w, a, b)
        return [unreal.Vector(v.x, v.y, v.z) for v in p.get_editor_property("path_points")] if p else []
    def caminar(pts):
        cur = pts[0]; rec = 0.0
        for tgt in pts[1:]:
            pasos = 0; maxp = int(math.hypot(tgt.x - cur.x, tgt.y - cur.y) / 4 * 2) + 60; quieto = 0
            while math.hypot(tgt.x - cur.x, tgt.y - cur.y) > 8:
                pasos += 1
                if pasos > maxp or quieto > 15:
                    return {"llego": False, "tope": [round(cur.x), round(cur.y), round(cur.z)], "por": "no avanza", "m": round(rec / 100, 1)}
                dx, dy = tgt.x - cur.x, tgt.y - cur.y; n = math.hypot(dx, dy); dx /= n; dy /= n
                h = unreal.SystemLibrary.line_trace_single(w, unreal.Vector(cur.x, cur.y, cur.z + 60), unreal.Vector(cur.x + dx * 45, cur.y + dy * 45, cur.z + 60), unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, False, ign, unreal.DrawDebugTrace.NONE, True)
                if h and h.to_tuple()[0]:
                    t = h.to_tuple()
                    return {"llego": False, "tope": [round(cur.x), round(cur.y), round(cur.z)], "por": "choca:" + (t[9].get_actor_label() if t[9] else "?"), "m": round(rec / 100, 1)}
                p = proj(cur.x + dx * 4, cur.y + dy * 4, cur.z, (40, 40, 300))
                if p is None:
                    return {"llego": False, "tope": [round(cur.x), round(cur.y), round(cur.z)], "por": "sin NavMesh", "m": round(rec / 100, 1)}
                av = math.hypot(p.x - cur.x, p.y - cur.y); quieto = quieto + 1 if av < 0.5 else 0
                rec += av; cur = p
        return {"llego": True, "m": round(rec / 100, 1)}
    P = {"plaza": proj(383, -950), "templo": proj(50, 9550), "convento": proj(5950, 4250), "hacienda": proj(-7250, -820)}
    for a, b in (("plaza", "templo"), ("templo", "convento"), ("convento", "hacienda")):
        pp = camino(P[a], P[b])
        res["rutas"][a + "_" + b] = [[round(v.x), round(v.y), round(v.z)] for v in pp]
        res["caminata"][a + "_" + b] = caminar(pp) if len(pp) > 1 else {"llego": False, "por": "sin camino"}
    def libre(v):
        for kk in range(8):
            ang = kk * math.pi / 4
            h = unreal.SystemLibrary.line_trace_single(w, unreal.Vector(v.x, v.y, v.z + 100), unreal.Vector(v.x + 50 * math.cos(ang), v.y + 50 * math.sin(ang), v.z + 100), unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, False, [], unreal.DrawDebugTrace.NONE, True)
            if h and h.to_tuple()[0]: return False
        return True
    def estacion_en(pp, s_desde_final):
        # punto del camino a s_desde_final cm antes del final + desplazamiento lateral
        acc = 0.0; q = pp[-1]; d = (pp[-1].x - pp[-2].x, pp[-1].y - pp[-2].y)
        for i in range(len(pp) - 1, 0, -1):
            s = math.hypot(pp[i].x - pp[i - 1].x, pp[i].y - pp[i - 1].y)
            if acc + s >= s_desde_final:
                t = (s_desde_final - acc) / s
                q = unreal.Vector(pp[i].x + (pp[i - 1].x - pp[i].x) * t, pp[i].y + (pp[i - 1].y - pp[i].y) * t, pp[i].z)
                d = (pp[i].x - pp[i - 1].x, pp[i].y - pp[i - 1].y); break
            acc += s
        n = math.hypot(*d) or 1; dx, dy = d[0] / n, d[1] / n
        for side in (1, -1):
            for off in (220, 180, 260, 150):
                v = proj(q.x + (-dy) * side * off, q.y + dx * side * off, q.z, (20, 20, 300))
                if v and abs(v.z - q.z) < 60 and libre(v):
                    return {"camino": [round(q.x), round(q.y), round(q.z)], "pos": [round(v.x), round(v.y), round(v.z)], "yaw_llegada": round(math.degrees(math.atan2(-dy, -dx)), 1)}
        return {"camino": [round(q.x), round(q.y), round(q.z)], "pos": None}
    def recorte(pp, s_desde_final):
        # camino hasta s_desde_final cm antes del final
        tot = sum(math.hypot(pp[i].x - pp[i - 1].x, pp[i].y - pp[i - 1].y) for i in range(1, len(pp)))
        objetivo = tot - s_desde_final; acc = 0.0; out = [pp[0]]
        for i in range(1, len(pp)):
            s = math.hypot(pp[i].x - pp[i - 1].x, pp[i].y - pp[i - 1].y)
            if acc + s >= objetivo:
                t = (objetivo - acc) / s
                out.append(unreal.Vector(pp[i - 1].x + (pp[i].x - pp[i - 1].x) * t, pp[i - 1].y + (pp[i].y - pp[i - 1].y) * t, pp[i].z)); break
            out.append(pp[i]); acc += s
        return out
    rt = {k: [unreal.Vector(*v) for v in vv] for k, vv in res["rutas"].items()}
    # puertas del convento: distancia del camino a ellas
    dA = acts["PUERTA_Convento_A"].get_actor_location()
    pc = rt["templo_convento"]
    acc = 0.0; s_puerta = None
    tot = sum(math.hypot(pc[i].x - pc[i - 1].x, pc[i].y - pc[i - 1].y) for i in range(1, len(pc)))
    for i in range(1, len(pc)):
        s = math.hypot(pc[i].x - pc[i - 1].x, pc[i].y - pc[i - 1].y)
        for k in range(0, int(s // 20) + 1):
            t = min(1.0, k * 20 / s) if s > 0 else 0
            x = pc[i - 1].x + (pc[i].x - pc[i - 1].x) * t; y = pc[i - 1].y + (pc[i].y - pc[i - 1].y) * t
            if math.hypot(x - dA.x, y - dA.y) < 150 and s_puerta is None: s_puerta = acc + s * t
        acc += s
    res["convento_s_puerta_desde_final"] = round(tot - s_puerta) if s_puerta else None
    res["estaciones"]["templo"] = estacion_en(rt["plaza_templo"], 0)
    sp = (tot - s_puerta + 700) if s_puerta else 0
    res["estaciones"]["convento"] = estacion_en(pc, sp)
    res["convento_ruta_recortada_hasta"] = round(sp)
    res["estaciones"]["hacienda"] = estacion_en(rt["convento_hacienda"], 0)
except Exception:
    res["err"] = traceback.format_exc()[:1500]
open(OUT, "w").write(json.dumps(res))
