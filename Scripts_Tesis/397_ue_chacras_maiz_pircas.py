# 397_ue_chacras_maiz_pircas.py
# Proyecto: Jatun Wasi Nawpa Kay (tesis VR Quest 2)
# Fecha: 2026-11-24
# Proposito: dar vida a campos vacios con elementos del valle cochabambino:
#   (v2: el maiz KitHacienda no tiene material -> se omite; corrales de pirca de 9x6 m)
#   - 3 chacras de maiz (8x5 m) cercadas con pirca de piedra (con entrada hacia el sendero)
#   - pasto seco de valle + rocas dispersas
#   Todo como HISM dentro del actor existente RELLENO_Campos (reversible borrando ese actor).
#   Respeta: >9 m del NavMesh, edificios (+8 m), leyendas (criatura 12 m + corredor 9 m),
#   y vegetacion alta existente.
# Uso: DRY = True (simula) / False (coloca) antes de exec().
import unreal, json, math, random, traceback

try:
    DRY
except NameError:
    DRY = True

OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/chacras.json"
world = unreal.EditorLevelLibrary.get_editor_world()
res = {"dry": DRY, "err": None, "parcels": [], "counts": {}}

CORN = "/Game/JWN/Props/Hacienda/KitHacienda_SM_HAC_Corn"
PIRCA = ["/Game/StylescapeHD/Misc/StoneFence/SM_Stone_Fence_01", "/Game/StylescapeHD/Misc/StoneFence/SM_Stone_Fence_02"]
GRASS = ["/Game/StylescapeHD/Foliage/Grassland/SM_Grass_04",
         "/Game/StylescapeHD/Foliage/Grassland/SM_Grass_05"]
ROCKS = ["/Game/StylescapeHD/Foliage/Grassland/SM_Rock_03", "/Game/StylescapeHD/Foliage/Grassland/SM_Rock_04"]
LEG = {"karisiri": ((3801, 3281), (4000, 1700)), "condenado": ((1031, 8380), (325, 7596)),
       "duende": ((-4135, 668), (-4310, -143))}

def seg_dist(px, py, ax, ay, bx, by):
    dx, dy = bx - ax, by - ay
    t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)))
    return math.hypot(px - (ax + t * dx), py - (ay + t * dy))

def legend_clear(x, y, rc=1200, rk=900):
    for (cx, cy), (nx, ny) in LEG.values():
        if math.hypot(x - cx, y - cy) < rc or seg_dist(x, y, nx, ny, cx, cy) < rk:
            return False
    return True

def nav_proj(x, y, ext):
    try:
        r = unreal.NavigationSystemV1.project_point_to_navigation(
            world, unreal.Vector(x, y, 100), None, None, unreal.Vector(ext, ext, 600))
        return r[0] if isinstance(r, tuple) else r
    except Exception:
        return None

def ground_z(x, y):
    try:
        r = unreal.SystemLibrary.line_trace_single(world, unreal.Vector(x, y, 3000), unreal.Vector(x, y, -3000),
            unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, False, [], unreal.DrawDebugTrace.NONE, True)
        hit = r if isinstance(r, unreal.HitResult) else next((e for e in (r if isinstance(r, tuple) else []) if isinstance(e, unreal.HitResult)), None)
        if hit is None:
            return None
        t = hit.to_tuple()
        return t[4].z if t[0] else None
    except Exception:
        return None

try:
    # material del maiz: si es emisivo/glow, NO usar (brillaria de noche)
    corn_sm = unreal.load_asset(CORN)
    corn_mats = [m.get_name() for m in corn_sm.get_editor_property("static_materials") and
                 [sm.get_editor_property("material_interface") for sm in corn_sm.get_editor_property("static_materials")] if m]
    res["corn_mats"] = corn_mats
    use_corn = not any(("glow" in m.lower() or "emis" in m.lower() or "worldgrid" in m.lower() or "default" in m.lower()) for m in corn_mats)
    res["use_corn"] = use_corn

    tall, big, trees_only = [], [], []
    for a in unreal.EditorLevelLibrary.get_all_level_actors():
        isms = a.get_components_by_class(unreal.InstancedStaticMeshComponent)
        for c in isms:
            sm = c.get_editor_property("static_mesh"); n = sm.get_name() if sm else ""
            if any(k in n for k in ("Tree", "Maple", "Oak", "Pine", "Bush", "Plant", "Cactus")):
                for i in range(c.get_instance_count()):
                    p = c.get_instance_transform(i, True).translation
                    tall.append((p.x, p.y))
                    if any(k in n for k in ("Tree", "Maple", "Oak", "Pine")):
                        trees_only.append((p.x, p.y))
        if not isms and a.get_components_by_class(unreal.StaticMeshComponent):
            o, e = a.get_actor_bounds(False)
            if (e.x > 250 or e.y > 250) and e.x < 8000 and e.y < 8000 and e.z > 60:
                big.append((o.x - e.x, o.x + e.x, o.y - e.y, o.y + e.y))
    hashT = {}
    for (x, y) in tall:
        hashT.setdefault((int(x // 400), int(y // 400)), []).append((x, y))

    def tall_near(x, y, r):
        kx, ky = int(x // 400), int(y // 400)
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                for (px, py) in hashT.get((kx + dx, ky + dy), []):
                    if (px - x) ** 2 + (py - y) ** 2 < r * r:
                        return True
        return False

    def in_big(x, y, pad):
        return any(b[0] - pad < x < b[1] + pad and b[2] - pad < y < b[3] + pad for b in big)

    def point_ok(x, y):
        loc = nav_proj(x, y, 900)
        if loc is not None and math.hypot(loc.x - x, loc.y - y) < 900:
            return False
        return legend_clear(x, y) and not in_big(x, y, 800) and not any((px - x) ** 2 + (py - y) ** 2 < 40000 for (px, py) in trees_only)

    # --- candidatas a chacra
    random.seed(397)
    cands = []
    for gx in range(-16000, 16001, 600):
        for gy in range(-13000, 20001, 600):
            loc = nav_proj(gx, gy, 3500)
            if loc is None:
                continue
            d = math.hypot(loc.x - gx, loc.y - gy)
            if 1200 < d < 3000:
                cands.append((d, gx, gy, loc.x, loc.y))
    cands.sort()
    parcels = []
    for (d, cx, cy, nx, ny) in cands:
        if len(parcels) >= 4:
            break
        if any(math.hypot(cx - p[0], cy - p[1]) < 3500 for p in parcels):
            continue
        yaw = math.atan2(ny - cy, nx - cx)        # eje local X apunta al sendero
        ux, uy = math.cos(yaw), math.sin(yaw); vx, vy = -uy, ux
        perim = [(a, b) for a in range(-450, 451, 150) for b in (-300, 300)] + [(a, b) for a in (-450, 450) for b in range(-300, 301, 150)]
        ok = all(point_ok(cx + ux * a + vx * b, cy + uy * a + vy * b) for (a, b) in perim)
        if ok:
            parcels.append((cx, cy, yaw, round(d)))
    res["parcels"] = [[round(p[0]), round(p[1]), round(math.degrees(p[2])), p[3]] for p in parcels]

    corn, pirca, grass, rocks = [], [], [], []
    for (cx, cy, yaw, d) in parcels:
        ux, uy = math.cos(yaw), math.sin(yaw); vx, vy = -uy, ux
        z0 = ground_z(cx, cy) or 0.0
        if use_corn:
            for a in range(-360, 361, 75):          # surcos (filas) perpendiculares al sendero
                for b in range(-220, 221, 45):
                    px = cx + ux * a + vx * (b + random.uniform(-8, 8))
                    py = cy + uy * a + vy * (b + random.uniform(-8, 8))
                    corn.append((px, py, z0, random.uniform(0, 360), random.uniform(0.85, 1.15)))
        # pirca perimetral 9x6 m, con entrada de 2 m en el lado que mira al sendero
        hw, hh = 450, 300
        sides = [((-hw, -hh), (hw, -hh)), ((hw, -hh), (hw, hh)), ((hw, hh), (-hw, hh)), ((-hw, hh), (-hw, -hh))]
        for si, ((a0, b0), (a1, b1)) in enumerate(sides):
            L = math.hypot(a1 - a0, b1 - b0); n = int(L // 190)
            for k in range(n):
                t = (k + 0.5) / n
                a = a0 + (a1 - a0) * t; b = b0 + (b1 - b0) * t
                if si == 1 and abs(b) < 110:      # entrada hacia el sendero (lado +X local)
                    continue
                px = cx + ux * a + vx * b; py = cy + uy * a + vy * b
                seg_yaw = math.degrees(math.atan2((b1 - b0) * vy + (a1 - a0) * uy, (b1 - b0) * vx + (a1 - a0) * ux))
                pirca.append((px, py, z0, seg_yaw + random.uniform(-3, 3), 1.0, k % 2))

    # pasto seco + rocas dispersas (fuera de chacras)
    for gx in range(-16000, 16001, 450):
        for gy in range(-13000, 20001, 450):
            if len(grass) >= 160 and len(rocks) >= 40:
                break
            x = gx + random.uniform(-180, 180); y = gy + random.uniform(-180, 180)
            loc = nav_proj(x, y, 3500)
            if loc is None:
                continue
            d = math.hypot(loc.x - x, loc.y - y)
            if d < 800 or d > 3500 or not legend_clear(x, y, 900, 600) or in_big(x, y, 300):
                continue
            if any(abs((x - p[0]) * math.cos(p[2]) + (y - p[1]) * math.sin(p[2])) < 600 and
                   abs(-(x - p[0]) * math.sin(p[2]) + (y - p[1]) * math.cos(p[2])) < 450 for p in parcels):
                continue
            r = random.random()
            if r < 0.30 and len(grass) < 160:
                z = ground_z(x, y)
                if z is not None:
                    grass.append((x, y, z, random.uniform(0, 360), random.uniform(0.8, 1.3), random.randrange(len(GRASS))))
            elif r > 0.965 and len(rocks) < 40:
                z = ground_z(x, y)
                if z is not None:
                    rocks.append((x, y, z - 10, random.uniform(0, 360), random.uniform(0.7, 1.2), random.randrange(len(ROCKS))))

    res["counts"] = {"corn": len(corn), "pirca": len(pirca), "grass": len(grass), "rocks": len(rocks)}

    if not DRY:
        actor = next(a for a in unreal.EditorLevelLibrary.get_all_level_actors() if a.get_actor_label() == "RELLENO_Campos")
        sds = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
        root = sds.k2_gather_subobject_data_for_instance(actor)[0]
        made = []
        def add_group(mpath, items, cull, minlod):
            if not items:
                return
            h, fail = sds.add_new_subobject(unreal.AddNewSubobjectParams(parent_handle=root,
                new_class=unreal.HierarchicalInstancedStaticMeshComponent, blueprint_context=None))
            comp = unreal.SubobjectDataBlueprintFunctionLibrary.get_object(unreal.SubobjectDataBlueprintFunctionLibrary.get_data(h))
            comp.set_static_mesh(unreal.load_asset(mpath))
            comp.set_mobility(unreal.ComponentMobility.STATIC)
            comp.set_editor_property("cast_shadow", False)
            comp.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
            comp.set_editor_property("can_ever_affect_navigation", False)
            comp.set_editor_property("instance_start_cull_distance", int(cull * 0.8))
            comp.set_editor_property("instance_end_cull_distance", int(cull))
            comp.set_editor_property("override_min_lod", True)
            comp.set_editor_property("min_lod", minlod)
            comp.add_instances([unreal.Transform(unreal.Vector(it[0], it[1], it[2]), unreal.Rotator(0, 0, it[3]),
                                unreal.Vector(it[4], it[4], it[4])) for it in items], False, True)
            made.append([mpath.split("/")[-1], comp.get_instance_count(), cull, minlod])
        add_group(CORN, corn, 4500, 1)
        for i, p in enumerate(PIRCA):
            add_group(p, [it for it in pirca if it[5] == i], 5000, 1)
        for i, p in enumerate(GRASS):
            add_group(p, [it for it in grass if it[5] == i], 3500, 1)
        for i, p in enumerate(ROCKS):
            add_group(p, [it for it in rocks if it[5] == i], 4000, 0)
        res["made"] = made
        unreal.EditorLevelLibrary.save_current_level()
except Exception:
    res["err"] = traceback.format_exc()[:900]
open(OUT, "w").write(json.dumps(res, indent=1))


