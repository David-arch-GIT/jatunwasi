# 483_ue_ruta_convento_hacienda.py
# Proyecto: Jatun Wasi Nawpa Kay (tesis VR Quest 2)
# Fecha: 2026-11-24
# Proposito: (solo lectura) camino Convento->Hacienda desde FUERA de las puertas del convento (estacion de
#   Adela, 7 m antes de las puertas) y simulacion de la locomocion real del visitante por el (con guarda).
#   Agrega "convento_hacienda_ext" a rutas_finales.json.
import unreal, json, math, traceback
F = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/rutas_finales.json"
res = json.loads(open(F).read())
try:
    w = unreal.EditorLevelLibrary.get_editor_world()
    acts = {a.get_actor_label(): a for a in unreal.EditorLevelLibrary.get_all_level_actors()}
    ign = [acts["BAR_Convento"], acts["BAR_Hacienda"]]
    def proj(x, y, z=100, e=(60, 60, 600)):
        r = unreal.NavigationSystemV1.project_point_to_navigation(w, unreal.Vector(x, y, z), None, None, unreal.Vector(*e))
        return r[0] if isinstance(r, tuple) else r
    a = proj(*res["estaciones"]["convento"]["camino"][:2]); b = proj(-7250, -820)
    p = unreal.NavigationSystemV1.find_path_to_location_synchronously(w, a, b)
    pp = [unreal.Vector(v.x, v.y, v.z) for v in p.get_editor_property("path_points")] if p else []
    res["rutas"]["convento_hacienda_ext"] = [[round(v.x), round(v.y), round(v.z)] for v in pp]
    cur = pp[0]; rec = 0.0; out = {"llego": True}
    for tgt in pp[1:]:
        pasos = 0; maxp = int(math.hypot(tgt.x - cur.x, tgt.y - cur.y) / 4 * 2) + 60; quieto = 0
        while math.hypot(tgt.x - cur.x, tgt.y - cur.y) > 8 and out["llego"]:
            pasos += 1
            if pasos > maxp or quieto > 15: out = {"llego": False, "tope": [round(cur.x), round(cur.y)], "por": "no avanza"}; break
            dx, dy = tgt.x - cur.x, tgt.y - cur.y; n = math.hypot(dx, dy); dx /= n; dy /= n
            h = unreal.SystemLibrary.line_trace_single(w, unreal.Vector(cur.x, cur.y, cur.z + 60), unreal.Vector(cur.x + dx * 45, cur.y + dy * 45, cur.z + 60), unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, False, ign, unreal.DrawDebugTrace.NONE, True)
            if h and h.to_tuple()[0]:
                t = h.to_tuple(); out = {"llego": False, "tope": [round(cur.x), round(cur.y)], "por": "choca:" + (t[9].get_actor_label() if t[9] else "?")}; break
            q = proj(cur.x + dx * 4, cur.y + dy * 4, cur.z, (40, 40, 300))
            if q is None: out = {"llego": False, "tope": [round(cur.x), round(cur.y)], "por": "sin NavMesh"}; break
            av = math.hypot(q.x - cur.x, q.y - cur.y); quieto = quieto + 1 if av < 0.5 else 0; rec += av; cur = q
        if not out["llego"]: break
    out["m"] = round(rec / 100, 1)
    res["caminata"]["convento_hacienda_ext"] = out
except Exception:
    res["err483"] = traceback.format_exc()[:1200]
open(F, "w").write(json.dumps(res))
