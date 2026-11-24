# 398_ue_horizonte_arboles_foto.py
# Proyecto: Jatun Wasi Nawpa Kay (tesis VR Quest 2)
# Fecha: 2026-11-24
# Proposito: tapar la franja oscura vacia del horizonte con un segundo anillo de
#   "arboles-foto": mismos arboles StylescapeHD forzados a LOD3 (impostor = foto en
#   tarjetas, 9 vertices) -> costo casi nulo. Anillo 175-245 m alrededor del centro
#   del anillo HORIZ existente, escala grande, sin sombras/colision/culling.
#   Deja libre el sector hacia el Cristo. Actor propio "RELLENO_Horizonte" (tag RELLENO).
# Uso: DRY = True/False antes de exec().
import unreal, json, math, random, traceback
try:
    DRY
except NameError:
    DRY = True
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/horizonte_foto.json"
res = {"dry": DRY, "err": None}
MESHES = ["/Game/StylescapeHD/Foliage/Grassland/SM_Oak_03", "/Game/StylescapeHD/Foliage/Forest/SM_Maple_03",
          "/Game/StylescapeHD/Foliage/Forest/SM_Maple_04", "/Game/StylescapeHD/Foliage/Grassland/SM_Oak_04"]
CX, CY, Z = -723.0, 5308.0, -5.0
try:
    cristo = None
    for a in unreal.EditorLevelLibrary.get_all_level_actors():
        if "cristo" in a.get_actor_label().lower():
            L = a.get_actor_location(); cristo = (a.get_actor_label(), L.x, L.y)
            break
    res["cristo"] = cristo
    cristo_ang = math.degrees(math.atan2(cristo[2] - CY, cristo[1] - CX)) if cristo else None
    random.seed(398)
    items = []
    for row, (r0, r1) in enumerate([(17500, 21000), (21000, 24500)]):
        n = 420
        for i in range(n):
            ang = (360.0 / n) * (i + (0.5 if row else 0.0)) + random.uniform(-0.3, 0.3)
            if cristo_ang is not None and abs(((ang - cristo_ang) + 180) % 360 - 180) < 5:
                continue
            r = random.uniform(r0, r1)
            x = CX + math.cos(math.radians(ang)) * r; y = CY + math.sin(math.radians(ang)) * r
            items.append((x, y, random.uniform(0, 360), random.uniform(1.8, 2.8), random.randrange(len(MESHES))))
    res["count"] = len(items)
    if not DRY:
        actor = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.Actor, unreal.Vector(0, 0, 0))
        actor.set_actor_label("RELLENO_Horizonte")
        actor.tags = [unreal.Name("RELLENO")]
        sds = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
        root = sds.k2_gather_subobject_data_for_instance(actor)[0]
        made = []
        for mi, mpath in enumerate(MESHES):
            sel = [it for it in items if it[4] == mi]
            h, fail = sds.add_new_subobject(unreal.AddNewSubobjectParams(parent_handle=root,
                new_class=unreal.HierarchicalInstancedStaticMeshComponent, blueprint_context=None))
            comp = unreal.SubobjectDataBlueprintFunctionLibrary.get_object(unreal.SubobjectDataBlueprintFunctionLibrary.get_data(h))
            comp.set_static_mesh(unreal.load_asset(mpath))
            comp.set_mobility(unreal.ComponentMobility.STATIC)
            comp.set_editor_property("cast_shadow", False)
            comp.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
            comp.set_editor_property("can_ever_affect_navigation", False)
            comp.set_editor_property("instance_end_cull_distance", 0)
            comp.set_editor_property("override_min_lod", True)
            comp.set_editor_property("min_lod", 3)   # solo impostor (foto)
            comp.add_instances([unreal.Transform(unreal.Vector(x, y, Z), unreal.Rotator(0, 0, yaw), unreal.Vector(s, s, s))
                                for (x, y, yaw, s, _) in sel], False, True)
            made.append([mpath.split("/")[-1], comp.get_instance_count()])
        res["made"] = made
        unreal.EditorLevelLibrary.save_current_level()
except Exception:
    res["err"] = traceback.format_exc()[:800]
open(OUT, "w").write(json.dumps(res, indent=1))
