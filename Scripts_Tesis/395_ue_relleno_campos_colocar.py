# 395_ue_relleno_campos_colocar.py
# Proyecto: Jatun Wasi Nawpa Kay (tesis VR Quest 2)
# Fecha: 2026-11-24
# Proposito: rellenar campos vacios visibles desde los senderos con vegetacion
#   INSTANCIADA barata (HISM, sin sombras, sin colision, MinLOD, culling).
#   Todo va en UN actor "RELLENO_Campos" (tag RELLENO) -> reversible borrando ese actor.
#   Respeta: >7 m del NavMesh, edificios (+15 m para arboles), y las 3 leyendas
#   (criatura + corredor de vision desde su punto de narracion quedan libres).
# Uso: definir DRY = True (solo cuenta) o False (coloca) antes de exec().
import unreal, json, math, random, traceback

try:
    DRY
except NameError:
    DRY = True

OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/relleno_colocar.json"
world = unreal.EditorLevelLibrary.get_editor_world()
res = {"dry": DRY, "counts": {}, "err": None, "trace_ok": 0, "trace_fail": 0}

TREES = ["/Game/StylescapeHD/Foliage/Grassland/SM_Oak_02",
         "/Game/StylescapeHD/Foliage/Grassland/SM_Oak_01",
         "/Game/StylescapeHD/Foliage/Forest/SM_Maple_02",
         "/Game/StylescapeHD/Foliage/Grassland/SM_Oak_03"]
TREE_W = [0.40, 0.25, 0.20, 0.15]
BUSHES = ["/Game/StylescapeHD/Foliage/Grassland/SM_Bush_01",
          "/Game/StylescapeHD/Foliage/Grassland/SM_Bush_02",
          "/Game/StylescapeHD/Foliage/Grassland/SM_Bush_03",
          "/Game/StylescapeHD/Foliage/Grassland/SM_Bush_04"]
CACTUS = ["/Game/StylescapeHD/Foliage/Desert/SM_Cactus_01",
          "/Game/StylescapeHD/Foliage/Desert/SM_Cactus_02"]
MAX_TREES, MAX_BUSH, MAX_CACT = 140, 320, 24

LEG = {"karisiri": ((3801, 3281), (4000, 1700)),
       "condenado": ((1031, 8380), (325, 7596)),
       "duende": ((-4135, 668), (-4310, -143))}

def seg_dist(px, py, ax, ay, bx, by):
    dx, dy = bx - ax, by - ay
    t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)))
    return math.hypot(px - (ax + t * dx), py - (ay + t * dy))

def legend_clear(x, y, r_creature, r_corr):
    for (cx, cy), (nx, ny) in LEG.values():
        if math.hypot(x - cx, y - cy) < r_creature or seg_dist(x, y, nx, ny, cx, cy) < r_corr:
            return False
    return True

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

def ground_z(x, y):
    try:
        r = unreal.SystemLibrary.line_trace_single(
            world, unreal.Vector(x, y, 3000), unreal.Vector(x, y, -3000),
            unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, False, [], unreal.DrawDebugTrace.NONE, True)
        hit = None
        if isinstance(r, unreal.HitResult):
            hit = r
        elif isinstance(r, tuple):
            for e in r:
                if isinstance(e, unreal.HitResult):
                    hit = e
        if hit is None:
            res["trace_fail"] += 1
            return None
        t = hit.to_tuple()
        if not t[0]:  # blocking_hit
            res["trace_fail"] += 1
            return None
        res["trace_ok"] += 1
        return t[4].z  # location
    except Exception as e:
        res["trace_fail"] += 1
        res["trace_err"] = str(e)[:200]
        return None

try:
    # --- datos del nivel: arboles existentes, arbustos existentes, edificios
    trees_ex, bush_ex, big = [], [], []
    for a in unreal.EditorLevelLibrary.get_all_level_actors():
        isms = a.get_components_by_class(unreal.InstancedStaticMeshComponent)
        for c in isms:
            sm = c.get_editor_property("static_mesh"); n = sm.get_name() if sm else ""
            kind = "t" if any(k in n for k in ("Tree", "Maple", "Oak", "Pine")) else (
                   "b" if any(k in n for k in ("Bush", "Plant")) else None)
            if not kind:
                continue
            for i in range(c.get_instance_count()):
                p = c.get_instance_transform(i, True).translation
                (trees_ex if kind == "t" else bush_ex).append((p.x, p.y))
        if not isms and a.get_components_by_class(unreal.StaticMeshComponent):
            o, e = a.get_actor_bounds(False)
            if (e.x > 250 or e.y > 250) and e.x < 8000 and e.y < 8000 and e.z > 60:
                big.append((o.x - e.x, o.x + e.x, o.y - e.y, o.y + e.y))

    def near(lst, x, y, r):
        r2 = r * r
        for (px, py) in lst:
            if (px - x) ** 2 + (py - y) ** 2 < r2:
                return True
        return False

    def in_big(x, y, pad):
        return any(b[0] - pad < x < b[1] + pad and b[2] - pad < y < b[3] + pad for b in big)

    random.seed(395)
    new_t, new_b, new_c = [], [], []   # (x, y, z, yaw, scale, meshidx)
    for gx in range(-16000, 16001, 500):
        for gy in range(-13000, 20001, 500):
            x = gx + random.uniform(-220, 220); y = gy + random.uniform(-220, 220)
            d = nav_dist(x, y, 4500)
            if d is None or d < 700:
                continue
            if in_big(x, y, 300):
                continue
            if not legend_clear(x, y, 700, 500):
                continue
            roll = random.random()
            # ARBOL: sin arbol (existente o nuevo) a <9 m, lejos de edificios, leyendas holgadas
            if (len(new_t) < MAX_TREES and d > 1000 and roll < 0.42 and not in_big(x, y, 1500)
                    and legend_clear(x, y, 1200, 800)
                    and not near(trees_ex, x, y, 900) and not near([(t[0], t[1]) for t in new_t], x, y, 900)):
                z = ground_z(x, y)
                if z is not None:
                    mi = random.choices(range(len(TREES)), TREE_W)[0]
                    new_t.append((x, y, z, random.uniform(0, 360), random.uniform(0.85, 1.25), mi))
                    # 1-2 arbustos al pie del arbol
                    for _ in range(random.randint(1, 2)):
                        if len(new_b) >= MAX_BUSH: break
                        a2 = random.uniform(0, 6.283); r2 = random.uniform(220, 420)
                        bx, by = x + math.cos(a2) * r2, y + math.sin(a2) * r2
                        if legend_clear(bx, by, 700, 500) and (nav_dist(bx, by, 700) is None):
                            bz = ground_z(bx, by)
                            if bz is not None:
                                new_b.append((bx, by, bz, random.uniform(0, 360), random.uniform(0.8, 1.3), random.randrange(len(BUSHES))))
                    continue
            # ARBUSTO suelto
            if len(new_b) < MAX_BUSH and roll > 0.80 and not near(bush_ex, x, y, 350):
                z = ground_z(x, y)
                if z is not None:
                    new_b.append((x, y, z, random.uniform(0, 360), random.uniform(0.8, 1.3), random.randrange(len(BUSHES))))
                continue
            # CARDON (cactus del valle) cerca del sendero, raro
            if len(new_c) < MAX_CACT and 0.60 < roll < 0.64 and d < 1800:
                z = ground_z(x, y)
                if z is not None:
                    new_c.append((x, y, z, random.uniform(0, 360), random.uniform(0.8, 1.15), random.randrange(len(CACTUS))))

    res["counts"] = {"trees": len(new_t), "bushes": len(new_b), "cactus": len(new_c),
                     "existing_trees": len(trees_ex), "existing_bush": len(bush_ex)}

    if not DRY:
        actor = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.Actor, unreal.Vector(0, 0, 0))
        actor.set_actor_label("RELLENO_Campos")
        actor.tags = [unreal.Name("RELLENO")]
        sds = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
        root = sds.k2_gather_subobject_data_for_instance(actor)[0]
        made = []
        groups = [(TREES, new_t, 6000, 2), (BUSHES, new_b, 5500, 1), (CACTUS, new_c, 5500, 1)]
        for meshes, items, cull, minlod in groups:
            for mi, mpath in enumerate(meshes):
                sel = [it for it in items if it[5] == mi]
                if not sel:
                    continue
                params = unreal.AddNewSubobjectParams(parent_handle=root,
                    new_class=unreal.HierarchicalInstancedStaticMeshComponent, blueprint_context=None)
                h, fail = sds.add_new_subobject(params)
                comp = unreal.SubobjectDataBlueprintFunctionLibrary.get_object(
                    unreal.SubobjectDataBlueprintFunctionLibrary.get_data(h))
                comp.set_static_mesh(unreal.load_asset(mpath))
                comp.set_mobility(unreal.ComponentMobility.STATIC)
                comp.set_editor_property("cast_shadow", False)
                comp.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
                comp.set_editor_property("can_ever_affect_navigation", False)
                comp.set_editor_property("instance_start_cull_distance", int(cull * 0.8))
                comp.set_editor_property("instance_end_cull_distance", int(cull))
                comp.set_editor_property("override_min_lod", True)
                comp.set_editor_property("min_lod", minlod)
                xf = [unreal.Transform(unreal.Vector(x, y, z), unreal.Rotator(0, 0, yaw), unreal.Vector(s, s, s))
                      for (x, y, z, yaw, s, _) in sel]
                comp.add_instances(xf, False, True)
                made.append([mpath.split("/")[-1], comp.get_instance_count(), cull, minlod])
        res["made"] = made
        unreal.EditorLevelLibrary.save_current_level()
except Exception:
    res["err"] = traceback.format_exc()[:900]

open(OUT, "w").write(json.dumps(res, indent=1))

