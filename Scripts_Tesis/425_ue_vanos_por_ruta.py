# 425_ue_vanos_por_ruta.py
# Proyecto: Jatun Wasi Nawpa Kay (tesis VR Quest 2)
# Fecha: 2026-11-24
# Proposito: (solo lectura) hallar la PRIMERA puerta que cruza el visitante al entrar a cada
#   edificio, siguiendo la ruta real del NavMesh desde la plaza (find_path_to_location_synchronously).
#   Se muestrea la ruta cada 10 cm; un punto es "vano" si a 1.5 m hay muro a ambos lados
#   (perpendicular a la ruta, < 3 m) y dintel encima (< 6 m). Para cada vano: centro, angulo de paso,
#   ancho, alto, profundidad del muro y PERFIL de ancho por altura (arco o rectangular).
import unreal, json, math, traceback
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/vanos_ruta.json"
VEG = ("JW_ENV_", "PCG_", "HORIZ_", "HACFOR_", "RELLENO_", "NOCHE_", "ENV_", "StarDome", "RLV_", "Ground_", "BAR_", "Trig", "TRG_", "COL_Templo_Umbral", "GUIA_", "Narr_", "RELATO_", "RelatoCartela", "Adela", "Guia_", "App")
GOALS = {"templo": (0, 11200), "convento": (6290, 5000), "hacienda": (-7050, -2300)}
START = (600, -950)
res = {"err": None}
try:
    world = unreal.EditorLevelLibrary.get_editor_world()
    ign = [a for a in unreal.EditorLevelLibrary.get_all_level_actors() if a.get_actor_label().startswith(VEG) or isinstance(a, (unreal.TriggerBase, unreal.Volume, unreal.Pawn))]
    def tr(a, b):
        h = unreal.SystemLibrary.line_trace_single(world, a, b, unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, False, ign, unreal.DrawDebugTrace.NONE, True)
        if h is None: return None
        t = h.to_tuple()
        return (t[4], t[10].get_owner().get_actor_label() if t[10] else None) if t[0] else None
    for name, (gx, gy) in GOALS.items():
        path = unreal.NavigationSystemV1.find_path_to_location_synchronously(world, unreal.Vector(START[0], START[1], 20), unreal.Vector(gx, gy, 20))
        pts = list(path.get_editor_property("path_points")) if path else []
        r = {"n_pts": len(pts), "pts": [[round(p.x), round(p.y), round(p.z)] for p in pts]}
        doors = []; inside = False
        for a, b in zip(pts[:-1], pts[1:]):
            seg = math.hypot(b.x - a.x, b.y - a.y)
            if seg < 1: continue
            dx, dy = (b.x - a.x) / seg, (b.y - a.y) / seg; lx, ly = -dy, dx
            n = int(seg // 10)
            for k in range(n + 1):
                x = a.x + dx * k * 10; y = a.y + dy * k * 10; z = a.z + (b.z - a.z) * k / max(1, n)
                c = unreal.Vector(x, y, z + 150)
                L = tr(c, unreal.Vector(x + lx * 300, y + ly * 300, z + 150))
                R = tr(c, unreal.Vector(x - lx * 300, y - ly * 300, z + 150)) if L else None
                U = tr(c, unreal.Vector(x, y, z + 600)) if (L and R) else None
                hit = bool(L and R and U)
                if hit and not inside:
                    w = math.hypot(L[0].x - R[0].x, L[0].y - R[0].y)
                    mx = (L[0].x + R[0].x) / 2; my = (L[0].y + R[0].y) / 2
                    prof = []
                    for zz in range(10, 700, 10):
                        PL = tr(unreal.Vector(mx, my, z + zz), unreal.Vector(mx + lx * 400, my + ly * 400, z + zz))
                        PR = tr(unreal.Vector(mx, my, z + zz), unreal.Vector(mx - lx * 400, my - ly * 400, z + zz))
                        prof.append([zz, round(math.hypot(PL[0].x - mx, PL[0].y - my)) if PL else None, round(math.hypot(PR[0].x - mx, PR[0].y - my)) if PR else None])
                    depth = 0
                    for kk in range(1, 200):
                        xx = mx + dx * kk * 5; yy = my + dy * kk * 5
                        if tr(unreal.Vector(xx, yy, z + 150), unreal.Vector(xx + lx * (w / 2 + 20), yy + ly * (w / 2 + 20), z + 150)):
                            depth = kk * 5
                        else:
                            break
                    doors.append({"cx": round(mx, 1), "cy": round(my, 1), "floor": round(z, 1), "ang": round(math.degrees(math.atan2(dy, dx)), 1),
                                  "w": round(w), "h": round(U[0].z - z), "walls": [L[1], R[1]], "lintel": U[1], "depth": depth, "profile": prof})
                inside = hit
        r["doors"] = doors
        res[name] = r
except Exception:
    res["err"] = traceback.format_exc()[:1200]
open(OUT, "w").write(json.dumps(res))
