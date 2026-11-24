# 423_ue_buscar_vanos_puerta.py
# Proyecto: Jatun Wasi Nawpa Kay (tesis VR Quest 2)
# Fecha: 2026-11-24
# Proposito: (solo lectura) encontrar los VANOS de puerta reales del Templo, Convento y Hacienda.
#   Recorre puntos del NavMesh (grilla 50 cm) cerca de cada edificio; un punto es "vano" si a 1.5 m
#   de altura hay muro a ambos lados (izq/der) a < 2.6 m, el frente y fondo estan libres, y hay
#   dintel/arco encima (< 7 m). Luego mide el vano en el mejor punto: ancho exacto (trazas cada 2 cm),
#   altura en el centro y perfil de altura a lo ancho (detecta arco). Salida: vanos.json
import unreal, json, math, traceback
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/vanos.json"
VEG = ("JW_ENV_", "PCG_", "HORIZ_", "HACFOR_", "RELLENO_", "NOCHE_", "ENV_", "StarDome", "RLV_", "Ground_", "BAR_", "Trig", "COL_Templo_Umbral")
ZONES = {"templo": (50, 10300, 1200), "convento": (5200, 4300, 2600), "hacienda": (-6300, -2200, 2000)}
res = {"err": None}
try:
    world = unreal.EditorLevelLibrary.get_editor_world()
    ign = [a for a in unreal.EditorLevelLibrary.get_all_level_actors() if a.get_actor_label().startswith(VEG) or isinstance(a, (unreal.TriggerBase, unreal.Volume))]
    def tr(a, b):
        h = unreal.SystemLibrary.line_trace_single(world, a, b, unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, False, ign, unreal.DrawDebugTrace.NONE, True)
        if h is None:
            return None
        t = h.to_tuple()
        return (t[4], t[10].get_owner().get_actor_label() if t[10] else None) if t[0] else None
    def onnav(x, y):
        p = unreal.NavigationSystemV1.project_point_to_navigation(world, unreal.Vector(x, y, 50), None, None, unreal.Vector(10, 10, 200))
        p = p[0] if isinstance(p, tuple) else p
        return p
    for zn, (cx, cy, R) in ZONES.items():
        cands = []
        for ix in range(int(-R / 50), int(R / 50) + 1):
            for iy in range(int(-R / 50), int(R / 50) + 1):
                x = cx + ix * 50; y = cy + iy * 50
                p = onnav(x, y)
                if p is None:
                    continue
                z = p.z + 150
                for ang in (0, 15, 30, 45, 60, 75, 90, 105, 120, 135, 150, 165):
                    a = math.radians(ang); dx, dy = math.cos(a), math.sin(a)   # direccion de paso
                    lx, ly = -dy, dx                                            # lateral
                    L1 = tr(unreal.Vector(x, y, z), unreal.Vector(x + lx * 260, y + ly * 260, z))
                    if not L1: continue
                    L2 = tr(unreal.Vector(x, y, z), unreal.Vector(x - lx * 260, y - ly * 260, z))
                    if not L2: continue
                    F1 = tr(unreal.Vector(x, y, z), unreal.Vector(x + dx * 300, y + dy * 300, z))
                    F2 = tr(unreal.Vector(x, y, z), unreal.Vector(x - dx * 300, y - dy * 300, z))
                    if F1 or F2: continue
                    up = tr(unreal.Vector(x, y, z), unreal.Vector(x, y, z + 700))
                    if not up: continue
                    w = math.hypot(L1[0].x - L2[0].x, L1[0].y - L2[0].y)
                    cands.append([x, y, round(p.z), ang, round(w), round(up[0].z - p.z), L1[1], L2[1], up[1]])
        # agrupar: centro del vano = punto medio entre muros; quedarse con anchos > 120
        res[zn] = sorted(cands, key=lambda c: (c[4]))[:400]
except Exception:
    res["err"] = traceback.format_exc()[:1200]
open(OUT, "w").write(json.dumps(res))
