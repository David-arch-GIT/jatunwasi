# 478_ue_rutas_estaciones_adela.py
# Proyecto: Jatun Wasi Nawpa Kay (tesis VR Quest 2)
# Fecha: 2026-11-24
# Proposito: (solo lectura) caminos NavMesh de cada tramo del recorrido guiado y propuesta de ESTACION de
#   Adela en cada lugar: punto del camino mas cercano al RELATO_<zona>, desplazado ~2.2 m a un costado
#   (sobre NavMesh, con espacio libre) y mirando hacia atras por el camino (hacia el visitante que llega).
import unreal, json, math, traceback
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/rutas_adela.json"
res = {"err": None, "tramos": {}, "estaciones": {}}
try:
    w = unreal.EditorLevelLibrary.get_editor_world()
    def nav(x, y, z=100, e=(60, 60, 600)):
        r = unreal.NavigationSystemV1.project_point_to_navigation(w, unreal.Vector(x, y, z), None, None, unreal.Vector(*e))
        return r[0] if isinstance(r, tuple) else r
    def path(a, b):
        p = unreal.NavigationSystemV1.find_path_to_location_synchronously(w, a, b)
        return [unreal.Vector(v.x, v.y, v.z) for v in p.get_editor_property("path_points")] if p else []
    def libre(x, y, z):
        for k in range(8):
            ang = k * math.pi / 4
            h = unreal.SystemLibrary.line_trace_single(w, unreal.Vector(x, y, z + 100), unreal.Vector(x + 60 * math.cos(ang), y + 60 * math.sin(ang), z + 100), unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, False, [], unreal.DrawDebugTrace.NONE, True)
            if h and h.to_tuple()[0]: return False
        return True
    pts = {"plaza": (383, -950), "templo": (50, 9550), "convento": (5950, 4250), "hacienda": (-7250, -820)}
    P = {k: nav(*v) for k, v in pts.items()}
    res["proy"] = {k: [round(v.x), round(v.y), round(v.z)] if v else None for k, v in P.items()}
    legs = [("plaza", "templo"), ("templo", "convento"), ("convento", "hacienda")]
    for a, b in legs:
        pp = path(P[a], P[b])
        L = sum(math.dist([pp[i].x, pp[i].y], [pp[i + 1].x, pp[i + 1].y]) for i in range(len(pp) - 1)) if len(pp) > 1 else 0
        res["tramos"][a + "_" + b] = {"n": len(pp), "largo_m": round(L / 100, 1), "pts": [[round(v.x), round(v.y), round(v.z)] for v in pp]}
        # estacion en b: ultimo segmento que llega al relato -> direccion de llegada
        if len(pp) >= 2:
            # punto del camino 3 m antes del final
            acc = 0; q = pp[-1]; prev = pp[-2]
            for i in range(len(pp) - 1, 0, -1):
                s = math.dist([pp[i].x, pp[i].y], [pp[i - 1].x, pp[i - 1].y])
                if acc + s >= 300:
                    t = (300 - acc) / s
                    q = unreal.Vector(pp[i].x + (pp[i - 1].x - pp[i].x) * t, pp[i].y + (pp[i - 1].y - pp[i].y) * t, pp[i].z)
                    prev = pp[i - 1]; break
                acc += s
            dx, dy = pp[-1].x - prev.x, pp[-1].y - prev.y; n = math.hypot(dx, dy) or 1; dx /= n; dy /= n
            cands = []
            for side in (1, -1):
                for off in (220, 180, 260, 140):
                    x = pp[-1].x + (-dy) * side * off; y = pp[-1].y + dx * side * off
                    v = nav(x, y, pp[-1].z, (20, 20, 300))
                    if v and abs(v.z - pp[-1].z) < 60 and libre(v.x, v.y, v.z):
                        cands.append([round(v.x), round(v.y), round(v.z), side, off])
            yaw = math.degrees(math.atan2(-dy, -dx))
            res["estaciones"][b] = {"fin_camino": [round(pp[-1].x), round(pp[-1].y), round(pp[-1].z)], "llegada_dir": [round(dx, 2), round(dy, 2)], "yaw_mirar_visitante": round(yaw, 1), "cands": cands[:4]}
except Exception:
    res["err"] = traceback.format_exc()[:1500]
open(OUT, "w").write(json.dumps(res))
