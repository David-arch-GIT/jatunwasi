# 424_ue_medir_vanos.py
# Proyecto: Jatun Wasi Nawpa Kay (tesis VR Quest 2)
# Fecha: 2026-11-24
# Proposito: (solo lectura) medir con precision los 3 vanos donde van las puertas Tripo.
#   Para cada entrada (centro aproximado + rango de angulos de paso): elige el angulo cuyo corte
#   lateral es mas simetrico/estrecho, recorre el eje de paso (+-5 m cada 10 cm) midiendo ancho libre
#   a 1.5 m y altura libre; el PLANO de la puerta = posicion de menor ancho con dintel. Ahi mide el
#   PERFIL del vano (ancho libre cada 10 cm de altura -> detecta arco) y el centro exacto.
import unreal, json, math, traceback
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/vanos_medidos.json"
VEG = ("JW_ENV_", "PCG_", "HORIZ_", "HACFOR_", "RELLENO_", "NOCHE_", "ENV_", "StarDome", "RLV_", "Ground_", "BAR_", "Trig", "TRG_", "COL_Templo_Umbral", "GUIA_", "Narr_", "RELATO_", "RelatoCartela")
ENT = {"templo": (50, 10300, range(80, 101, 2)), "convento": (6300, 3450, range(60, 121, 2)), "hacienda": (-6996, -2500, range(70, 131, 2))}
res = {"err": None}
try:
    world = unreal.EditorLevelLibrary.get_editor_world()
    ign = [a for a in unreal.EditorLevelLibrary.get_all_level_actors() if a.get_actor_label().startswith(VEG) or isinstance(a, (unreal.TriggerBase, unreal.Volume))]
    def tr(a, b):
        h = unreal.SystemLibrary.line_trace_single(world, a, b, unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, False, ign, unreal.DrawDebugTrace.NONE, True)
        if h is None: return None
        t = h.to_tuple()
        return (t[4], t[10].get_owner().get_actor_label() if t[10] else None) if t[0] else None
    def floor_z(x, y):   # v2: suelo = NavMesh (los techos de porches/zaguanes engañaban a la traza vertical)
        p = unreal.NavigationSystemV1.project_point_to_navigation(world, unreal.Vector(x, y, 60), None, None, unreal.Vector(60, 60, 250))
        p = p[0] if isinstance(p, tuple) else p
        return p.z if p is not None else None
    def lateral(x, y, z, ang, reach=450):
        a = math.radians(ang); lx, ly = -math.sin(a), math.cos(a)
        L = tr(unreal.Vector(x, y, z), unreal.Vector(x + lx * reach, y + ly * reach, z))
        R = tr(unreal.Vector(x, y, z), unreal.Vector(x - lx * reach, y - ly * reach, z))
        return L, R
    for name, (cx, cy, angs) in ENT.items():
        best = None
        for ang in angs:
            a = math.radians(ang); dx, dy = math.cos(a), math.sin(a)
            for k in range(-50, 51):
                x = cx + dx * k * 10; y = cy + dy * k * 10
                z = floor_z(x, y)
                if z is None: continue
                L, R = lateral(x, y, z + 150, ang)
                if not (L and R): continue
                w = math.hypot(L[0].x - R[0].x, L[0].y - R[0].y)
                up = tr(unreal.Vector(x, y, z + 150), unreal.Vector(x, y, z + 900))
                if not up or w < 100: continue
                score = w
                if best is None or score < best["w"] - 0.5:
                    mx = (L[0].x + R[0].x) / 2; my = (L[0].y + R[0].y) / 2
                    best = {"ang": ang, "k": k, "w": round(w, 1), "cx": round(mx, 1), "cy": round(my, 1), "floor": round(z, 1),
                            "h": round(up[0].z - z, 1), "walls": [L[1], R[1]], "lintel": up[1]}
        if best:
            prof = []
            for zz in range(10, 800, 10):
                L, R = lateral(best["cx"], best["cy"], best["floor"] + zz, best["ang"])
                if L and R:
                    a = math.radians(best["ang"]); lx, ly = -math.sin(a), math.cos(a)
                    dl = (L[0].x - best["cx"]) * lx + (L[0].y - best["cy"]) * ly
                    dr = (R[0].x - best["cx"]) * lx + (R[0].y - best["cy"]) * ly
                    prof.append([zz, round(dl, 1), round(dr, 1)])
                else:
                    prof.append([zz, None, None])
            best["profile"] = prof
            # profundidad del muro: recorrer el eje hasta salir de los muros laterales
            a = math.radians(best["ang"]); dx, dy = math.cos(a), math.sin(a)
            depth = []
            for k in range(-60, 61):
                x = best["cx"] + dx * k * 5; y = best["cy"] + dy * k * 5
                L, R = lateral(x, y, best["floor"] + 150, best["ang"], reach=best["w"] / 2 + 15)
                depth.append(1 if (L and R) else 0)
            ins = [i for i, v in enumerate(depth) if v]
            best["wall_depth_cm"] = (ins[-1] - ins[0]) * 5 if ins else None
            best["wall_from_to"] = [(ins[0] - 60) * 5, (ins[-1] - 60) * 5] if ins else None
        res[name] = best
except Exception:
    res["err"] = traceback.format_exc()[:1200]
open(OUT, "w").write(json.dumps(res))
