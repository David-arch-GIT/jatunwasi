# 394_ue_relleno_campos_analisis.py
# Proyecto: Jatun Wasi Nawpa Kay (tesis VR Quest 2)
# Fecha: 2026-11-24
# Proposito: SOLO ANALISIS (no modifica el nivel). Encuentra zonas vacias visibles
#   desde los senderos para rellenarlas con vegetacion instanciada barata.
#   Reglas: >7 m del NavMesh (camino), <45 m del NavMesh (visible), sin vegetacion
#   existente a <5 m, fuera de edificios, y libre alrededor de las 3 leyendas
#   (criatura r=7 m + corredor de vision desde su punto de narracion, ancho 5 m).
# Salida: Saved/ClaudeBackups/relleno_candidatos.json
import unreal, json, math, random

OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/relleno_candidatos.json"
world = unreal.EditorLevelLibrary.get_editor_world()
res = {"cells": [], "stats": {}, "err": None}

LEG = {  # criatura, punto de narracion
    "karisiri": ((3801, 3281), (4000, 1700)),
    "condenado": ((1031, 8380), (325, 7596)),
    "duende": ((-4135, 668), (-4310, -143)),
}

def seg_dist(px, py, ax, ay, bx, by):
    dx, dy = bx - ax, by - ay
    t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)))
    return math.hypot(px - (ax + t * dx), py - (ay + t * dy))

try:
    # 1) vegetacion existente -> hash 500 uu
    veg = {}
    nveg = 0
    big = []  # AABB de actores grandes (edificios, muros)
    for a in unreal.EditorLevelLibrary.get_all_level_actors():
        isms = a.get_components_by_class(unreal.InstancedStaticMeshComponent)
        for c in isms:
            smn = c.get_editor_property("static_mesh")
            smn = smn.get_name() if smn else ""
            # solo vegetacion ALTA cuenta como ocupado (el pasto/helecho de noche no se ve)
            if not any(k in smn for k in ("Tree", "Maple", "Oak", "Bush", "Plant", "Pine", "Birch")):
                continue
            for i in range(c.get_instance_count()):
                t = c.get_instance_transform(i, True)
                k = (int(t.translation.x // 500), int(t.translation.y // 500))
                veg.setdefault(k, []).append((t.translation.x, t.translation.y, t.translation.z))
                nveg += 1
        if not isms and a.get_components_by_class(unreal.StaticMeshComponent):
            o, e = a.get_actor_bounds(False)
            if (e.x > 250 or e.y > 250) and e.x < 8000 and e.y < 8000 and e.z > 60:
                big.append((o.x - e.x - 300, o.x + e.x + 300, o.y - e.y - 300, o.y + e.y + 300))
    res["stats"]["veg_instances"] = nveg
    res["stats"]["big_actors"] = len(big)

    def veg_near(x, y, r):
        kx, ky = int(x // 500), int(y // 500)
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                for (vx, vy, vz) in veg.get((kx + dx, ky + dy), []):
                    if math.hypot(vx - x, vy - y) < r:
                        return True
        return False

    def nav_dist(x, y, ext):
        try:
            r = unreal.NavigationSystemV1.project_point_to_navigation(
                world, unreal.Vector(x, y, 100), None, None, unreal.Vector(ext, ext, 600))
            loc = r[0] if isinstance(r, tuple) else r
            if loc is None:
                return None
            return math.hypot(loc.x - x, loc.y - y)
        except Exception:
            return None

    # 2) grilla 500 uu (5 m) con jitter
    random.seed(394)
    n_tested = 0
    excl = {"nav_close": 0, "not_visible": 0, "veg": 0, "building": 0, "legend": 0}
    for gx in range(-16000, 16001, 500):
        for gy in range(-13000, 20001, 500):
            x = gx + random.uniform(-200, 200)
            y = gy + random.uniform(-200, 200)
            n_tested += 1
            d_far = nav_dist(x, y, 4500)
            if d_far is None:
                excl["not_visible"] += 1
                continue
            if d_far < 700:
                excl["nav_close"] += 1
                continue
            if any(b[0] < x < b[1] and b[2] < y < b[3] for b in big):
                excl["building"] += 1
                continue
            leg_hit = False
            for nm, ((cx, cy), (nx, ny)) in LEG.items():
                if math.hypot(x - cx, y - cy) < 700 or seg_dist(x, y, nx, ny, cx, cy) < 500:
                    leg_hit = True
                    break
            if leg_hit:
                excl["legend"] += 1
                continue
            if veg_near(x, y, 500):
                excl["veg"] += 1
                continue
            res["cells"].append([round(x), round(y), round(d_far)])
    res["stats"]["tested"] = n_tested
    res["stats"]["excluded"] = excl
    res["stats"]["candidates"] = len(res["cells"])
except Exception as e:
    import traceback
    res["err"] = str(e) + " | " + traceback.format_exc()[:600]

open(OUT, "w").write(json.dumps(res))
