# 480_ue_simular_caminata_tramos.py
# Proyecto: Jatun Wasi Nawpa Kay (tesis VR Quest 2)
# Fecha: 2026-11-24
# Proposito: (solo lectura, mundo del editor) simular la LOCOMOCION REAL del visitante (BP_XRPawn: rayo
#   45 cm adelante a +60 cm; proyeccion NavMesh extent 40/40/300; pasos de 4 cm) por los tramos dudosos
#   del NavMesh: plaza -> barrera Convento y plaza -> barrera Hacienda (barreras ignoradas = abiertas).
#   Ademas muestrea el NavMesh cada 25 cm sobre la recta para ver huecos (extent 5/5/300).
import unreal, json, math, traceback
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/sim_caminata.json"
res = {"err": None, "tramos": {}}
try:
    w = unreal.EditorLevelLibrary.get_editor_world()
    acts = {a.get_actor_label(): a for a in unreal.EditorLevelLibrary.get_all_level_actors()}
    ign = [acts["BAR_Convento"], acts["BAR_Hacienda"]]
    def proj(x, y, z, e):
        r = unreal.NavigationSystemV1.project_point_to_navigation(w, unreal.Vector(x, y, z), None, None, unreal.Vector(*e))
        return r[0] if isinstance(r, tuple) else r
    def caminar(pts):
        cur = proj(pts[0][0], pts[0][1], 100, (60, 60, 600)); recorrido = 0
        for (tx, ty) in pts[1:]:
            pasos = 0; maxp = int(math.hypot(tx - cur.x, ty - cur.y) / 4 * 2) + 50; quieto = 0   # GUARDA anti-bucle (480 colgo el editor sin esto)
            while math.hypot(tx - cur.x, ty - cur.y) > 8:
                pasos += 1
                if pasos > maxp or quieto > 15:
                    return {"llego": False, "tope": [round(cur.x), round(cur.y), round(cur.z)], "por": "no avanza (proyeccion lo regresa)", "m": round(recorrido / 100, 1)}
                dx, dy = tx - cur.x, ty - cur.y; n = math.hypot(dx, dy); dx /= n; dy /= n
                s = unreal.Vector(cur.x, cur.y, cur.z + 60); e = unreal.Vector(cur.x + dx * 45, cur.y + dy * 45, cur.z + 60)
                h = unreal.SystemLibrary.line_trace_single(w, s, e, unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, False, ign, unreal.DrawDebugTrace.NONE, True)
                if h and h.to_tuple()[0]:
                    return {"llego": False, "tope": [round(cur.x), round(cur.y), round(cur.z)], "por": "pared:" + (h.to_tuple()[9].get_actor_label() if h.to_tuple()[9] else "?"), "m": round(recorrido / 100, 1)}
                p = proj(cur.x + dx * 4, cur.y + dy * 4, cur.z, (40, 40, 300))
                if p is None:
                    return {"llego": False, "tope": [round(cur.x), round(cur.y), round(cur.z)], "por": "sin NavMesh", "m": round(recorrido / 100, 1)}
                av = math.hypot(p.x - cur.x, p.y - cur.y)
                quieto = quieto + 1 if av < 0.5 else 0
                recorrido += av; cur = p
        return {"llego": True, "fin": [round(cur.x), round(cur.y), round(cur.z)], "m": round(recorrido / 100, 1)}
    def huecos(a, b):
        L = math.hypot(b[0] - a[0], b[1] - a[1]); n = int(L // 25); out = []; inh = None
        for i in range(n + 1):
            x = a[0] + (b[0] - a[0]) * i / n; y = a[1] + (b[1] - a[1]) * i / n
            ok = proj(x, y, 50, (5, 5, 300)) is not None
            if not ok and inh is None: inh = (x, y)
            if ok and inh is not None:
                out.append([round(inh[0]), round(inh[1]), round(x), round(y), round(math.hypot(x - inh[0], y - inh[1]))]); inh = None
        return out
    res["tramos"]["plaza_a_barConv"] = caminar([(190, 209), (1216, 209), (1330, 342), (2063, 712), (2309, 916), (3325, 1311)])
    res["tramos"]["plaza_a_barHac"] = caminar([(383, -950), (-1490, -1000), (-1810, -1000), (-4940, 0)])
    res["huecos_1330_2063"] = huecos((1330, 342), (2063, 712))
    res["huecos_1311_-1490"] = huecos((1311, 456), (-1490, -1000))
    res["huecos_383_-1490"] = huecos((383, -950), (-1490, -1000))
except Exception:
    res["err"] = traceback.format_exc()[:1500]
open(OUT, "w").write(json.dumps(res))
