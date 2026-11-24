# 479_ue_rutas_horneadas_adela.py
# Proyecto: Jatun Wasi Nawpa Kay (tesis VR Quest 2)
# Fecha: 2026-11-24
# Proposito: el NavMesh esta CORTADO en BAR_Convento/BAR_Hacienda (NavMesh estatico) -> la busqueda de
#   caminos no cruza. Se HORNEAN las rutas de Adela (polilineas fijas) por tramos NavMesh y cruce recto de
#   cada barrera: Plaza->Templo, Templo->Convento, Convento->Hacienda. Valida cada sub-camino (que llegue
#   a menos de 60 cm de su destino) y propone estaciones (a un costado del final, mirando al que llega).
#   Escribe rutas_horneadas.json (lo usa 481 para configurar el componente).
import unreal, json, math, traceback
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/rutas_horneadas.json"
res = {"err": None, "barreras": {}, "rutas": {}, "estaciones": {}, "problemas": []}
try:
    w = unreal.EditorLevelLibrary.get_editor_world()
    def nav(x, y, z=100, e=(60, 60, 600)):
        r = unreal.NavigationSystemV1.project_point_to_navigation(w, unreal.Vector(x, y, z), None, None, unreal.Vector(*e))
        return r[0] if isinstance(r, tuple) else r
    def path(a, b, tag):
        p = unreal.NavigationSystemV1.find_path_to_location_synchronously(w, a, b)
        pts = [unreal.Vector(v.x, v.y, v.z) for v in p.get_editor_property("path_points")] if p else []
        if not pts or math.dist([pts[-1].x, pts[-1].y], [b.x, b.y]) > 60:
            res["problemas"].append("%s incompleto: termina %s" % (tag, [round(pts[-1].x), round(pts[-1].y)] if pts else None))
        return pts
    acts = {a.get_actor_label(): a for a in unreal.EditorLevelLibrary.get_all_level_actors()}
    cruces = {}
    for bn in ("BAR_Convento", "BAR_Hacienda"):
        b = acts[bn]; L = b.get_actor_location(); R = b.get_actor_rotation(); S = b.get_actor_scale3d()
        yaw = math.radians(R.yaw); fx, fy = math.cos(yaw), math.sin(yaw)   # eje X local = espesor
        A = nav(L.x - fx * 160, L.y - fy * 160, 100, (40, 40, 400)); B = nav(L.x + fx * 160, L.y + fy * 160, 100, (40, 40, 400))
        res["barreras"][bn] = {"loc": [round(L.x), round(L.y)], "yaw": round(R.yaw, 1), "escala": [round(S.x, 2), round(S.y, 2)],
                               "lado_menos": [round(A.x), round(A.y), round(A.z)] if A else None, "lado_mas": [round(B.x), round(B.y), round(B.z)] if B else None}
        cruces[bn] = (A, B)
    P = {"plaza": nav(383, -950), "templo": nav(50, 9550), "convento": nav(5950, 4250), "hacienda": nav(-7250, -820)}
    def cerca(v, c):  # devuelve el lado de la barrera mas cercano a v y el otro
        A, B = c
        return (A, B) if math.dist([v.x, v.y], [A.x, A.y]) < math.dist([v.x, v.y], [B.x, B.y]) else (B, A)
    def junta(*segs):
        out = []
        for s in segs:
            for v in s:
                if not out or math.dist([out[-1].x, out[-1].y, out[-1].z], [v.x, v.y, v.z]) > 5: out.append(v)
        return out
    r1 = path(P["plaza"], P["templo"], "plaza>templo")
    a1, b1 = cerca(P["templo"], cruces["BAR_Convento"])
    r2 = junta(path(P["templo"], a1, "templo>barConv"), path(b1, P["convento"], "barConv>convento"))
    c_conv_in, c_conv_out = cerca(P["convento"], cruces["BAR_Convento"])
    h_in, h_out = cerca(P["plaza"], cruces["BAR_Hacienda"])
    r3 = junta(path(P["convento"], c_conv_in, "convento>barConv"), path(c_conv_out, h_in, "barConv>barHac"), path(h_out, P["hacienda"], "barHac>hacienda"))
    for k, r in (("plaza_templo", r1), ("templo_convento", r2), ("convento_hacienda", r3)):
        Lm = sum(math.dist([r[i].x, r[i].y], [r[i + 1].x, r[i + 1].y]) for i in range(len(r) - 1))
        seg_max = max(math.dist([r[i].x, r[i].y], [r[i + 1].x, r[i + 1].y]) for i in range(len(r) - 1))
        res["rutas"][k] = {"largo_m": round(Lm / 100, 1), "seg_max_m": round(seg_max / 100, 1), "pts": [[round(v.x), round(v.y), round(v.z)] for v in r]}
        # estacion al final del tramo
        pp = r; end = pp[-1]; prev = pp[-2]
        dx, dy = end.x - prev.x, end.y - prev.y; n = math.hypot(dx, dy) or 1; dx /= n; dy /= n
        cands = []
        for side in (1, -1):
            for off in (220, 180, 260, 150):
                x = end.x + (-dy) * side * off; y = end.y + dx * side * off
                v = nav(x, y, end.z, (20, 20, 300))
                if not v or abs(v.z - end.z) > 60: continue
                ok = True
                for kk in range(8):
                    ang = kk * math.pi / 4
                    h = unreal.SystemLibrary.line_trace_single(w, unreal.Vector(v.x, v.y, v.z + 100), unreal.Vector(v.x + 50 * math.cos(ang), v.y + 50 * math.sin(ang), v.z + 100), unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, False, [], unreal.DrawDebugTrace.NONE, True)
                    if h and h.to_tuple()[0]: ok = False; break
                if ok: cands.append([round(v.x), round(v.y), round(v.z), side, off])
        res["estaciones"][k.split("_")[1]] = {"fin": [round(end.x), round(end.y), round(end.z)], "yaw_mirar_llegada": round(math.degrees(math.atan2(-dy, -dx)), 1), "cands": cands[:4]}
except Exception:
    res["err"] = traceback.format_exc()[:1500]
open(OUT, "w").write(json.dumps(res))
